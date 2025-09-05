import csv
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
import os
import tempfile
from datetime import datetime
import logging
from typing import List, Dict

class ExportManager:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.styles = getSampleStyleSheet()
    
    def export_to_csv(self, results: List[Dict]) -> str:
        """Export results to CSV file"""
        try:
            filename = f"kdp_keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(self.temp_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if not results:
                    csvfile.write("No data to export\n")
                    return filepath
                
                fieldnames = [
                    'keyword',
                    'difficulty_score',
                    'profitability_score',
                    'search_results_count',
                    'avg_price',
                    'avg_reviews',
                    'competition_level',
                    'average_interest',
                    'related_queries_top',
                    'categories'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    amazon_data = result.get('amazon', {})
                    trends_data = result.get('trends', {})
                    related_queries = trends_data.get('related_queries', {})
                    
                    row = {
                        'keyword': result.get('keyword', ''),
                        'difficulty_score': result.get('difficulty_score', 0),
                        'profitability_score': result.get('profitability_score', 0),
                        'search_results_count': amazon_data.get('search_results_count', 0),
                        'avg_price': amazon_data.get('avg_price', 0),
                        'avg_reviews': amazon_data.get('avg_reviews', 0),
                        'competition_level': amazon_data.get('competition_level', ''),
                        'average_interest': trends_data.get('average_interest', 0),
                        'related_queries_top': ', '.join(related_queries.get('top', [])[:5]),
                        'categories': ', '.join(amazon_data.get('categories', []))
                    }
                    writer.writerow(row)
            
            return filepath
            
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            raise
    
    def export_to_excel(self, results: List[Dict]) -> str:
        """Export results to Excel file with multiple sheets"""
        try:
            filename = f"kdp_keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(self.temp_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main results sheet
                main_data = []
                for result in results:
                    amazon_data = result.get('amazon', {})
                    trends_data = result.get('trends', {})
                    
                    row = {
                        'Keyword': result.get('keyword', ''),
                        'Difficulty Score': result.get('difficulty_score', 0),
                        'Profitability Score': result.get('profitability_score', 0),
                        'Search Results Count': amazon_data.get('search_results_count', 0),
                        'Average Price': amazon_data.get('avg_price', 0),
                        'Average Reviews': amazon_data.get('avg_reviews', 0),
                        'Competition Level': amazon_data.get('competition_level', ''),
                        'Average Interest': trends_data.get('average_interest', 0),
                        'Categories': ', '.join(amazon_data.get('categories', []))
                    }
                    main_data.append(row)
                
                df_main = pd.DataFrame(main_data)
                df_main.to_excel(writer, sheet_name='Keyword Analysis', index=False)
                
                # Top books sheet
                books_data = []
                for result in results:
                    keyword = result.get('keyword', '')
                    amazon_data = result.get('amazon', {})
                    for book in amazon_data.get('top_books', [])[:5]:  # Top 5 books per keyword
                        book_row = {
                            'Keyword': keyword,
                            'Book Title': book.get('title', ''),
                            'Price': book.get('price', 0),
                            'Reviews Count': book.get('reviews_count', 0),
                            'Rating': book.get('rating', 0),
                            'Format': book.get('format', '')
                        }
                        books_data.append(book_row)
                
                if books_data:
                    df_books = pd.DataFrame(books_data)
                    df_books.to_excel(writer, sheet_name='Top Competing Books', index=False)
                
                # Related queries sheet
                queries_data = []
                for result in results:
                    keyword = result.get('keyword', '')
                    trends_data = result.get('trends', {})
                    related_queries = trends_data.get('related_queries', {})
                    
                    for query in related_queries.get('top', [])[:10]:
                        queries_data.append({
                            'Original Keyword': keyword,
                            'Related Query': query,
                            'Type': 'Top'
                        })
                    
                    for query in related_queries.get('rising', [])[:10]:
                        queries_data.append({
                            'Original Keyword': keyword,
                            'Related Query': query,
                            'Type': 'Rising'
                        })
                
                if queries_data:
                    df_queries = pd.DataFrame(queries_data)
                    df_queries.to_excel(writer, sheet_name='Related Queries', index=False)
            
            return filepath
            
        except Exception as e:
            logging.error(f"Error exporting to Excel: {e}")
            raise
    
    def export_to_pdf(self, results: List[Dict]) -> str:
        """Export results to PDF report"""
        try:
            filename = f"kdp_keywords_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.temp_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph("KDP Keyword Research Report", title_style))
            story.append(Spacer(1, 20))
            
            # Report metadata
            report_info = f"""
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Total Keywords Analyzed:</b> {len(results)}<br/>
            <b>Report Type:</b> Comprehensive Keyword Analysis
            """
            story.append(Paragraph(report_info, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Summary statistics
            if results:
                avg_difficulty = sum(r.get('difficulty_score', 0) for r in results) / len(results)
                avg_profitability = sum(r.get('profitability_score', 0) for r in results) / len(results)
                high_potential = len([r for r in results if r.get('profitability_score', 0) >= 70])
                
                summary = f"""
                <b>Summary Statistics:</b><br/>
                • Average Difficulty Score: {avg_difficulty:.1f}/100<br/>
                • Average Profitability Score: {avg_profitability:.1f}/100<br/>
                • High Potential Keywords: {high_potential}<br/>
                • Recommended Focus: {self.get_strategy_recommendation(results)}
                """
                story.append(Paragraph(summary, self.styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Detailed results table
            story.append(Paragraph("Detailed Keyword Analysis", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Create table data
            table_data = [['Keyword', 'Difficulty', 'Profitability', 'Competition', 'Avg Price']]
            
            for result in results[:20]:  # Limit to first 20 for PDF
                amazon_data = result.get('amazon', {})
                row = [
                    result.get('keyword', '')[:30],  # Truncate long keywords
                    f"{result.get('difficulty_score', 0):.1f}",
                    f"{result.get('profitability_score', 0):.1f}",
                    amazon_data.get('competition_level', 'Unknown'),
                    f"${amazon_data.get('avg_price', 0):.2f}"
                ]
                table_data.append(row)
            
            # Create and style table
            table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Top opportunities section
            high_potential_keywords = [
                r for r in results 
                if r.get('profitability_score', 0) >= 70 and r.get('difficulty_score', 0) <= 60
            ]
            
            if high_potential_keywords:
                story.append(Paragraph("Top Opportunities", self.styles['Heading2']))
                story.append(Spacer(1, 12))
                
                for keyword_data in high_potential_keywords[:5]:
                    opportunity_text = f"""
                    <b>{keyword_data.get('keyword', '')}</b><br/>
                    Profitability: {keyword_data.get('profitability_score', 0):.1f}/100 | 
                    Difficulty: {keyword_data.get('difficulty_score', 0):.1f}/100<br/>
                    Competition: {keyword_data.get('amazon', {}).get('competition_level', 'Unknown')}
                    """
                    story.append(Paragraph(opportunity_text, self.styles['Normal']))
                    story.append(Spacer(1, 8))
            
            # Recommendations section
            story.append(Paragraph("Recommendations", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            recommendations = self.generate_recommendations(results)
            story.append(Paragraph(recommendations, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            return filepath
            
        except Exception as e:
            logging.error(f"Error exporting to PDF: {e}")
            raise
    
    def get_strategy_recommendation(self, results: List[Dict]) -> str:
        """Generate strategy recommendation based on results"""
        if not results:
            return "No data available"
        
        high_potential = len([r for r in results if r.get('profitability_score', 0) >= 70])
        high_competition = len([r for r in results if r.get('difficulty_score', 0) >= 80])
        
        if high_potential > len(results) * 0.3:
            return "Strong opportunities identified - focus on high-potential keywords"
        elif high_competition > len(results) * 0.5:
            return "High competition market - consider long-tail variations"
        else:
            return "Mixed opportunities - diversify keyword strategy"
    
    def generate_recommendations(self, results: List[Dict]) -> str:
        """Generate detailed recommendations text"""
        if not results:
            return "No recommendations available - please analyze some keywords first."
        
        recommendations = []
        
        # Analyze difficulty distribution
        avg_difficulty = sum(r.get('difficulty_score', 0) for r in results) / len(results)
        if avg_difficulty > 70:
            recommendations.append("• Consider targeting more specific, long-tail keyword variations to reduce competition.")
        
        # Analyze profitability
        high_profit_count = len([r for r in results if r.get('profitability_score', 0) >= 70])
        if high_profit_count > 0:
            recommendations.append(f"• Focus your content creation on the {high_profit_count} high-profitability keywords identified.")
        
        # Price analysis
        avg_prices = [r.get('amazon', {}).get('avg_price', 0) for r in results if r.get('amazon', {}).get('avg_price', 0) > 0]
        if avg_prices:
            avg_price = sum(avg_prices) / len(avg_prices)
            if avg_price < 10:
                recommendations.append("• Consider premium pricing strategies as the market shows low average prices.")
            elif avg_price > 30:
                recommendations.append("• Market shows high price tolerance - consider comprehensive, high-value content.")
        
        # Competition analysis
        low_comp_keywords = [r for r in results if r.get('amazon', {}).get('search_results_count', 0) < 1000]
        if low_comp_keywords:
            recommendations.append(f"• {len(low_comp_keywords)} keywords show low competition - prioritize these for quick market entry.")
        
        # Trending opportunities
        high_interest = [r for r in results if r.get('trends', {}).get('average_interest', 0) > 50]
        if high_interest:
            recommendations.append(f"• {len(high_interest)} keywords show strong search interest - time-sensitive opportunities.")
        
        if not recommendations:
            recommendations.append("• Continue researching to find more targeted keyword opportunities.")
            recommendations.append("• Consider expanding your keyword list with more specific, niche terms.")
        
        return "<br/>".join(recommendations)
