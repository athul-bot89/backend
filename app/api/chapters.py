"""
API endpoints for chapter management.
Handles chapter detection, creation, and content extraction.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json

from app.database.database import get_db
from app.database.models import Textbook, Chapter
from app.models.schemas import (
    ChapterResponse,
    ChapterCreate,
    ChapterUpdate,
    ChapterBatchCreate,
    ChapterBatchResponse,
    ChapterDetectionRequest,
    ChapterDetectionResponse,
    DetectedChapter,
    TextExtractionResponse,
    PageRangeRequest,
    SummaryRequest,
    SummaryResponse,
    MessageResponse
)
from app.services.pdf_service import PDFService
from app.services.ai_service import AIService
from app.config import settings

# Create router for chapter endpoints
router = APIRouter(prefix="/chapters", tags=["chapters"])

@router.post("/detect", response_model=ChapterDetectionResponse)
def detect_chapters(
    request: ChapterDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Detect chapters from table of contents using AI.
    
    Either provide the TOC text directly or ensure the textbook has TOC pages set.
    """
    
    # Get the textbook
    textbook = db.query(Textbook).filter(Textbook.id == request.textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Get TOC text
    toc_text = request.toc_text
    if not toc_text:
        # Check if textbook has TOC pages set
        if not textbook.toc_text and (not textbook.toc_start_page or not textbook.toc_end_page):
            raise HTTPException(
                status_code=400, 
                detail="Table of contents not found. Please set TOC pages first or provide TOC text."
            )
        
        # Use stored TOC text or extract it
        if textbook.toc_text:
            toc_text = textbook.toc_text
        else:
            pdf_service = PDFService()
            toc_text = pdf_service.extract_text_from_pages(
                textbook.file_path,
                textbook.toc_start_page,
                textbook.toc_end_page
            )
            # Store for future use
            textbook.toc_text = toc_text
            db.commit()
    
    # Use AI to detect chapters
    ai_service = AIService()
    try:
        detected_chapters = ai_service.detect_chapters_from_toc(toc_text)
        
        # Convert to response format
        chapters_list = [
            DetectedChapter(
                chapter_number=ch["chapter_number"],
                title=ch["title"],
                detected_page=ch.get("detected_page")
            )
            for ch in detected_chapters
        ]
        
        return ChapterDetectionResponse(
            detected_chapters=chapters_list,
            total_chapters=len(chapters_list)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect chapters: {str(e)}")

@router.post("/batch", response_model=ChapterBatchResponse)
def create_chapters_batch(
    batch_data: ChapterBatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create multiple chapters at once for a textbook.
    
    This endpoint also triggers background tasks to:
    - Split PDFs for each chapter
    - Extract text from each chapter
    """
    
    # Verify textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == batch_data.textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    created_chapters = []
    pdf_service = PDFService()
    
    for chapter_data in batch_data.chapters:
        # Check if chapter already exists
        existing = db.query(Chapter).filter(
            Chapter.textbook_id == batch_data.textbook_id,
            Chapter.chapter_number == chapter_data.chapter_number
        ).first()
        
        if existing:
            continue  # Skip if chapter already exists
        
        # Create chapter
        chapter = Chapter(
            textbook_id=batch_data.textbook_id,
            chapter_number=chapter_data.chapter_number,
            title=chapter_data.title,
            start_page=chapter_data.start_page,
            end_page=chapter_data.end_page
        )
        
        # Generate chapter PDF path
        chapter_filename = f"textbook_{batch_data.textbook_id}_chapter_{chapter_data.chapter_number}.pdf"
        chapter_pdf_path = os.path.join(settings.chapters_dir, chapter_filename)
        
        try:
            # Split PDF for this chapter
            pdf_service.split_pdf_by_pages(
                textbook.file_path,
                chapter_pdf_path,
                chapter_data.start_page,
                chapter_data.end_page
            )
            chapter.pdf_path = chapter_pdf_path
            
            # Extract text from chapter
            chapter_text = pdf_service.extract_text_from_pages(
                textbook.file_path,
                chapter_data.start_page,
                chapter_data.end_page
            )
            chapter.extracted_text = chapter_text
            
        except Exception as e:
            print(f"Error processing chapter {chapter_data.chapter_number}: {e}")
            # Continue with chapter creation even if PDF processing fails
        
        db.add(chapter)
        created_chapters.append(chapter)
    
    db.commit()
    
    # Refresh to get IDs
    for chapter in created_chapters:
        db.refresh(chapter)
    
    return ChapterBatchResponse(
        created_count=len(created_chapters),
        chapters=created_chapters
    )

@router.get("/textbook/{textbook_id}", response_model=List[ChapterResponse])
def list_chapters_by_textbook(
    textbook_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all chapters for a specific textbook.
    
    - **textbook_id**: ID of the textbook
    """
    
    # Verify textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    chapters = db.query(Chapter).filter(
        Chapter.textbook_id == textbook_id
    ).order_by(Chapter.chapter_number).all()
    
    return chapters

@router.get("/{chapter_id}", response_model=ChapterResponse)
def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific chapter.
    
    - **chapter_id**: ID of the chapter
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return chapter

@router.patch("/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    chapter_id: int,
    update_data: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update chapter information.
    
    - **chapter_id**: ID of the chapter to update
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    
    # If page range is updated, regenerate PDF and text
    if "start_page" in update_dict or "end_page" in update_dict:
        start_page = update_dict.get("start_page", chapter.start_page)
        end_page = update_dict.get("end_page", chapter.end_page)
        
        pdf_service = PDFService()
        textbook = chapter.textbook
        
        try:
            # Regenerate chapter PDF
            if chapter.pdf_path:
                pdf_service.split_pdf_by_pages(
                    textbook.file_path,
                    chapter.pdf_path,
                    start_page,
                    end_page
                )
            
            # Re-extract text
            chapter_text = pdf_service.extract_text_from_pages(
                textbook.file_path,
                start_page,
                end_page
            )
            chapter.extracted_text = chapter_text
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update chapter content: {str(e)}")
    
    # Update fields
    for field, value in update_dict.items():
        setattr(chapter, field, value)
    
    db.commit()
    db.refresh(chapter)
    
    return chapter

@router.post("/{chapter_id}/generate-summary", response_model=SummaryResponse)
def generate_chapter_summary(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate AI summary for a chapter.
    
    - **chapter_id**: ID of the chapter to summarize
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.extracted_text:
        raise HTTPException(status_code=400, detail="Chapter text not extracted yet")
    
    ai_service = AIService()
    
    try:
        # Generate summary
        summary = ai_service.generate_chapter_summary(
            chapter.extracted_text,
            chapter.title
        )
        
        # Extract key concepts
        key_concepts = ai_service.extract_key_concepts(chapter.extracted_text)
        
        # Store in database
        chapter.summary = summary
        chapter.key_concepts = json.dumps(key_concepts)
        db.commit()
        
        return SummaryResponse(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            summary=summary,
            key_concepts=key_concepts
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.delete("/{chapter_id}", response_model=MessageResponse)
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a chapter and its associated files.
    
    - **chapter_id**: ID of the chapter to delete
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Delete chapter PDF if it exists
    if chapter.pdf_path and os.path.exists(chapter.pdf_path):
        try:
            os.remove(chapter.pdf_path)
        except Exception as e:
            print(f"Warning: Could not delete chapter file {chapter.pdf_path}: {e}")
    
    chapter_title = chapter.title
    db.delete(chapter)
    db.commit()
    
    return MessageResponse(
        message=f"Chapter '{chapter_title}' deleted successfully"
    )