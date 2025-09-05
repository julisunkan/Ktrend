import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from typing import List, Dict, Tuple
import re

class KeywordAnalysis:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_difficulty_score(self, search_results_count: int, interest_data: List[int]) -> float:
        """Calculate keyword difficulty score (0-100)"""
        try:
            # Normalize search results count (logarithmic scale)
            if search_results_count <= 0:
                competition_score = 0
            elif search_results_count < 1000:
                competition_score = 10
            elif search_results_count < 10000:
                competition_score = 30
            elif search_results_count < 50000:
                competition_score = 60
            elif search_results_count < 100000:
                competition_score = 80
            else:
                competition_score = 100
            
            # Factor in search volume/interest
            if interest_data:
                avg_interest = np.mean(interest_data)
                # Higher interest slightly increases difficulty
                interest_factor = min(avg_interest / 100 * 20, 20)
            else:
                interest_factor = 0
            
            difficulty = min(competition_score + interest_factor, 100)
            return round(difficulty, 2)
            
        except Exception as e:
            logging.error(f"Error calculating difficulty score: {e}")
            return 50.0  # Default medium difficulty
    
    def calculate_profitability_score(self, difficulty_score: float, avg_interest: float, avg_price: float) -> float:
        """Calculate profitability score (0-100)"""
        try:
            # Lower difficulty is better for profitability
            difficulty_factor = 100 - difficulty_score
            
            # Higher interest is better
            interest_factor = min(avg_interest, 100)
            
            # Price factor (sweet spot around $10-30)
            if avg_price == 0:
                price_factor = 50  # Unknown price gets neutral score
            elif 10 <= avg_price <= 30:
                price_factor = 100  # Optimal price range
            elif 5 <= avg_price < 10:
                price_factor = 80   # Decent low price
            elif 30 < avg_price <= 50:
                price_factor = 70   # Higher price, still good
            elif avg_price < 5:
                price_factor = 40   # Too low
            else:
                price_factor = 30   # Too high
            
            # Weighted average
            profitability = (
                difficulty_factor * 0.4 +
                interest_factor * 0.4 +
                price_factor * 0.2
            )
            
            return round(profitability, 2)
            
        except Exception as e:
            logging.error(f"Error calculating profitability score: {e}")
            return 50.0  # Default medium profitability
    
    def get_score_color(self, score: float) -> str:
        """Get color code for score visualization"""
        if score >= 80:
            return 'success'  # Green - high potential
        elif score >= 60:
            return 'warning'  # Yellow - medium potential
        elif score >= 40:
            return 'info'     # Blue - low-medium potential
        else:
            return 'danger'   # Red - low potential
    
    def cluster_keywords(self, keywords: List[str], n_clusters: int = None) -> Dict:
        """Cluster keywords using K-means based on semantic similarity"""
        try:
            if len(keywords) < 2:
                return {'clusters': [{'cluster_id': 0, 'keywords': keywords, 'theme': 'Single keyword'}]}
            
            # Determine optimal number of clusters
            if n_clusters is None:
                n_clusters = min(max(2, len(keywords) // 3), 8)
            n_clusters = max(1, n_clusters)  # Ensure at least 1 cluster
            
            # Vectorize keywords
            tfidf_matrix = self.vectorizer.fit_transform(keywords)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Group keywords by cluster
            clusters = {}
            for i, keyword in enumerate(keywords):
                cluster_id = cluster_labels[i]
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(keyword)
            
            # Generate cluster themes
            cluster_results = []
            feature_names = self.vectorizer.get_feature_names_out()
            
            for cluster_id, cluster_keywords in clusters.items():
                # Get centroid
                cluster_center = kmeans.cluster_centers_[cluster_id]
                
                # Get top terms for this cluster
                top_indices = cluster_center.argsort()[-3:][::-1]
                top_terms = [str(feature_names[i]) for i in top_indices]
                theme = ' + '.join(top_terms)
                
                cluster_results.append({
                    'cluster_id': int(cluster_id),
                    'keywords': cluster_keywords,
                    'theme': theme,
                    'size': len(cluster_keywords)
                })
            
            # Sort by cluster size
            cluster_results.sort(key=lambda x: x['size'], reverse=True)
            
            return {'clusters': cluster_results}
            
        except Exception as e:
            logging.error(f"Error clustering keywords: {e}")
            return {'clusters': [{'cluster_id': 0, 'keywords': keywords, 'theme': 'Unclustered'}]}
    
    def calculate_keyword_similarity(self, keyword1: str, keyword2: str) -> float:
        """Calculate semantic similarity between two keywords"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([keyword1, keyword2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity, 3)
        except Exception as e:
            logging.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def analyze_keyword_patterns(self, keywords: List[str]) -> Dict:
        """Analyze patterns in keyword list"""
        patterns = {
            'average_length': 0,
            'long_tail_percentage': 0,
            'question_keywords': [],
            'action_keywords': [],
            'common_words': {},
            'word_count_distribution': {}
        }
        
        try:
            if not keywords:
                return patterns
            
            # Calculate average length
            lengths = [len(keyword.split()) for keyword in keywords]
            patterns['average_length'] = round(np.mean(lengths), 2)
            
            # Long-tail percentage (3+ words)
            long_tail_count = sum(1 for length in lengths if length >= 3)
            patterns['long_tail_percentage'] = round((long_tail_count / len(keywords)) * 100, 2)
            
            # Word count distribution
            word_counts = {}
            for length in lengths:
                word_counts[length] = word_counts.get(length, 0) + 1
            patterns['word_count_distribution'] = word_counts
            
            # Identify question keywords
            question_words = ['how', 'what', 'why', 'when', 'where', 'who', 'which']
            patterns['question_keywords'] = [
                kw for kw in keywords 
                if any(kw.lower().startswith(qw) for qw in question_words)
            ]
            
            # Identify action keywords
            action_words = ['buy', 'get', 'find', 'learn', 'make', 'create', 'build', 'start']
            patterns['action_keywords'] = [
                kw for kw in keywords 
                if any(word in kw.lower() for word in action_words)
            ]
            
            # Common words analysis
            all_words = []
            for keyword in keywords:
                words = re.findall(r'\b\w+\b', keyword.lower())
                all_words.extend(words)
            
            word_freq = {}
            for word in all_words:
                if len(word) > 2:  # Ignore very short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top 10 most common words
            patterns['common_words'] = dict(
                sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
        except Exception as e:
            logging.error(f"Error analyzing keyword patterns: {e}")
        
        return patterns
    
    def recommend_keyword_strategy(self, analysis_results: List[Dict]) -> Dict:
        """Recommend keyword strategy based on analysis results"""
        recommendations = {
            'high_potential_keywords': [],
            'avoid_keywords': [],
            'long_tail_opportunities': [],
            'niche_opportunities': [],
            'strategy_tips': []
        }
        
        try:
            for result in analysis_results:
                keyword = result.get('keyword', '')
                profitability = result.get('profitability_score', 0)
                difficulty = result.get('difficulty_score', 0)
                search_results = result.get('amazon', {}).get('search_results_count', 0)
                
                # High potential keywords
                if profitability >= 70 and difficulty <= 60:
                    recommendations['high_potential_keywords'].append({
                        'keyword': keyword,
                        'profitability': profitability,
                        'difficulty': difficulty
                    })
                
                # Avoid high competition keywords
                elif difficulty >= 80:
                    recommendations['avoid_keywords'].append({
                        'keyword': keyword,
                        'reason': 'Too competitive',
                        'difficulty': difficulty
                    })
                
                # Long-tail opportunities
                elif len(keyword.split()) >= 3 and difficulty <= 50:
                    recommendations['long_tail_opportunities'].append({
                        'keyword': keyword,
                        'word_count': len(keyword.split()),
                        'difficulty': difficulty
                    })
                
                # Niche opportunities (low competition)
                elif search_results < 1000 and profitability >= 40:
                    recommendations['niche_opportunities'].append({
                        'keyword': keyword,
                        'search_results': search_results,
                        'profitability': profitability
                    })
            
            # Generate strategy tips
            if recommendations['high_potential_keywords']:
                recommendations['strategy_tips'].append(
                    f"Focus on {len(recommendations['high_potential_keywords'])} high-potential keywords identified"
                )
            
            if recommendations['long_tail_opportunities']:
                recommendations['strategy_tips'].append(
                    f"Consider {len(recommendations['long_tail_opportunities'])} long-tail keywords for specific niches"
                )
            
            if len(recommendations['avoid_keywords']) > len(analysis_results) * 0.5:
                recommendations['strategy_tips'].append(
                    "Many keywords are highly competitive - consider more specific, long-tail variations"
                )
            
            if recommendations['niche_opportunities']:
                recommendations['strategy_tips'].append(
                    f"Explore {len(recommendations['niche_opportunities'])} niche opportunities with low competition"
                )
                
        except Exception as e:
            logging.error(f"Error generating keyword strategy recommendations: {e}")
        
        return recommendations
