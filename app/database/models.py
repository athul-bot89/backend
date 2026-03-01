"""
Database models for the teaching assistant application.
Defines the structure of tables for textbooks, chapters, and related content.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Base class for all database models
Base = declarative_base()

class Textbook(Base):
    """Model for storing textbook information."""
    __tablename__ = "textbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to the uploaded PDF
    total_pages = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Table of contents info
    toc_start_page = Column(Integer)  # Start page of table of contents
    toc_end_page = Column(Integer)    # End page of table of contents
    toc_text = Column(Text)           # Extracted text from TOC
    
    # Relationships
    chapters = relationship("Chapter", back_populates="textbook", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Textbook(title='{self.title}', id={self.id})>"


class Chapter(Base):
    """Model for storing individual chapter information."""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    
    # Content storage
    pdf_path = Column(String(500))  # Path to the split chapter PDF
    extracted_text = Column(Text)   # Full text content of the chapter
    
    # AI-generated content (to be used later)
    summary = Column(Text)
    key_concepts = Column(Text)  # JSON string of key concepts
    
    # Processing status fields
    processing_status = Column(String(50), default="pending")  # pending, processing, pdf_ready, completed, failed
    processing_error = Column(Text)  # Error message if processing failed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    textbook = relationship("Textbook", back_populates="chapters")
    worksheets = relationship("Worksheet", back_populates="chapter", cascade="all, delete-orphan")
    lesson_plans = relationship("LessonPlan", back_populates="chapter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chapter(title='{self.title}', number={self.chapter_number})>"


class Worksheet(Base):
    """Model for storing generated worksheets."""
    __tablename__ = "worksheets"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(255), nullable=False)
    difficulty_level = Column(String(50))  # e.g., "beginner", "intermediate", "advanced"
    content = Column(Text, nullable=False)  # JSON or markdown content
    answer_key = Column(Text)  # Answer key for the worksheet
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="worksheets")
    
    def __repr__(self):
        return f"<Worksheet(title='{self.title}', id={self.id})>"


class LessonPlan(Base):
    """Model for storing generated lesson plans."""
    __tablename__ = "lesson_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(255), nullable=False)
    duration_minutes = Column(Integer)  # Estimated lesson duration
    objectives = Column(Text)  # Learning objectives (JSON)
    activities = Column(Text)  # Lesson activities (JSON)
    materials_needed = Column(Text)  # Required materials
    content = Column(Text, nullable=False)  # Full lesson plan content
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="lesson_plans")
    
    def __repr__(self):
        return f"<LessonPlan(title='{self.title}', id={self.id})>"