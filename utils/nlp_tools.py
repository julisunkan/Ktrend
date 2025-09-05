import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from nltk.corpus import stopwords
import string
import logging
from typing import List, Dict, Set
import re
from collections import Counter

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class NLPTools:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = set(string.punctuation)
    
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word using WordNet"""
        synonyms = set()
        
        try:
            synsets = wordnet.synsets(word)
            for syn in synsets:
                lemmas = syn.lemmas()
                for lemma in lemmas:
                    synonym = lemma.name().replace('_', ' ')
                    if synonym.lower() != word.lower():
                        synonyms.add(synonym)
            
            return list(synonyms)[:15]  # Limit to 15 synonyms
            
        except Exception as e:
            logging.error(f"Error getting synonyms for '{word}': {e}")
            return []
    
    def expand_with_synonyms(self, keyword: str) -> List[str]:
        """Expand a keyword phrase with synonyms of each word"""
        expanded_phrases = set()
        
        try:
            words = word_tokenize(keyword.lower())
            words = [word for word in words if word not in self.punctuation and word not in self.stop_words]
            
            if not words:
                return [keyword]
            
            # For each word, get synonyms and create variations
            for i, word in enumerate(words):
                synonyms = self.get_synonyms(word)
                
                for synonym in synonyms[:5]:  # Use top 5 synonyms
                    new_words = words.copy()
                    new_words[i] = synonym
                    new_phrase = ' '.join(new_words)
                    expanded_phrases.add(new_phrase)
            
            # Also add the original keyword
            expanded_phrases.add(keyword)
            
            return list(expanded_phrases)[:20]  # Limit to 20 variations
            
        except Exception as e:
            logging.error(f"Error expanding '{keyword}' with synonyms: {e}")
            return [keyword]
    
    def generate_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Generate n-grams from text"""
        try:
            tokens = word_tokenize(text.lower())
            tokens = [token for token in tokens if token not in self.punctuation and token not in self.stop_words]
            
            if len(tokens) < n:
                return []
            
            n_grams = list(ngrams(tokens, n))
            return [' '.join(gram) for gram in n_grams]
            
        except Exception as e:
            logging.error(f"Error generating {n}-grams from text: {e}")
            return []
    
    def generate_phrase_variations(self, keyword: str) -> List[str]:
        """Generate various phrase combinations and structures"""
        variations = set()
        
        try:
            # Original keyword
            variations.add(keyword)
            
            # Different orderings (for multi-word keywords)
            words = keyword.split()
            if len(words) > 1:
                # Reverse order
                variations.add(' '.join(reversed(words)))
                
                # If 3+ words, try different combinations
                if len(words) >= 3:
                    variations.add(f"{words[-1]} {' '.join(words[:-1])}")
                    variations.add(f"{words[1]} {words[0]} {' '.join(words[2:])}")
            
            # Add common modifiers
            modifiers = {
                'prefixes': ['best', 'top', 'ultimate', 'complete', 'beginner', 'advanced', 'how to', 'guide to'],
                'suffixes': ['guide', 'book', 'manual', 'handbook', 'tutorial', 'course', 'tips', 'secrets']
            }
            
            for prefix in modifiers['prefixes']:
                variations.add(f"{prefix} {keyword}")
            
            for suffix in modifiers['suffixes']:
                variations.add(f"{keyword} {suffix}")
            
            # Question formats
            question_starters = ['how to', 'what is', 'why is', 'when to', 'where to']
            for starter in question_starters:
                if not keyword.lower().startswith(starter):
                    variations.add(f"{starter} {keyword}")
            
            return list(variations)[:25]  # Limit to 25 variations
            
        except Exception as e:
            logging.error(f"Error generating phrase variations for '{keyword}': {e}")
            return [keyword]
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text using n-gram analysis"""
        key_phrases = []
        
        try:
            # Generate bigrams and trigrams
            bigrams = self.generate_ngrams(text, 2)
            trigrams = self.generate_ngrams(text, 3)
            
            # Combine and count frequency
            all_phrases = bigrams + trigrams
            phrase_counts = Counter(all_phrases)
            
            # Filter out phrases with very common words
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
            
            filtered_phrases = []
            for phrase, count in phrase_counts.items():
                words = phrase.split()
                if not any(word in common_words for word in words) and len(phrase) > 3:
                    filtered_phrases.append((phrase, count))
            
            # Sort by frequency and return top phrases
            filtered_phrases.sort(key=lambda x: x[1], reverse=True)
            key_phrases = [phrase for phrase, count in filtered_phrases[:max_phrases]]
            
        except Exception as e:
            logging.error(f"Error extracting key phrases: {e}")
        
        return key_phrases
    
    def build_semantic_keyword_groups(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Group keywords by semantic similarity"""
        groups = {}
        
        try:
            # Define semantic categories for books/content
            categories = {
                'how_to': ['how to', 'guide', 'tutorial', 'step by step', 'instructions', 'learn'],
                'business': ['business', 'entrepreneur', 'marketing', 'sales', 'profit', 'money', 'finance'],
                'health': ['health', 'fitness', 'diet', 'nutrition', 'wellness', 'exercise', 'weight'],
                'technology': ['technology', 'software', 'programming', 'computer', 'digital', 'tech'],
                'cooking': ['cooking', 'recipe', 'food', 'kitchen', 'meal', 'chef', 'cookbook'],
                'self_help': ['self help', 'motivation', 'success', 'confidence', 'mindset', 'personal'],
                'romance': ['romance', 'love', 'relationship', 'dating', 'marriage'],
                'children': ['children', 'kids', 'child', 'parenting', 'family'],
                'education': ['education', 'learning', 'study', 'school', 'teaching', 'academic'],
                'fiction': ['fiction', 'novel', 'story', 'fantasy', 'mystery', 'thriller']
            }
            
            # Initialize groups
            for category in categories:
                groups[category] = []
            groups['other'] = []
            
            # Categorize keywords
            for keyword in keywords:
                keyword_lower = keyword.lower()
                categorized = False
                
                for category, category_words in categories.items():
                    if any(str(word) in keyword_lower for word in category_words):
                        groups[category].append(keyword)
                        categorized = True
                        break
                
                if not categorized:
                    groups['other'].append(keyword)
            
            # Remove empty groups
            groups = {k: v for k, v in groups.items() if v}
            
        except Exception as e:
            logging.error(f"Error building semantic keyword groups: {e}")
        
        return groups
    
    def generate_long_tail_keywords(self, base_keyword: str, context: str = 'books') -> List[str]:
        """Generate long-tail keyword variations for specific contexts"""
        long_tail_keywords = []
        
        try:
            # Context-specific templates
            if context.lower() == 'books':
                templates = [
                    "how to {keyword}",
                    "best {keyword} book",
                    "{keyword} for beginners",
                    "{keyword} step by step",
                    "complete guide to {keyword}",
                    "{keyword} made easy",
                    "learn {keyword}",
                    "{keyword} secrets",
                    "{keyword} tips and tricks",
                    "ultimate {keyword} guide",
                    "{keyword} handbook",
                    "{keyword} mastery",
                    "beginner's guide to {keyword}",
                    "{keyword} for dummies",
                    "advanced {keyword} techniques"
                ]
            else:
                templates = [
                    "how to {keyword}",
                    "best {keyword}",
                    "{keyword} guide",
                    "{keyword} tips",
                    "{keyword} tutorial",
                    "{keyword} course",
                    "learn {keyword}",
                    "{keyword} training"
                ]
            
            # Generate variations
            for template in templates:
                long_tail = template.format(keyword=base_keyword)
                long_tail_keywords.append(long_tail)
            
            # Add question-based variations
            question_templates = [
                "what is {keyword}",
                "how does {keyword} work",
                "why use {keyword}",
                "when to use {keyword}",
                "where to learn {keyword}"
            ]
            
            for template in question_templates:
                question = template.format(keyword=base_keyword)
                long_tail_keywords.append(question)
            
        except Exception as e:
            logging.error(f"Error generating long-tail keywords for '{base_keyword}': {e}")
        
        return long_tail_keywords[:20]  # Limit to 20 variations
    
    def analyze_keyword_intent(self, keyword: str) -> Dict[str, any]:
        """Analyze the intent behind a keyword"""
        intent_analysis = {
            'intent_type': 'informational',
            'commercial_signals': 0,
            'urgency_level': 'low',
            'specificity': 'general',
            'question_based': False
        }
        
        try:
            keyword_lower = keyword.lower()
            
            # Commercial intent signals
            commercial_words = ['buy', 'purchase', 'price', 'cost', 'cheap', 'discount', 'deal', 'sale', 'order']
            commercial_count = sum(1 for word in commercial_words if word in keyword_lower)
            intent_analysis['commercial_signals'] = commercial_count
            
            if commercial_count > 0:
                intent_analysis['intent_type'] = 'commercial'
            
            # Question-based keywords
            question_words = ['how', 'what', 'why', 'when', 'where', 'who', 'which']
            if any(keyword_lower.startswith(word) for word in question_words):
                intent_analysis['question_based'] = True
                intent_analysis['intent_type'] = 'informational'
            
            # Urgency indicators
            urgent_words = ['now', 'today', 'immediately', 'urgent', 'quick', 'fast']
            if any(word in keyword_lower for word in urgent_words):
                intent_analysis['urgency_level'] = 'high'
            elif any(word in keyword_lower for word in ['soon', 'this week', 'asap']):
                intent_analysis['urgency_level'] = 'medium'
            
            # Specificity level
            word_count = len(keyword.split())
            if word_count >= 4:
                intent_analysis['specificity'] = 'highly specific'
            elif word_count == 3:
                intent_analysis['specificity'] = 'specific'
            elif word_count == 2:
                intent_analysis['specificity'] = 'moderate'
            
        except Exception as e:
            logging.error(f"Error analyzing intent for '{keyword}': {e}")
        
        return intent_analysis
