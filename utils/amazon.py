import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List
import time
import urllib.parse

class AmazonAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        })
    
    def analyze_competition(self, keyword: str) -> Dict:
        """Analyze Amazon competition for a keyword"""
        try:
            search_results = self.search_amazon_books(keyword)
            
            analysis = {
                'search_results_count': search_results.get('total_results', 0),
                'top_books': search_results.get('books', [])[:10],
                'avg_price': self.calculate_average_price(search_results.get('books', [])),
                'avg_reviews': self.calculate_average_reviews(search_results.get('books', [])),
                'categories': self.extract_categories(search_results.get('books', [])),
                'competition_level': self.assess_competition_level(search_results.get('total_results', 0))
            }
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing Amazon competition for '{keyword}': {e}")
            return {
                'search_results_count': 0,
                'top_books': [],
                'avg_price': 0,
                'avg_reviews': 0,
                'categories': [],
                'competition_level': 'Unknown'
            }
    
    def search_amazon_books(self, keyword: str) -> Dict:
        """Search Amazon for books with the given keyword"""
        try:
            # Amazon search URL for books
            search_url = f"https://www.amazon.com/s?k={urllib.parse.quote(keyword)}&i=stripbooks&ref=sr_pg_1"
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract total results count
                total_results = self.extract_results_count(soup)
                
                # Extract book information
                books = self.extract_book_details(soup)
                
                return {
                    'total_results': total_results,
                    'books': books
                }
            else:
                logging.warning(f"Amazon search failed with status code: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error searching Amazon for '{keyword}': {e}")
        
        return {'total_results': 0, 'books': []}
    
    def extract_results_count(self, soup: BeautifulSoup) -> int:
        """Extract the total number of search results"""
        try:
            # Look for results count in various possible locations
            result_selectors = [
                'span[data-component-type="s-result-info-bar"] span',
                '.a-section .a-size-base',
                '.s-result-info-bar span'
            ]
            
            for selector in result_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Look for patterns like "1-16 of over 50,000 results"
                    match = re.search(r'of\s+(?:over\s+)?([0-9,]+)\s+results', text, re.IGNORECASE)
                    if match:
                        count_str = match.group(1).replace(',', '')
                        return int(count_str)
                    
                    # Look for patterns like "50,000 results"
                    match = re.search(r'([0-9,]+)\s+results', text, re.IGNORECASE)
                    if match:
                        count_str = match.group(1).replace(',', '')
                        return int(count_str)
                        
        except Exception as e:
            logging.error(f"Error extracting results count: {e}")
        
        return 0
    
    def extract_book_details(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract details of books from search results"""
        books = []
        
        try:
            # Find all product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:20]:  # Limit to first 20 results
                book = {}
                
                try:
                    # Title
                    title_element = container.find('h2', class_='a-size-mini') or container.find('span', class_='a-size-medium')
                    if title_element:
                        title_link = title_element.find('a')
                        if title_link:
                            book['title'] = title_link.get_text().strip()
                            book['url'] = 'https://www.amazon.com' + title_link.get('href', '')
                    
                    # Price
                    price_element = container.find('span', class_='a-price-whole') or container.find('span', class_='a-offscreen')
                    if price_element:
                        price_text = price_element.get_text().strip()
                        price_match = re.search(r'[\d.]+', price_text)
                        if price_match:
                            book['price'] = float(price_match.group())
                    
                    # Reviews count
                    reviews_element = container.find('a', class_='a-link-normal')
                    if reviews_element:
                        reviews_text = reviews_element.get_text().strip()
                        reviews_match = re.search(r'([0-9,]+)', reviews_text)
                        if reviews_match:
                            book['reviews_count'] = int(reviews_match.group(1).replace(',', ''))
                    
                    # Rating
                    rating_element = container.find('span', class_='a-icon-alt')
                    if rating_element:
                        rating_text = rating_element.get_text().strip()
                        rating_match = re.search(r'([\d.]+)', rating_text)
                        if rating_match:
                            book['rating'] = float(rating_match.group(1))
                    
                    # Format (Kindle, Paperback, etc.)
                    format_element = container.find('span', class_='a-size-base-plus')
                    if format_element:
                        book['format'] = format_element.get_text().strip()
                    
                    if book.get('title'):  # Only add if we have at least a title
                        books.append(book)
                        
                except Exception as e:
                    logging.warning(f"Error extracting book details: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error extracting book details: {e}")
        
        return books
    
    def calculate_average_price(self, books: List[Dict]) -> float:
        """Calculate average price of books"""
        prices = [book.get('price', 0) for book in books if book.get('price', 0) > 0]
        return sum(prices) / len(prices) if prices else 0
    
    def calculate_average_reviews(self, books: List[Dict]) -> float:
        """Calculate average number of reviews"""
        reviews = [book.get('reviews_count', 0) for book in books if book.get('reviews_count', 0) > 0]
        return sum(reviews) / len(reviews) if reviews else 0
    
    def extract_categories(self, books: List[Dict]) -> List[str]:
        """Extract common categories from book data"""
        # This would typically involve more detailed page scraping
        # For now, return common book categories based on titles
        categories = []
        
        for book in books[:5]:
            title = book.get('title', '').lower()
            
            if any(word in title for word in ['cookbook', 'recipe', 'cooking']):
                categories.append('Cooking & Food')
            elif any(word in title for word in ['romance', 'love']):
                categories.append('Romance')
            elif any(word in title for word in ['mystery', 'thriller', 'crime']):
                categories.append('Mystery & Thriller')
            elif any(word in title for word in ['business', 'entrepreneur', 'success']):
                categories.append('Business')
            elif any(word in title for word in ['health', 'fitness', 'diet']):
                categories.append('Health & Fitness')
            elif any(word in title for word in ['children', 'kids']):
                categories.append('Children\'s Books')
        
        return list(set(categories))
    
    def assess_competition_level(self, results_count: int) -> str:
        """Assess competition level based on results count"""
        if results_count == 0:
            return 'No competition'
        elif results_count < 1000:
            return 'Low competition'
        elif results_count < 10000:
            return 'Medium competition'
        elif results_count < 50000:
            return 'High competition'
        else:
            return 'Very high competition'
    
    def get_bestseller_data(self, category: str) -> List[Dict]:
        """Get bestseller data for a specific category"""
        bestsellers = []
        
        try:
            # Amazon bestsellers URL (simplified)
            url = f"https://www.amazon.com/gp/bestsellers/books/{category}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract bestseller information (simplified)
                bestseller_elements = soup.find_all('div', class_='a-section')[:10]
                
                for element in bestseller_elements:
                    bestseller = {}
                    
                    title_element = element.find('div', class_='p13n-sc-truncate')
                    if title_element:
                        bestseller['title'] = title_element.get_text().strip()
                    
                    # Add more bestseller data extraction as needed
                    if bestseller.get('title'):
                        bestsellers.append(bestseller)
                        
        except Exception as e:
            logging.error(f"Error getting bestseller data for category '{category}': {e}")
        
        return bestsellers
