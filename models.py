from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

class ResearchSession(db.Model):
    __tablename__ = 'research_sessions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    data = Column(Text, nullable=False)  # JSON string of search results
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResearchSession {self.name}>'

class FavoriteKeyword(db.Model):
    __tablename__ = 'favorite_keywords'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(500), nullable=False, unique=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FavoriteKeyword {self.keyword}>'
