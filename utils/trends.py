import requests
import urllib.parse
from pytrends.request import TrendReq
import pandas as pd
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
import time
import feedparser

class TrendAnalyzer:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_keyword_trends(self, keyword: str) -> Dict:
        """Get Google Trends data for a keyword"""
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='US', gprop='')
            
            # Interest over time
            interest_over_time = self.pytrends.interest_over_time()
            
            # Related queries
            related_queries = self.pytrends.related_queries()
            
            # Regional interest
            regional_interest = self.pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
            
            trends_data = {
                'interest_over_time': interest_over_time[keyword].tolist() if not interest_over_time.empty else [],
                'average_interest': float(interest_over_time[keyword].mean()) if not interest_over_time.empty else 0,
                'related_queries': {
                    'top': related_queries[keyword]['top']['query'].tolist() if related_queries[keyword]['top'] is not None else [],
                    'rising': related_queries[keyword]['rising']['query'].tolist() if related_queries[keyword]['rising'] is not None else []
                },
                'regional_interest': regional_interest[keyword].to_dict() if not regional_interest.empty else {}
            }
            
            return trends_data
            
        except Exception as e:
            logging.error(f"Error getting trends for '{keyword}': {e}")
            return {
                'interest_over_time': [],
                'average_interest': 0,
                'related_queries': {'top': [], 'rising': []},
                'regional_interest': {}
            }
    
    def get_daily_trending_topics(self) -> List[str]:
        """Get daily trending topics from multiple sources"""
        trending_topics = []
        
        # Google Trends daily trends
        try:
            daily_trends = self.pytrends.trending_searches(pn='united_states')
            if not daily_trends.empty:
                trending_topics.extend(daily_trends[0].tolist()[:10])
        except Exception as e:
            logging.warning(f"Error getting Google daily trends: {e}")
        
        # YouTube trending (scraping)
        youtube_trends = self.get_youtube_trending()
        trending_topics.extend(youtube_trends)
        
        # Twitter trends (RSS)
        twitter_trends = self.get_twitter_trends_rss()
        trending_topics.extend(twitter_trends)
        
        # Remove duplicates and limit
        return list(dict.fromkeys(trending_topics))[:20]
    
    def get_youtube_trending(self) -> List[str]:
        """Scrape YouTube trending video titles"""
        trending_titles = []
        try:
            url = "https://www.youtube.com/feed/trending"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for video titles in trending page
                title_elements = soup.find_all('a', {'id': 'video-title'})
                for element in title_elements[:10]:
                    title = element.get('title') or ''
                    if title and hasattr(title, 'strip'):
                        title = title.strip()
                        if title:
                            trending_titles.append(title)
                        
        except Exception as e:
            logging.warning(f"Error scraping YouTube trending: {e}")
        
        return trending_titles
    
    def get_twitter_trends_rss(self) -> List[str]:
        """Get Twitter trending topics via RSS feeds"""
        trends = []
        try:
            # Use Twitter's RSS feeds or alternative sources
            rss_urls = [
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.bbci.co.uk/news/rss.xml'
            ]
            
            for url in rss_urls:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:5]:
                        title = entry.title.strip()
                        if title:
                            trends.append(title)
                except Exception as e:
                    logging.warning(f"Error parsing RSS feed {url}: {e}")
                    
        except Exception as e:
            logging.warning(f"Error getting Twitter trends: {e}")
        
        return trends[:10]
    
    def get_quora_questions(self, topic: str) -> List[str]:
        """Scrape popular questions from Quora for a topic"""
        questions = []
        try:
            url = f"https://www.quora.com/search?q={urllib.parse.quote(topic)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for question links
                question_links = soup.find_all('a', href=True)
                for link in question_links[:10]:
                    href = link.get('href') or ''
                    if isinstance(href, str) and ('/unanswered/' in href or 'What-' in href or 'How-' in href):
                        question_text = link.get_text().strip()
                        if question_text and len(question_text) > 10:
                            questions.append(question_text)
                            
        except Exception as e:
            logging.warning(f"Error scraping Quora questions for '{topic}': {e}")
        
        return questions[:8]
    
    def get_stackexchange_questions(self, topic: str) -> List[str]:
        """Get popular questions from Stack Exchange sites"""
        questions = []
        try:
            # Use Stack Exchange API
            url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=votes&intitle={urllib.parse.quote(topic)}&site=stackoverflow"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', [])[:8]:
                    title = item.get('title', '').strip()
                    if title:
                        questions.append(title)
                        
        except Exception as e:
            logging.warning(f"Error getting StackExchange questions for '{topic}': {e}")
        
        return questions
    
    def analyze_seasonal_trends(self, keyword: str) -> Dict:
        """Analyze seasonal trends for a keyword"""
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 5-y', geo='US', gprop='')
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                # Group by month to identify seasonal patterns
                interest_over_time['month'] = interest_over_time.index.month
                monthly_avg = interest_over_time.groupby('month')[keyword].mean()
                
                return {
                    'monthly_averages': monthly_avg.to_dict(),
                    'peak_months': monthly_avg.nlargest(3).index.tolist(),
                    'low_months': monthly_avg.nsmallest(3).index.tolist()
                }
        except Exception as e:
            logging.error(f"Error analyzing seasonal trends for '{keyword}': {e}")
        
        return {'monthly_averages': {}, 'peak_months': [], 'low_months': []}
