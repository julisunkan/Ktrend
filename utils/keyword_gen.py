import requests
import urllib.parse
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict

class KeywordGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def expand_keyword(self, keyword: str) -> List[str]:
        """Expand a keyword using multiple sources"""
        expanded = set()
        
        try:
            # Google Autocomplete
            google_suggestions = self.get_google_autocomplete(keyword)
            expanded.update(google_suggestions)
            
            # DuckDuckGo suggestions
            ddg_suggestions = self.get_duckduckgo_suggestions(keyword)
            expanded.update(ddg_suggestions)
            
            # Wikipedia titles
            wiki_suggestions = self.get_wikipedia_suggestions(keyword)
            expanded.update(wiki_suggestions)
            
        except Exception as e:
            logging.error(f"Error expanding keyword '{keyword}': {e}")
        
        return list(expanded)[:20]  # Limit to 20 suggestions
    
    def get_google_autocomplete(self, keyword: str) -> List[str]:
        """Get Google autocomplete suggestions"""
        suggestions = []
        try:
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={urllib.parse.quote(keyword)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    suggestions = [s for s in data[1] if s and s.lower() != keyword.lower()]
                    
        except Exception as e:
            logging.warning(f"Google autocomplete failed for '{keyword}': {e}")
        
        return suggestions[:10]
    
    def get_duckduckgo_suggestions(self, keyword: str) -> List[str]:
        """Get DuckDuckGo search suggestions"""
        suggestions = []
        try:
            url = f"https://duckduckgo.com/ac/?q={urllib.parse.quote(keyword)}&type=list"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    suggestions = [item['phrase'] for item in data[1] if 'phrase' in item]
                    
        except Exception as e:
            logging.warning(f"DuckDuckGo suggestions failed for '{keyword}': {e}")
        
        return suggestions[:10]
    
    def get_wikipedia_suggestions(self, keyword: str) -> List[str]:
        """Get Wikipedia page title suggestions"""
        suggestions = []
        try:
            url = f"https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'opensearch',
                'search': keyword,
                'limit': 10,
                'namespace': 0,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    suggestions = data[1]  # Title suggestions
                    
        except Exception as e:
            logging.warning(f"Wikipedia suggestions failed for '{keyword}': {e}")
        
        return suggestions[:8]
    
    def bulk_expand_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Expand multiple keywords in bulk"""
        results = {}
        
        for keyword in keywords:
            if keyword.strip():
                results[keyword] = self.expand_keyword(keyword.strip())
                time.sleep(0.5)  # Rate limiting
        
        return results
    
    def generate_long_tail_variations(self, keyword: str) -> List[str]:
        """Generate long-tail keyword variations"""
        variations = []
        
        # Common prefixes and suffixes for books
        prefixes = ['how to', 'best', 'complete guide to', 'beginner', 'advanced', 'ultimate']
        suffixes = ['book', 'guide', 'handbook', 'manual', 'course', 'tutorial', 'for beginners', 'step by step']
        
        for prefix in prefixes:
            variations.append(f"{prefix} {keyword}")
        
        for suffix in suffixes:
            variations.append(f"{keyword} {suffix}")
        
        # Combine prefix and suffix
        for prefix in prefixes[:3]:
            for suffix in suffixes[:3]:
                variations.append(f"{prefix} {keyword} {suffix}")
        
        return variations[:15]
