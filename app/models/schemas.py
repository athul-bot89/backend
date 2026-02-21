"""
Pydantic schemas for request/response models.
These define the structure of data sent to and from the API.
"""

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional
from datetime import datetime

# Textbook schemas
class TextbookBase(BaseModel):
    """Base schema for textbook data."""
    title: str = Field(..., description="Title of the textbook")
    author: Optional[str] = Field(None, description="Author of the textbook")

class TextbookCreate(TextbookBase):
    """Schema for creating a new textbook."""
    pass

class TextbookUpdate(BaseModel):
    """Schema for updating textbook information."""
    title: Optional[str] = None
    author: Optional[str] = None
    toc_start_page: Optional[int] = Field(None, ge=1, description="Start page of table of contents")
    toc_end_page: Optional[int] = Field(None, ge=1, description="End page of table of contents")

class TextbookResponse(TextbookBase):
    """Schema for textbook response."""
    id: int
    original_filename: str
    total_pages: Optional[int]
    uploaded_at: datetime
    toc_start_page: Optional[int]
    toc_end_page: Optional[int]
    chapter_count: int = Field(default=0)
    
    class Config:
        from_attributes = True
    
    @computed_field
    @property
    def has_toc_extracted(self) -> bool:
        return self.toc_start_page is not None and self.toc_end_page is not None

# Chapter schemas
class ChapterBase(BaseModel):
    """Base schema for chapter data."""
    title: str = Field(..., description="Title of the chapter")
    chapter_number: int = Field(..., ge=1, description="Chapter number")
    start_page: int = Field(..., ge=1, description="Starting page number")
    end_page: int = Field(..., ge=1, description="Ending page number")

class ChapterCreate(ChapterBase):
    """Schema for creating a new chapter."""
    textbook_id: int = Field(..., description="ID of the parent textbook")

class ChapterUpdate(BaseModel):
    """Schema for updating chapter information."""
    title: Optional[str] = None
    start_page: Optional[int] = Field(None, ge=1)
    end_page: Optional[int] = Field(None, ge=1)

class ChapterResponse(ChapterBase):
    """Schema for chapter response."""
    id: int
    textbook_id: int
    pdf_path: Optional[str] = None
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @computed_field
    @property
    def has_pdf(self) -> bool:
        return bool(self.pdf_path)
    
    @computed_field
    @property
    def has_text(self) -> bool:
        return bool(self.extracted_text)
    
    @computed_field
    @property
    def has_summary(self) -> bool:
        return bool(self.summary)

# Text extraction schemas
class PageRangeRequest(BaseModel):
    """Schema for requesting text from a page range."""
    start_page: int = Field(..., ge=1, description="Starting page number")
    end_page: int = Field(..., ge=1, description="Ending page number")

class TextExtractionResponse(BaseModel):
    """Schema for text extraction response."""
    extracted_text: str = Field(..., description="Extracted text content")
    page_count: int = Field(..., description="Number of pages extracted")
    start_page: int
    end_page: int

# Chapter detection schemas
class DetectedChapter(BaseModel):
    """Schema for AI-detected chapter."""
    chapter_number: int
    title: str
    detected_page: Optional[int] = None

class ChapterDetectionRequest(BaseModel):
    """Schema for requesting chapter detection."""
    textbook_id: int = Field(..., description="ID of the textbook")
    toc_text: Optional[str] = Field(None, description="Optional: provide TOC text directly")

class ChapterDetectionResponse(BaseModel):
    """Schema for chapter detection response."""
    detected_chapters: List[DetectedChapter]
    total_chapters: int

# Batch chapter creation
class ChapterBatchCreate(BaseModel):
    """Schema for creating multiple chapters at once."""
    textbook_id: int
    chapters: List[ChapterBase]

class ChapterBatchResponse(BaseModel):
    """Response for batch chapter creation."""
    created_count: int
    chapters: List[ChapterResponse]

# File upload response
class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    filename: str
    file_path: str
    size_bytes: int
    message: str = "File uploaded successfully"

# Error response
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    status_code: int

# Summary generation
class SummaryRequest(BaseModel):
    """Schema for requesting summary generation."""
    chapter_id: int = Field(..., description="ID of the chapter to summarize")

class SummaryResponse(BaseModel):
    """Schema for summary response."""
    chapter_id: int
    chapter_title: str
    summary: str
    key_concepts: List[str]

# Generic message response
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True