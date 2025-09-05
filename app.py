import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import json

# Import utility modules
from utils.keyword_gen import KeywordGenerator
from utils.trends import TrendAnalyzer
from utils.amazon import AmazonAnalyzer
from utils.analysis import KeywordAnalysis
from utils.export import ExportManager
from utils.nlp_tools import NLPTools

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///kdp_tool.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization
from models import ResearchSession, FavoriteKeyword

# Initialize utility classes
keyword_gen = KeywordGenerator()
trend_analyzer = TrendAnalyzer()
amazon_analyzer = AmazonAnalyzer()
keyword_analysis = KeywordAnalysis()
export_manager = ExportManager()
nlp_tools = NLPTools()

@app.route('/')
def index():
    """Main dashboard page"""
    # Get recent sessions
    recent_sessions = ResearchSession.query.order_by(ResearchSession.created_at.desc()).limit(5).all()
    
    # Get trending topics for the day
    trending_topics = []
    try:
        trending_topics = trend_analyzer.get_daily_trending_topics()[:10]
    except Exception as e:
        logging.error(f"Error fetching trending topics: {e}")
    
    return render_template('index.html', 
                         recent_sessions=recent_sessions,
                         trending_topics=trending_topics)

@app.route('/search', methods=['POST'])
def search_keywords():
    """Process keyword search and analysis"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        bulk_input = data.get('bulk_input', '')
        
        if bulk_input:
            keywords.extend([k.strip() for k in bulk_input.split('\n') if k.strip()])
        
        if not keywords:
            return jsonify({'error': 'No keywords provided'}), 400
        
        results = []
        
        for keyword in keywords:
            if not keyword.strip():
                continue
                
            # Generate expanded keywords
            expanded = keyword_gen.expand_keyword(keyword)
            
            # Get trends data
            trends_data = trend_analyzer.get_keyword_trends(keyword)
            
            # Get Amazon competition data
            amazon_data = amazon_analyzer.analyze_competition(keyword)
            
            # Calculate scores
            difficulty_score = keyword_analysis.calculate_difficulty_score(
                amazon_data.get('search_results_count', 0),
                trends_data.get('interest_over_time', [])
            )
            
            profitability_score = keyword_analysis.calculate_profitability_score(
                difficulty_score,
                trends_data.get('average_interest', 0),
                amazon_data.get('avg_price', 0)
            )
            
            result = {
                'keyword': keyword,
                'expanded_keywords': expanded,
                'trends': trends_data,
                'amazon': amazon_data,
                'difficulty_score': difficulty_score,
                'profitability_score': profitability_score,
                'score_color': keyword_analysis.get_score_color(profitability_score)
            }
            
            results.append(result)
        
        # Save session
        session_data = {
            'keywords': keywords,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        research_session = ResearchSession()
        research_session.name = f"Search {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        research_session.data = json.dumps(session_data)
        db.session.add(research_session)
        db.session.commit()
        
        # Store in flask session for current use
        session['current_results'] = results
        session['current_session_id'] = research_session.id
        
        return jsonify({
            'success': True,
            'results': results,
            'session_id': research_session.id
        })
        
    except Exception as e:
        logging.error(f"Error in search_keywords: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    """Manage favorite keywords"""
    if request.method == 'POST':
        data = request.get_json()
        keyword = data.get('keyword')
        action = data.get('action', 'add')
        
        if action == 'add':
            existing = FavoriteKeyword.query.filter_by(keyword=keyword).first()
            if not existing:
                favorite = FavoriteKeyword()
                favorite.keyword = keyword
                db.session.add(favorite)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Added to favorites'})
            else:
                return jsonify({'success': False, 'message': 'Already in favorites'})
        
        elif action == 'remove':
            favorite = FavoriteKeyword.query.filter_by(keyword=keyword).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Removed from favorites'})
            else:
                return jsonify({'success': False, 'message': 'Not found in favorites'})
    
    # GET request - show favorites page
    favorites_list = FavoriteKeyword.query.order_by(FavoriteKeyword.created_at.desc()).all()
    return render_template('favorites.html', favorites=favorites_list)

@app.route('/sessions')
def sessions():
    """List all research sessions"""
    sessions_list = ResearchSession.query.order_by(ResearchSession.created_at.desc()).all()
    return render_template('sessions.html', sessions=sessions_list)

@app.route('/session/<int:session_id>')
def load_session(session_id):
    """Load a specific research session"""
    research_session = ResearchSession.query.get_or_404(session_id)
    session_data = json.loads(research_session.data)
    
    session['current_results'] = session_data.get('results', [])
    session['current_session_id'] = session_id
    
    flash(f'Loaded session: {research_session.name}', 'success')
    return redirect(url_for('index'))

@app.route('/export/<format>')
def export_data(format):
    """Export current results in specified format"""
    try:
        results = session.get('current_results', [])
        if not results:
            flash('No data to export. Please run a search first.', 'warning')
            return redirect(url_for('index'))
        
        if format == 'csv':
            file_path = export_manager.export_to_csv(results)
            return send_file(file_path, as_attachment=True, download_name='kdp_keywords.csv')
        
        elif format == 'excel':
            file_path = export_manager.export_to_excel(results)
            return send_file(file_path, as_attachment=True, download_name='kdp_keywords.xlsx')
        
        elif format == 'pdf':
            file_path = export_manager.export_to_pdf(results)
            return send_file(file_path, as_attachment=True, download_name='kdp_keywords_report.pdf')
        
        else:
            flash('Invalid export format', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Export error: {e}")
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/trending')
def trending():
    """Get current trending topics"""
    try:
        topics = trend_analyzer.get_daily_trending_topics()
        return jsonify({'trends': topics})
    except Exception as e:
        logging.error(f"Error fetching trends: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cluster')
def cluster_keywords():
    """Cluster current keywords"""
    try:
        results = session.get('current_results', [])
        if not results:
            return jsonify({'error': 'No keywords to cluster'}), 400
        
        keywords = [r['keyword'] for r in results]
        clusters = keyword_analysis.cluster_keywords(keywords)
        
        return jsonify({'clusters': clusters})
    except Exception as e:
        logging.error(f"Clustering error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
