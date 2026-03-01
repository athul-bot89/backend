"""
API endpoints for text extraction from PDFs.
Handles extracting text from specific page ranges.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Textbook
from app.models.schemas import TextExtractionResponse, PageRangeRequest
from app.services.pdf_service import PDFService

# Create router for extraction endpoints
router = APIRouter(prefix="/extract", tags=["extraction"])

@router.post("/textbook/{textbook_id}/pages", response_model=TextExtractionResponse)
def extract_text_from_pages(
    textbook_id: int,
    page_range: PageRangeRequest,
    db: Session = Depends(get_db)
):
    """
    Extract text from specific page range of a textbook.
    
    This is useful for:
    - Extracting table of contents
    - Previewing specific pages
    - Getting text from any page range
    
    - **textbook_id**: ID of the textbook
    - **start_page**: Starting page number (1-based)
    - **end_page**: Ending page number (inclusive)
    """
    
    # Get the textbook
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Validate page range
    if page_range.start_page < 1:
        raise HTTPException(status_code=400, detail="Start page must be at least 1")
    
    if page_range.end_page > textbook.total_pages:
        raise HTTPException(
            status_code=400, 
            detail=f"End page {page_range.end_page} exceeds total pages {textbook.total_pages}"
        )
    
    if page_range.start_page > page_range.end_page:
        raise HTTPException(status_code=400, detail="Start page must be less than or equal to end page")
    
    try:
        # Extract text using PDF service with OCR language support
        pdf_service = PDFService()
        extracted_text = pdf_service.extract_text_from_pages(
            textbook.file_path,
            page_range.start_page,
            page_range.end_page,
            ocr_fallback=page_range.ocr_enabled,
            ocr_language=page_range.ocr_language
        )
        
        return TextExtractionResponse(
            extracted_text=extracted_text,
            page_count=page_range.end_page - page_range.start_page + 1,
            start_page=page_range.start_page,
            end_page=page_range.end_page
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

@router.get("/textbook/{textbook_id}/toc", response_model=TextExtractionResponse)
def get_table_of_contents(
    textbook_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the table of contents text if it has been extracted.
    
    - **textbook_id**: ID of the textbook
    """
    
    # Get the textbook
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Check if TOC has been set
    if not textbook.toc_start_page or not textbook.toc_end_page:
        raise HTTPException(
            status_code=400,
            detail="Table of contents pages not set. Please update textbook with TOC page range first."
        )
    
    # Return cached TOC if available
    if textbook.toc_text:
        return TextExtractionResponse(
            extracted_text=textbook.toc_text,
            page_count=textbook.toc_end_page - textbook.toc_start_page + 1,
            start_page=textbook.toc_start_page,
            end_page=textbook.toc_end_page
        )
    
    # Extract TOC if not cached
    try:
        pdf_service = PDFService()
        toc_text = pdf_service.extract_text_from_pages(
            textbook.file_path,
            textbook.toc_start_page,
            textbook.toc_end_page
        )
        
        # Cache the TOC text
        textbook.toc_text = toc_text
        db.commit()
        
        return TextExtractionResponse(
            extracted_text=toc_text,
            page_count=textbook.toc_end_page - textbook.toc_start_page + 1,
            start_page=textbook.toc_start_page,
            end_page=textbook.toc_end_page
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract TOC: {str(e)}")

@router.post("/textbook/{textbook_id}/set-toc", response_model=TextExtractionResponse)
def set_table_of_contents_pages(
    textbook_id: int,
    page_range: PageRangeRequest,
    db: Session = Depends(get_db)
):
    """
    Set the table of contents page range and extract the text.
    
    This is a convenience endpoint that:
    1. Updates the textbook's TOC page range
    2. Extracts the text from those pages
    3. Caches the TOC text for future use
    
    - **textbook_id**: ID of the textbook
    - **start_page**: Starting page of TOC
    - **end_page**: Ending page of TOC
    """
    
    # Get the textbook
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Validate page range
    if page_range.start_page < 1:
        raise HTTPException(status_code=400, detail="Start page must be at least 1")
    
    if page_range.end_page > textbook.total_pages:
        raise HTTPException(
            status_code=400, 
            detail=f"End page {page_range.end_page} exceeds total pages {textbook.total_pages}"
        )
    
    if page_range.start_page > page_range.end_page:
        raise HTTPException(status_code=400, detail="Start page must be less than or equal to end page")
    
    try:
        # Extract TOC text
        pdf_service = PDFService()
        toc_text = pdf_service.extract_text_from_pages(
            textbook.file_path,
            page_range.start_page,
            page_range.end_page
        )
        
        # Update textbook with TOC information
        textbook.toc_start_page = page_range.start_page
        textbook.toc_end_page = page_range.end_page
        textbook.toc_text = toc_text
        
        db.commit()
        
        return TextExtractionResponse(
            extracted_text=toc_text,
            page_count=page_range.end_page - page_range.start_page + 1,
            start_page=page_range.start_page,
            end_page=page_range.end_page
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set and extract TOC: {str(e)}")