"""
Pydantic schemas for request/response models.
These define the structure of data sent to and from the API.
"""

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Dict
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
    end_page: int = Field(..., ge=0, description="Ending page number (0 means auto-detect)")

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
    processing_status: Optional[str] = Field(default="pending", description="Processing status: pending, processing, pdf_ready, completed, failed")
    processing_error: Optional[str] = None
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
    ocr_language: Optional[str] = Field(
        default="eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori",
        description="OCR language(s). Use + to combine multiple languages (e.g., 'eng+hin+tam'). "
                   "Supported: eng (English), hin (Hindi), tam (Tamil), tel (Telugu), "
                   "kan (Kannada), mal (Malayalam), mar (Marathi), guj (Gujarati), "
                   "ben (Bengali), pan (Punjabi), ori (Odia)"
    )
    ocr_enabled: Optional[bool] = Field(
        default=True,
        description="Enable OCR for image-based PDFs"
    )

class TextExtractionResponse(BaseModel):
    """Schema for text extraction response."""
    extracted_text: str = Field(..., description="Extracted text content")
    page_count: int = Field(..., description="Number of pages extracted")
    start_page: int
    end_page: int

# Chapter detection schemas
class DetectedChapter(BaseModel):
    """Schema for AI-detected chapter."""
    title: str
    chapter_number: int
    start_page: int = Field(default=0, description="Starting page number")
    end_page: int = Field(default=0, description="Ending page number")

class ChapterDetectionRequest(BaseModel):
    """Schema for requesting chapter detection."""
    textbook_id: int = Field(..., description="ID of the textbook")
    toc_text: Optional[str] = Field(None, description="Optional: provide TOC text directly")

class ChapterDetectionResponse(BaseModel):
    """Schema for chapter detection response."""
    textbook_id: int = Field(..., description="ID of the textbook")
    chapters: List[DetectedChapter]
    
    class Config:
        from_attributes = True

# Batch chapter creation
class ChapterBatchCreate(BaseModel):
    """Schema for creating multiple chapters at once."""
    textbook_id: int
    chapters: List[ChapterBase]

class ChapterBatchResponse(BaseModel):
    """Response for batch chapter creation."""
    created_count: int
    chapters: List[ChapterResponse]
    message: Optional[str] = None

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

# Worksheet generation
class WorksheetQuestion(BaseModel):
    """Schema for a single worksheet question."""
    question: str = Field(..., description="The question text")
    question_type: str = Field(..., description="Type of question (multiple_choice, true_false, short_answer, essay)")
    options: Optional[List[str]] = Field(None, description="Options for multiple choice questions")
    correct_answer: Optional[str] = Field(None, description="Correct answer or answer key")
    difficulty: str = Field(default="medium", description="Difficulty level (easy, medium, hard)")

class WorksheetResponse(BaseModel):
    """Schema for worksheet generation response."""
    chapter_id: int
    chapter_title: str
    total_questions: int
    questions: List[WorksheetQuestion]
    generated_at: datetime = Field(default_factory=datetime.now)

# Chapter Q&A / Chat
class ChapterQuestionRequest(BaseModel):
    """Schema for asking a question about a chapter."""
    question: str = Field(..., description="The question or doubt about the chapter")
    include_context: bool = Field(default=True, description="Whether to include chapter context in the answer")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation for context")

class ChapterAnswerResponse(BaseModel):
    """Schema for chapter Q&A response."""
    chapter_id: int
    chapter_title: str
    question: str
    answer: str
    related_concepts: Optional[List[str]] = Field(None, description="Related concepts from the chapter")
    confidence_score: Optional[float] = Field(None, description="Confidence score of the answer (0-1)")
    timestamp: datetime = Field(default_factory=datetime.now)

# Generic message response
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True

# Schedule schemas
class ChapterScheduleItem(BaseModel):
    """Schema for a single chapter in the study schedule."""
    chapter_name: str = Field(..., description="Name of the chapter")
    chapter_id: Optional[int] = Field(None, description="Optional chapter ID if referring to existing chapter")
    target_completion_date: datetime = Field(..., description="Target date to complete this chapter")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours needed to complete")
    priority: Optional[str] = Field(default="medium", description="Priority level (low, medium, high)")

class StudyScheduleRequest(BaseModel):
    """Schema for requesting a study schedule."""
    textbook_id: Optional[int] = Field(None, description="Optional textbook ID if scheduling for existing textbook")
    chapters: List[ChapterScheduleItem] = Field(..., description="List of chapters with their target dates")
    start_date: Optional[datetime] = Field(None, description="Start date for the schedule (defaults to today)")
    study_hours_per_day: float = Field(default=2.0, description="Available study hours per day")
    include_weekends: bool = Field(default=True, description="Whether to include weekends in schedule")
    break_days: Optional[List[datetime]] = Field(None, description="List of dates to skip (holidays, etc.)")

class ScheduledChapter(BaseModel):
    """Schema for a scheduled chapter with calculated study plan."""
    chapter_name: str
    chapter_id: Optional[int]
    target_completion_date: datetime
    suggested_start_date: datetime
    estimated_study_days: int
    daily_hours: float
    priority: str
    study_tips: Optional[List[str]] = Field(None, description="AI-generated study tips for this chapter")

class StudyScheduleResponse(BaseModel):
    """Schema for study schedule response."""
    textbook_id: Optional[int]
    total_chapters: int
    start_date: datetime
    end_date: datetime
    total_study_days: int
    schedule: List[ScheduledChapter]
    weekly_breakdown: Optional[Dict[str, List[str]]] = Field(None, description="Weekly breakdown of chapters")
    conflicts: Optional[List[str]] = Field(None, description="Any scheduling conflicts or warnings")
    recommendations: Optional[List[str]] = Field(None, description="AI-generated study recommendations")
    created_at: datetime = Field(default_factory=datetime.now)