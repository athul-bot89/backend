"""
Study schedule API endpoints.
Handles creation and management of study schedules for chapters.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
import logging

from app.database.database import get_db
from app.database.models import Chapter, Textbook
from app.models.schemas import (
    StudyScheduleRequest,
    StudyScheduleResponse,
    ScheduledChapter,
    ErrorResponse
)
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/schedule",
    tags=["Schedule"]
)

def calculate_study_plan(
    chapters: List[dict],
    start_date: datetime,
    study_hours_per_day: float,
    include_weekends: bool,
    break_days: List[datetime] = None
) -> List[ScheduledChapter]:
    """
    Calculate optimal study plan for given chapters.
    
    Args:
        chapters: List of chapters with their details
        start_date: Start date for the schedule
        study_hours_per_day: Available study hours per day
        include_weekends: Whether to include weekends
        break_days: List of dates to skip
        
    Returns:
        List of scheduled chapters with study plan
    """
    scheduled_chapters = []
    current_date = start_date
    break_days = break_days or []
    
    # Sort chapters by target completion date and priority
    priority_weights = {"high": 0, "medium": 1, "low": 2}
    sorted_chapters = sorted(
        chapters,
        key=lambda x: (
            x["target_completion_date"],
            priority_weights.get(x.get("priority", "medium"), 1)
        )
    )
    
    for chapter in sorted_chapters:
        # Calculate estimated study days based on estimated hours
        estimated_hours = chapter.get("estimated_hours", study_hours_per_day * 2)
        estimated_study_days = max(1, int(estimated_hours / study_hours_per_day))
        
        # Find next available study date
        suggested_start = current_date
        days_counted = 0
        temp_date = suggested_start
        
        while days_counted < estimated_study_days:
            # Skip break days
            if temp_date.date() in [bd.date() if hasattr(bd, 'date') else bd for bd in break_days]:
                temp_date += timedelta(days=1)
                continue
            
            # Skip weekends if not included
            if not include_weekends and temp_date.weekday() in [5, 6]:
                temp_date += timedelta(days=1)
                continue
            
            days_counted += 1
            if days_counted < estimated_study_days:
                temp_date += timedelta(days=1)
        
        # Create scheduled chapter
        scheduled_chapter = ScheduledChapter(
            chapter_name=chapter["chapter_name"],
            chapter_id=chapter.get("chapter_id"),
            target_completion_date=chapter["target_completion_date"],
            suggested_start_date=suggested_start,
            estimated_study_days=estimated_study_days,
            daily_hours=min(study_hours_per_day, estimated_hours / estimated_study_days),
            priority=chapter.get("priority", "medium"),
            study_tips=None  # Will be populated by AI service if needed
        )
        
        scheduled_chapters.append(scheduled_chapter)
        
        # Move to next chapter start date
        current_date = temp_date + timedelta(days=1)
    
    return scheduled_chapters

def create_weekly_breakdown(scheduled_chapters: List[ScheduledChapter]) -> Dict[str, List[str]]:
    """
    Create a weekly breakdown of the study schedule.
    
    Args:
        scheduled_chapters: List of scheduled chapters
        
    Returns:
        Dictionary with week numbers and chapters to study
    """
    weekly_breakdown = {}
    
    for chapter in scheduled_chapters:
        # Calculate week number from start date
        week_start = chapter.suggested_start_date
        week_num = week_start.isocalendar()[1]
        week_key = f"Week {week_num} ({week_start.strftime('%b %d')})"
        
        if week_key not in weekly_breakdown:
            weekly_breakdown[week_key] = []
        
        weekly_breakdown[week_key].append(chapter.chapter_name)
    
    return weekly_breakdown

def check_conflicts(scheduled_chapters: List[ScheduledChapter]) -> List[str]:
    """
    Check for scheduling conflicts or warnings.
    
    Args:
        scheduled_chapters: List of scheduled chapters
        
    Returns:
        List of conflict warnings
    """
    conflicts = []
    
    for i, chapter in enumerate(scheduled_chapters):
        # Check if suggested start is after target completion
        if chapter.suggested_start_date > chapter.target_completion_date:
            conflicts.append(
                f"⚠️ '{chapter.chapter_name}' cannot be completed by target date "
                f"({chapter.target_completion_date.strftime('%Y-%m-%d')})"
            )
        
        # Check for overlapping high-priority chapters
        if chapter.priority == "high":
            for j, other in enumerate(scheduled_chapters):
                if i != j and other.priority == "high":
                    if (
                        chapter.suggested_start_date <= other.suggested_start_date <= 
                        (chapter.suggested_start_date + timedelta(days=chapter.estimated_study_days))
                    ):
                        conflicts.append(
                            f"⚠️ High priority chapters '{chapter.chapter_name}' and "
                            f"'{other.chapter_name}' have overlapping study periods"
                        )
    
    return conflicts

@router.post("/create", response_model=StudyScheduleResponse)
async def create_study_schedule(
    request: StudyScheduleRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends()
):
    """
    Create a study schedule for given chapters.
    
    This endpoint accepts a list of chapters with their target completion dates
    and generates an optimized study schedule considering available study hours,
    weekends, and break days.
    """
    try:
        # Validate textbook if provided
        if request.textbook_id:
            textbook = db.query(Textbook).filter(Textbook.id == request.textbook_id).first()
            if not textbook:
                raise HTTPException(status_code=404, detail=f"Textbook with ID {request.textbook_id} not found")
        
        # Prepare chapters data
        chapters_data = []
        for chapter_item in request.chapters:
            chapter_dict = {
                "chapter_name": chapter_item.chapter_name,
                "chapter_id": chapter_item.chapter_id,
                "target_completion_date": chapter_item.target_completion_date,
                "estimated_hours": chapter_item.estimated_hours or (request.study_hours_per_day * 2),
                "priority": chapter_item.priority or "medium"
            }
            
            # If chapter_id is provided, validate it exists
            if chapter_item.chapter_id:
                chapter = db.query(Chapter).filter(Chapter.id == chapter_item.chapter_id).first()
                if not chapter:
                    logger.warning(f"Chapter with ID {chapter_item.chapter_id} not found")
                else:
                    # Use actual chapter data if available
                    chapter_dict["chapter_name"] = chapter.title
            
            chapters_data.append(chapter_dict)
        
        # Set start date
        start_date = request.start_date or datetime.now()
        
        # Calculate study plan
        scheduled_chapters = calculate_study_plan(
            chapters=chapters_data,
            start_date=start_date,
            study_hours_per_day=request.study_hours_per_day,
            include_weekends=request.include_weekends,
            break_days=request.break_days
        )
        
        # Generate AI-powered study tips for high-priority chapters
        for scheduled_chapter in scheduled_chapters:
            if scheduled_chapter.priority == "high":
                try:
                    # Generate study tips using AI service
                    tips_prompt = f"Generate 3 brief study tips for learning a chapter titled '{scheduled_chapter.chapter_name}'"
                    tips_response = await ai_service.generate_completion(tips_prompt, max_tokens=150)
                    
                    # Parse tips from response
                    tips = [tip.strip() for tip in tips_response.split('\n') if tip.strip()][:3]
                    scheduled_chapter.study_tips = tips
                except Exception as e:
                    logger.error(f"Failed to generate study tips: {str(e)}")
        
        # Create weekly breakdown
        weekly_breakdown = create_weekly_breakdown(scheduled_chapters)
        
        # Check for conflicts
        conflicts = check_conflicts(scheduled_chapters)
        
        # Generate overall recommendations
        recommendations = []
        
        # Add recommendations based on schedule analysis
        total_chapters = len(scheduled_chapters)
        high_priority_count = sum(1 for ch in scheduled_chapters if ch.priority == "high")
        
        if high_priority_count > total_chapters * 0.5:
            recommendations.append("📚 Many high-priority chapters detected. Consider increasing daily study hours.")
        
        if not request.include_weekends:
            recommendations.append("🗓️ Weekends excluded from schedule. Consider using them for review sessions.")
        
        if conflicts:
            recommendations.append("⏰ Schedule conflicts detected. Consider adjusting target dates or study hours.")
        
        # Calculate total study days
        total_study_days = sum(ch.estimated_study_days for ch in scheduled_chapters)
        
        # Calculate end date
        end_date = max(ch.suggested_start_date + timedelta(days=ch.estimated_study_days) 
                      for ch in scheduled_chapters)
        
        # Create response
        response = StudyScheduleResponse(
            textbook_id=request.textbook_id,
            total_chapters=total_chapters,
            start_date=start_date,
            end_date=end_date,
            total_study_days=total_study_days,
            schedule=scheduled_chapters,
            weekly_breakdown=weekly_breakdown,
            conflicts=conflicts if conflicts else None,
            recommendations=recommendations if recommendations else None
        )
        
        logger.info(f"Created study schedule with {total_chapters} chapters")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating study schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create study schedule: {str(e)}")

@router.post("/optimize/{textbook_id}", response_model=StudyScheduleResponse)
async def optimize_existing_schedule(
    textbook_id: int,
    target_completion_date: datetime,
    study_hours_per_day: float = 2.0,
    include_weekends: bool = True,
    db: Session = Depends(get_db)
):
    """
    Create an optimized study schedule for all chapters in an existing textbook.
    
    This endpoint automatically fetches all chapters from the textbook and creates
    an evenly distributed study schedule to complete by the target date.
    """
    try:
        # Get textbook and its chapters
        textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
        if not textbook:
            raise HTTPException(status_code=404, detail=f"Textbook with ID {textbook_id} not found")
        
        chapters = db.query(Chapter).filter(Chapter.textbook_id == textbook_id).order_by(Chapter.chapter_number).all()
        if not chapters:
            raise HTTPException(status_code=404, detail=f"No chapters found for textbook {textbook_id}")
        
        # Calculate time distribution
        start_date = datetime.now()
        total_days = (target_completion_date - start_date).days
        days_per_chapter = max(1, total_days // len(chapters))
        
        # Create chapter schedule items
        chapters_data = []
        current_target_date = start_date
        
        for chapter in chapters:
            current_target_date += timedelta(days=days_per_chapter)
            
            # Estimate study hours based on page count
            page_count = chapter.end_page - chapter.start_page + 1
            estimated_hours = max(1, page_count * 0.2)  # Rough estimate: 0.2 hours per page
            
            # Determine priority based on chapter position
            if chapter.chapter_number <= 3:
                priority = "high"  # Early chapters are often foundational
            elif chapter.chapter_number >= len(chapters) - 2:
                priority = "high"  # Final chapters might be comprehensive
            else:
                priority = "medium"
            
            chapters_data.append({
                "chapter_name": chapter.title,
                "chapter_id": chapter.id,
                "target_completion_date": min(current_target_date, target_completion_date),
                "estimated_hours": estimated_hours,
                "priority": priority
            })
        
        # Calculate study plan
        scheduled_chapters = calculate_study_plan(
            chapters=chapters_data,
            start_date=start_date,
            study_hours_per_day=study_hours_per_day,
            include_weekends=include_weekends,
            break_days=[]
        )
        
        # Create weekly breakdown
        weekly_breakdown = create_weekly_breakdown(scheduled_chapters)
        
        # Check for conflicts
        conflicts = check_conflicts(scheduled_chapters)
        
        # Generate recommendations
        recommendations = [
            f"📖 Study schedule created for '{textbook.title}' with {len(chapters)} chapters",
            f"⏱️ Allocate {study_hours_per_day} hours daily for optimal progress",
            "📝 Take notes and create summaries after each chapter for better retention"
        ]
        
        # Calculate total study days
        total_study_days = sum(ch.estimated_study_days for ch in scheduled_chapters)
        
        # Calculate actual end date
        end_date = max(ch.suggested_start_date + timedelta(days=ch.estimated_study_days) 
                      for ch in scheduled_chapters)
        
        # Create response
        response = StudyScheduleResponse(
            textbook_id=textbook_id,
            total_chapters=len(chapters),
            start_date=start_date,
            end_date=end_date,
            total_study_days=total_study_days,
            schedule=scheduled_chapters,
            weekly_breakdown=weekly_breakdown,
            conflicts=conflicts if conflicts else None,
            recommendations=recommendations
        )
        
        logger.info(f"Created optimized schedule for textbook {textbook_id} with {len(chapters)} chapters")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating optimized schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create optimized schedule: {str(e)}")