"""
Database connection and session management.
Sets up SQLAlchemy engine and provides session creation.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.models import Base

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initialize the database by creating all tables.
    Call this when starting the application.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db() -> Session:
    """
    Dependency to get database session.
    Use this in FastAPI endpoints to get a database session.
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Worksheet database operations
def create_worksheet(db: Session, chapter_id: int, title: str, content: str, 
                    difficulty_level: str = None, answer_key: str = None):
    """
    Create a new worksheet in the database.
    
    Args:
        db: Database session
        chapter_id: ID of the chapter
        title: Worksheet title
        content: JSON string of worksheet questions
        difficulty_level: Difficulty level (optional)
        answer_key: Answer key (optional)
    
    Returns:
        Created Worksheet object
    """
    from app.database.models import Worksheet
    
    worksheet = Worksheet(
        chapter_id=chapter_id,
        title=title,
        content=content,
        difficulty_level=difficulty_level,
        answer_key=answer_key
    )
    db.add(worksheet)
    db.commit()
    db.refresh(worksheet)
    return worksheet

def get_worksheet_by_chapter_id(db: Session, chapter_id: int):
    """
    Get the worksheet for a specific chapter.
    
    Args:
        db: Database session
        chapter_id: ID of the chapter
    
    Returns:
        Worksheet object or None if not found
    """
    from app.database.models import Worksheet
    
    return db.query(Worksheet).filter(
        Worksheet.chapter_id == chapter_id
    ).first()

def update_worksheet(db: Session, chapter_id: int, content: str, 
                    title: str = None, difficulty_level: str = None, 
                    answer_key: str = None):
    """
    Update an existing worksheet for a chapter.
    
    Args:
        db: Database session
        chapter_id: ID of the chapter
        content: New JSON string of worksheet questions
        title: New title (optional)
        difficulty_level: New difficulty level (optional)
        answer_key: New answer key (optional)
    
    Returns:
        Updated Worksheet object or None if not found
    """
    from app.database.models import Worksheet
    from datetime import datetime
    
    worksheet = db.query(Worksheet).filter(
        Worksheet.chapter_id == chapter_id
    ).first()
    
    if worksheet:
        worksheet.content = content
        if title:
            worksheet.title = title
        if difficulty_level:
            worksheet.difficulty_level = difficulty_level
        if answer_key:
            worksheet.answer_key = answer_key
        # Update timestamp
        worksheet.created_at = datetime.utcnow()
        
        db.commit()
        db.refresh(worksheet)
        return worksheet
    return None

def delete_worksheet_by_chapter_id(db: Session, chapter_id: int):
    """
    Delete the worksheet for a specific chapter.
    
    Args:
        db: Database session
        chapter_id: ID of the chapter
    
    Returns:
        True if deleted, False if not found
    """
    from app.database.models import Worksheet
    
    worksheet = db.query(Worksheet).filter(
        Worksheet.chapter_id == chapter_id
    ).first()
    
    if worksheet:
        db.delete(worksheet)
        db.commit()
        return True
    return False