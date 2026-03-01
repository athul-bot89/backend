"""
API endpoints for textbook management.
Handles textbook upload, listing, and management operations.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
from fastapi.responses import FileResponse, StreamingResponse
import io

from app.database.database import get_db
from app.database.models import Textbook
from app.models.schemas import (
    TextbookCreate, 
    TextbookResponse, 
    TextbookUpdate,
    FileUploadResponse,
    MessageResponse
)
from app.config import settings
from app.services.pdf_service import PDFService

# Create router for textbook endpoints
router = APIRouter(prefix="/textbooks", tags=["textbooks"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_textbook(
    file: UploadFile = File(..., description="PDF file to upload"),
    title: str = Form(..., description="Title of the textbook"),
    author: Optional[str] = Form(None, description="Author of the textbook"),
    db: Session = Depends(get_db)
):
    """
    Upload a new textbook PDF file.
    
    - **file**: PDF file to upload (max 50MB)
    - **title**: Title of the textbook
    - **author**: Optional author name
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check file size
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {settings.max_upload_size // 1024 // 1024}MB"
        )
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(settings.upload_dir, safe_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get PDF information
        pdf_service = PDFService()
        total_pages = pdf_service.get_total_pages(file_path)
        
        # Create database entry
        textbook = Textbook(
            title=title,
            author=author,
            original_filename=file.filename,
            file_path=file_path,
            total_pages=total_pages
        )
        
        db.add(textbook)
        db.commit()
        db.refresh(textbook)
        
        return FileUploadResponse(
            filename=file.filename,
            file_path=file_path,
            size_bytes=file_size,
            message=f"Textbook uploaded successfully. Total pages: {total_pages}"
        )
    
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload textbook: {str(e)}")

@router.get("/", response_model=List[TextbookResponse])
def list_textbooks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get a list of all uploaded textbooks.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    textbooks = db.query(Textbook).offset(skip).limit(limit).all()
    
    # Add chapter count for each textbook
    for textbook in textbooks:
        textbook.chapter_count = len(textbook.chapters)
    
    return textbooks

@router.get("/{textbook_id}", response_model=TextbookResponse)
def get_textbook(
    textbook_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific textbook by ID.
    
    - **textbook_id**: ID of the textbook to retrieve
    """
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    textbook.chapter_count = len(textbook.chapters)
    return textbook

@router.patch("/{textbook_id}", response_model=TextbookResponse)
def update_textbook(
    textbook_id: int,
    update_data: TextbookUpdate,
    db: Session = Depends(get_db)
):
    """
    Update textbook information.
    
    - **textbook_id**: ID of the textbook to update
    - **update_data**: Fields to update
    """
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(textbook, field, value)
    
    # If TOC pages are updated, extract the TOC text
    if update_data.toc_start_page and update_data.toc_end_page:
        try:
            pdf_service = PDFService()
            toc_text = pdf_service.extract_text_from_pages(
                textbook.file_path,
                update_data.toc_start_page,
                update_data.toc_end_page,
                ocr_fallback=True,
                ocr_language="eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori"
            )
            textbook.toc_text = toc_text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract TOC text: {str(e)}")
    
    db.commit()
    db.refresh(textbook)
    
    textbook.chapter_count = len(textbook.chapters)
    return textbook

@router.delete("/{textbook_id}", response_model=MessageResponse)
def delete_textbook(
    textbook_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a textbook and all its associated data.
    
    - **textbook_id**: ID of the textbook to delete
    """
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Delete the PDF file
    if os.path.exists(textbook.file_path):
        try:
            os.remove(textbook.file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {textbook.file_path}: {e}")
    
    # Delete chapter PDFs
    for chapter in textbook.chapters:
        if chapter.pdf_path and os.path.exists(chapter.pdf_path):
            try:
                os.remove(chapter.pdf_path)
            except Exception as e:
                print(f"Warning: Could not delete chapter file {chapter.pdf_path}: {e}")
    
    # Delete from database (cascades to chapters, worksheets, lesson plans)
    db.delete(textbook)
    db.commit()
    
    return MessageResponse(
        message=f"Textbook '{textbook.title}' and all associated data deleted successfully"
    )

@router.get("/{textbook_id}/pdf")
def get_textbook_pdf(
    textbook_id: int,
    download: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get the PDF file for viewing/downloading.
    
    - **textbook_id**: ID of the textbook
    - **download**: If true, force download. If false, display inline
    """
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    if not os.path.exists(textbook.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Use 'attachment' for download, 'inline' for viewing
    disposition_type = "attachment" if download else "inline"
    
    return FileResponse(
        path=textbook.file_path,
        media_type="application/pdf",
        filename=textbook.original_filename,
        headers={
            "Content-Disposition": f'{disposition_type}; filename="{textbook.original_filename}"',
            "Content-Type": "application/pdf",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.get("/{textbook_id}/preview")
def preview_textbook_pages(
    textbook_id: int,
    start_page: int = 1,
    end_page: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get specific pages from a textbook for preview.
    
    - **textbook_id**: ID of the textbook
    - **start_page**: Starting page number
    - **end_page**: Ending page number (optional)
    """
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    if not os.path.exists(textbook.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    try:
        pdf_service = PDFService()
        # Extract the actual PDF pages
        pdf_bytes = pdf_service.extract_pages_as_pdf(
            textbook.file_path, 
            start_page, 
            end_page or start_page
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="preview_pages_{start_page}_{end_page or start_page}.pdf"',
                "Content-Type": "application/pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))