"""
API endpoints for chapter management.
Handles chapter detection, creation, and content extraction.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
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
    WorksheetQuestion,
    WorksheetResponse,
    ChapterQuestionRequest,
    ChapterAnswerResponse,
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
        # AI service now returns {"chapters": [...]}
        result = ai_service.detect_chapters_from_toc(toc_text)
        
        # Convert to response format with auto-fix for end_page
        chapters_raw = result.get("chapters", [])
        chapters_list = []
        
        for i, ch in enumerate(chapters_raw):
            end_page = ch.get("end_page", 0)
            start_page = ch.get("start_page", 0)
            
            # Auto-fix end_page if it's 0
            if end_page == 0 and i < len(chapters_raw) - 1:
                # Use next chapter's start_page - 1
                next_ch = chapters_raw[i + 1]
                end_page = next_ch.get("start_page", 0) - 1 if next_ch.get("start_page", 0) > 0 else 0
            
            chapters_list.append(
                DetectedChapter(
                    title=ch["title"],
                    chapter_number=ch["chapter_number"],
                    start_page=start_page,
                    end_page=end_page
                )
            )
        
        return ChapterDetectionResponse(
            textbook_id=request.textbook_id,
            chapters=chapters_list
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect chapters: {str(e)}")

@router.post("/batch", response_model=ChapterBatchResponse)
def create_chapters_batch(
    batch_data: ChapterBatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    async_processing: bool = True  # New parameter for async processing
):
    """
    Create multiple chapters at once for a textbook.
    
    - **async_processing**: If True (default), heavy PDF processing is done in background.
                           Returns immediately with chapter records.
                           If False, processes synchronously (may take longer).
    
    This endpoint can trigger background tasks to:
    - Split PDFs for each chapter
    - Extract text from each chapter
    """
    
    # Verify textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == batch_data.textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    if not os.path.exists(textbook.file_path):
        raise HTTPException(status_code=404, detail="Textbook PDF file not found")
    
    created_chapters = []
    skipped_chapters = []
    pdf_service = PDFService()
    
    # Create chapters directory if it doesn't exist
    os.makedirs(settings.chapters_dir, exist_ok=True)
    
    for i, chapter_data in enumerate(batch_data.chapters):
        # Check if chapter already exists
        existing = db.query(Chapter).filter(
            Chapter.textbook_id == batch_data.textbook_id,
            Chapter.chapter_number == chapter_data.chapter_number
        ).first()
        
        if existing:
            skipped_chapters.append(chapter_data.chapter_number)
            continue  # Skip if chapter already exists
        
        # Auto-fix end_page if it's 0 or invalid
        end_page = chapter_data.end_page
        if end_page == 0:
            # Try to use the next chapter's start_page - 1
            if i < len(batch_data.chapters) - 1:
                next_chapter = batch_data.chapters[i + 1]
                end_page = next_chapter.start_page - 1
            else:
                # For the last chapter, use textbook's total pages
                end_page = textbook.total_pages if textbook.total_pages else chapter_data.start_page + 20
        
        # Ensure end_page is at least equal to start_page
        if end_page < chapter_data.start_page:
            end_page = chapter_data.start_page
        
        # Create chapter record
        chapter = Chapter(
            textbook_id=batch_data.textbook_id,
            chapter_number=chapter_data.chapter_number,
            title=chapter_data.title,
            start_page=chapter_data.start_page,
            end_page=end_page,
            processing_status="pending" if async_processing else "processing"
        )
        
        # Generate chapter PDF path
        chapter_filename = f"textbook_{batch_data.textbook_id}_chapter_{chapter_data.chapter_number}.pdf"
        chapter_pdf_path = os.path.join(settings.chapters_dir, chapter_filename)
        chapter.pdf_path = chapter_pdf_path
        
        # Add chapter to database first
        db.add(chapter)
        db.flush()  # Flush to get the ID without committing
        created_chapters.append(chapter)
        
        if async_processing:
            # Schedule background processing for this chapter
            background_tasks.add_task(
                process_chapter_async,
                chapter_id=chapter.id,
                textbook_path=textbook.file_path,
                chapter_pdf_path=chapter_pdf_path,
                start_page=chapter_data.start_page,
                end_page=end_page,
                db_url=str(db.bind.url)  # Pass DB URL for background task
            )
        else:
            # Process synchronously with timeout protection
            try:
                # Split PDF for this chapter (with timeout)
                pdf_service.split_pdf_by_pages(
                    textbook.file_path,
                    chapter_pdf_path,
                    chapter_data.start_page,
                    end_page
                )
                
                # For synchronous mode, skip OCR to prevent hanging
                # Text extraction can be done later via separate endpoint
                chapter.processing_status = "pdf_ready"
                
            except Exception as e:
                print(f"Error processing chapter {chapter_data.chapter_number}: {e}")
                chapter.processing_status = "failed"
                chapter.processing_error = str(e)
    
    # Commit all chapters
    db.commit()
    
    # Refresh to get IDs
    for chapter in created_chapters:
        db.refresh(chapter)
    
    response = ChapterBatchResponse(
        created_count=len(created_chapters),
        chapters=created_chapters
    )
    
    # Add info about processing mode
    if async_processing:
        response.message = f"Created {len(created_chapters)} chapters. PDF processing scheduled in background."
    else:
        response.message = f"Created {len(created_chapters)} chapters with PDFs."
    
    if skipped_chapters:
        response.message += f" Skipped {len(skipped_chapters)} existing chapters: {skipped_chapters}"
    
    return response


def process_chapter_async(
    chapter_id: int,
    textbook_path: str,
    chapter_pdf_path: str,
    start_page: int,
    end_page: int,
    db_url: str
):
    """
    Background task to process a chapter's PDF and extract text.
    Runs asynchronously after the API response is sent.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create new database session for background task
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get the chapter
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            return
        
        chapter.processing_status = "processing"
        db.commit()
        
        pdf_service = PDFService()
        
        # Split PDF
        try:
            pdf_service.split_pdf_by_pages(
                textbook_path,
                chapter_pdf_path,
                start_page,
                end_page
            )
            chapter.processing_status = "pdf_ready"
            db.commit()
        except Exception as e:
            chapter.processing_status = "pdf_failed"
            chapter.processing_error = f"PDF split failed: {str(e)}"
            db.commit()
            return
        
        # Extract text (optional, can be done separately)
        try:
            chapter_text = pdf_service.extract_text_from_pages(
                textbook_path,
                start_page,
                end_page,
                ocr_fallback=True,  # Enable OCR to ensure all text is extracted
                ocr_language="eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori"  # Support multiple languages
            )
            chapter.extracted_text = chapter_text
            chapter.processing_status = "completed"
        except Exception as e:
            chapter.processing_status = "text_extraction_failed"
            chapter.processing_error = f"Text extraction failed: {str(e)}"
        
        db.commit()
        
    except Exception as e:
        print(f"Background processing error for chapter {chapter_id}: {e}")
    finally:
        db.close()

@router.get("/textbook/{textbook_id}/processing-status")
def get_chapters_processing_status(
    textbook_id: int,
    db: Session = Depends(get_db)
):
    """
    Get processing status for all chapters of a textbook.
    
    Returns a summary of chapter processing states.
    """
    
    # Verify textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    chapters = db.query(Chapter).filter(
        Chapter.textbook_id == textbook_id
    ).order_by(Chapter.chapter_number).all()
    
    status_summary = {
        "total": len(chapters),
        "pending": 0,
        "processing": 0,
        "pdf_ready": 0,
        "completed": 0,
        "failed": 0,
        "text_extraction_failed": 0,
        "pdf_failed": 0
    }
    
    chapter_statuses = []
    for chapter in chapters:
        status = chapter.processing_status or "pending"
        if status in status_summary:
            status_summary[status] += 1
        
        chapter_statuses.append({
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "status": status,
            "error": chapter.processing_error,
            "has_pdf": bool(chapter.pdf_path and os.path.exists(chapter.pdf_path)),
            "has_text": bool(chapter.extracted_text)
        })
    
    return {
        "textbook_id": textbook_id,
        "summary": status_summary,
        "chapters": chapter_statuses
    }

@router.post("/{chapter_id}/reprocess")
def reprocess_chapter(
    chapter_id: int,
    background_tasks: BackgroundTasks,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    Reprocess a failed or incomplete chapter.
    
    - **chapter_id**: ID of the chapter to reprocess
    - **force**: Force reprocessing even if already completed
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Check if already processing
    if chapter.processing_status == "processing":
        return {"message": "Chapter is already being processed"}
    
    # Check if already completed
    if chapter.processing_status == "completed" and not force:
        return {"message": "Chapter already processed successfully. Use force=true to reprocess."}
    
    textbook = chapter.textbook
    
    # Reset status
    chapter.processing_status = "pending"
    chapter.processing_error = None
    db.commit()
    
    # Schedule background processing
    background_tasks.add_task(
        process_chapter_async,
        chapter_id=chapter.id,
        textbook_path=textbook.file_path,
        chapter_pdf_path=chapter.pdf_path,
        start_page=chapter.start_page,
        end_page=chapter.end_page,
        db_url=str(db.bind.url)
    )
    
    return {
        "message": f"Chapter '{chapter.title}' scheduled for reprocessing",
        "chapter_id": chapter.id
    }

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
            
            # Re-extract text with Indian language OCR support
            chapter_text = pdf_service.extract_text_from_pages(
                textbook.file_path,
                start_page,
                end_page,
                ocr_fallback=True,
                ocr_language="eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori"
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

@router.post("/{chapter_id}/reextract-text", response_model=ChapterResponse)
def reextract_chapter_text(
    chapter_id: int,
    ocr_language: str = "eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori",
    ocr_enabled: bool = True,
    use_indian_extractor: bool = True,
    db: Session = Depends(get_db)
):
    """
    Re-extract text from a chapter with specific OCR settings.
    
    Useful when the initial extraction didn't capture Indian language text properly.
    
    - **chapter_id**: ID of the chapter
    - **ocr_language**: OCR languages to use (e.g., "eng+hin+tam" for English, Hindi, and Tamil)
    - **ocr_enabled**: Enable OCR for image-based PDFs
    - **use_indian_extractor**: Use specialized Indian language extraction method
    
    Supported languages:
    - eng: English
    - hin: Hindi
    - tam: Tamil  
    - tel: Telugu
    - kan: Kannada
    - mal: Malayalam
    - mar: Marathi
    - guj: Gujarati
    - ben: Bengali
    - pan: Punjabi
    - ori: Odia
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    pdf_service = PDFService()
    textbook = chapter.textbook
    
    try:
        # Use specialized Indian language extractor if requested
        if use_indian_extractor:
            chapter_text = pdf_service.extract_indian_language_text(
                textbook.file_path,
                chapter.start_page,
                chapter.end_page
            )
        else:
            # Re-extract text with specified OCR settings
            chapter_text = pdf_service.extract_text_from_pages(
                textbook.file_path,
                chapter.start_page,
                chapter.end_page,
                ocr_fallback=ocr_enabled,
                ocr_language=ocr_language
            )
        
        chapter.extracted_text = chapter_text
        db.commit()
        db.refresh(chapter)
        
        return chapter
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-extract text: {str(e)}")

@router.post("/{chapter_id}/generate-summary", response_model=SummaryResponse)
def generate_chapter_summary(
    chapter_id: int,
    force_regenerate: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """
    Generate or retrieve AI summary for a chapter.
    
    - **chapter_id**: ID of the chapter to summarize
    - **force_regenerate**: Force regeneration of summary even if it exists (default: False)
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.extracted_text:
        raise HTTPException(status_code=400, detail="Chapter text not extracted yet")
    
    # Check if summary already exists and return it unless forced to regenerate
    if chapter.summary and chapter.key_concepts and not force_regenerate:
        # Parse stored key concepts
        try:
            key_concepts = json.loads(chapter.key_concepts) if isinstance(chapter.key_concepts, str) else chapter.key_concepts
        except (json.JSONDecodeError, TypeError):
            key_concepts = []
        
        return SummaryResponse(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            summary=chapter.summary,
            key_concepts=key_concepts
        )
    
    # Generate new summary if it doesn't exist or if forced
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

@router.post("/{chapter_id}/generate-worksheet", response_model=WorksheetResponse)
def generate_chapter_worksheet(
    chapter_id: int,
    num_questions: Optional[int] = 10,
    regenerate: bool = Query(False, description="Force regeneration of worksheet even if cached"),
    db: Session = Depends(get_db)
):
    """
    Generate a worksheet with questions for a chapter.
    Returns cached worksheet if exists, unless regenerate=true.
    
    - **chapter_id**: ID of the chapter to generate questions from
    - **num_questions**: Number of questions to generate (default 10, max 20)
    - **regenerate**: Force regeneration of worksheet (default: false)
    """
    # Limit the number of questions
    if num_questions > 20:
        num_questions = 20
    elif num_questions < 1:
        num_questions = 1
    
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.extracted_text:
        raise HTTPException(status_code=400, detail="Chapter text not extracted yet")
    
    # Import database operations
    from app.database.database import (
        get_worksheet_by_chapter_id,
        create_worksheet,
        update_worksheet
    )
    import json
    
    # Check if worksheet exists and regenerate flag is not set
    if not regenerate:
        existing_worksheet = get_worksheet_by_chapter_id(db, chapter_id)
        if existing_worksheet:
            # Parse stored worksheet and return it
            try:
                stored_questions = json.loads(existing_worksheet.content)
                questions = [
                    WorksheetQuestion(
                        question=q["question"],
                        question_type=q["question_type"],
                        options=q.get("options"),
                        correct_answer=q.get("correct_answer"),
                        difficulty=q.get("difficulty", "medium")
                    )
                    for q in stored_questions
                ]
                
                return WorksheetResponse(
                    chapter_id=chapter.id,
                    chapter_title=chapter.title,
                    total_questions=len(questions),
                    questions=questions
                )
            except json.JSONDecodeError:
                # If stored content is corrupted, regenerate
                pass
    
    ai_service = AIService()
    
    try:
        # Generate worksheet questions
        questions_data = ai_service.generate_worksheet_questions(
            chapter.extracted_text,
            chapter.title,
            num_questions
        )
        
        # Convert to WorksheetQuestion objects
        questions = [
            WorksheetQuestion(
                question=q["question"],
                question_type=q["question_type"],
                options=q.get("options"),
                correct_answer=q.get("correct_answer"),
                difficulty=q.get("difficulty", "medium")
            )
            for q in questions_data
        ]
        
        # Store or update the worksheet in database
        worksheet_title = f"Worksheet for {chapter.title}"
        worksheet_content = json.dumps(questions_data, ensure_ascii=False)
        
        existing_worksheet = get_worksheet_by_chapter_id(db, chapter_id)
        if existing_worksheet:
            # Update existing worksheet
            update_worksheet(
                db,
                chapter_id=chapter_id,
                content=worksheet_content,
                title=worksheet_title,
                difficulty_level="mixed"  # Since we generate mixed difficulty questions
            )
        else:
            # Create new worksheet
            create_worksheet(
                db,
                chapter_id=chapter_id,
                title=worksheet_title,
                content=worksheet_content,
                difficulty_level="mixed"
            )
        
        return WorksheetResponse(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            total_questions=len(questions),
            questions=questions
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate worksheet: {str(e)}")

@router.delete("/{chapter_id}/worksheet")
def delete_chapter_worksheet(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete the cached worksheet for a chapter.
    Forces regeneration on next request.
    
    - **chapter_id**: ID of the chapter whose worksheet to delete
    """
    from app.database.database import delete_worksheet_by_chapter_id
    
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    deleted = delete_worksheet_by_chapter_id(db, chapter_id)
    if deleted:
        return {"message": f"Worksheet for chapter '{chapter.title}' has been deleted"}
    else:
        return {"message": f"No worksheet found for chapter '{chapter.title}'"}

@router.post("/{chapter_id}/ask-question", response_model=ChapterAnswerResponse)
def ask_chapter_question(
    chapter_id: int,
    request: ChapterQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about a specific chapter and get an AI-powered answer.
    
    - **chapter_id**: ID of the chapter to ask about
    - **question**: The question or doubt about the chapter
    - **include_context**: Whether to use chapter context (default: true)
    - **conversation_history**: Optional previous Q&A for maintaining context
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.extracted_text:
        raise HTTPException(status_code=400, detail="Chapter text not extracted yet")
    
    ai_service = AIService()
    
    try:
        # Get answer from AI service
        result = ai_service.answer_chapter_question(
            chapter_text=chapter.extracted_text if request.include_context else "",
            chapter_title=chapter.title,
            question=request.question,
            conversation_history=request.conversation_history
        )
        
        # Return the response
        return ChapterAnswerResponse(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            question=request.question,
            answer=result["answer"],
            related_concepts=result.get("related_concepts", []),
            confidence_score=result.get("confidence_score")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")

@router.post("/{chapter_id}/chat", response_model=ChapterAnswerResponse)
def chat_about_chapter(
    chapter_id: int,
    request: ChapterQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Interactive chat endpoint for discussing a chapter.
    Similar to ask-question but optimized for conversational interaction.
    
    - **chapter_id**: ID of the chapter to discuss
    - **question**: User's message or question
    - **conversation_history**: Previous conversation for context continuity
    """
    # This endpoint uses the same logic as ask_chapter_question
    # but you could customize it differently if needed
    return ask_chapter_question(chapter_id, request, db)

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