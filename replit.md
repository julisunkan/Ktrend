# KDP Keyword Research Tool

## Overview

The KDP Keyword Research Tool is a comprehensive Flask web application designed to help Amazon KDP authors and publishers discover profitable book keywords and trending topics. The application leverages multiple free APIs and web scraping techniques to provide keyword expansion, trend analysis, competitor intelligence, and profitability scoring. It features a modern dark-themed UI with data visualization capabilities and session management for research workflow optimization.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with configurable PostgreSQL support via DATABASE_URL
- **Session Management**: Flask sessions with configurable secret key for user state persistence
- **Modular Design**: Utility modules separated into distinct components for keyword generation, trend analysis, Amazon analysis, NLP processing, and export functionality

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap dark theme for responsive UI
- **JavaScript Framework**: Vanilla JavaScript with Chart.js for data visualization
- **Styling**: Bootstrap CSS with custom CSS overrides and Font Awesome icons
- **Theme System**: Dark/light mode toggle with localStorage persistence

### Data Processing Pipeline
- **Keyword Expansion**: Multi-source keyword generation using Google Autocomplete, DuckDuckGo suggestions, and Wikipedia titles
- **NLP Processing**: NLTK-based synonym generation, N-gram analysis, and text processing with WordNet integration
- **Scoring Algorithm**: Custom difficulty and profitability scoring based on competition analysis and search volume metrics
- **Clustering**: Scikit-learn TF-IDF vectorization with K-means clustering for keyword grouping

### API Integration Strategy
- **Google Trends**: PyTrends library for search volume and related query data
- **Amazon Analysis**: Web scraping with BeautifulSoup for competitor research and market intelligence
- **Trend Discovery**: RSS feed parsing and social media trend extraction
- **Rate Limiting**: Session-based request management with proper delays and error handling

### Data Models
- **ResearchSession**: Stores keyword research sessions with JSON data serialization
- **FavoriteKeyword**: User-curated keyword collections with notes and timestamps
- **Database Design**: SQLAlchemy models with datetime tracking and relationship management

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework with SQLAlchemy extension for database operations
- **Werkzeug**: WSGI utilities and middleware for proxy handling

### Data Analysis Libraries
- **pandas**: Data manipulation and analysis for trend data processing
- **numpy**: Numerical computing for statistical calculations
- **scikit-learn**: Machine learning library for clustering and text vectorization
- **NLTK**: Natural language processing for synonym generation and text analysis

### Web Scraping and API Libraries
- **requests**: HTTP client for API calls and web scraping
- **BeautifulSoup4**: HTML/XML parsing for Amazon data extraction
- **pytrends**: Google Trends API wrapper for search volume data
- **feedparser**: RSS feed parsing for trend discovery

### Export and Visualization
- **reportlab**: PDF generation for research reports
- **openpyxl**: Excel file generation for data export
- **Chart.js**: Frontend charting library for data visualization

### UI and Styling
- **Bootstrap**: CSS framework with dark theme support
- **Font Awesome**: Icon library for UI enhancement
- **Custom CSS**: Theme-aware styling with CSS variables

### Development Tools
- **lxml**: XML/HTML parser for BeautifulSoup backend
- **logging**: Built-in Python logging for error tracking and debugging