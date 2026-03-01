"""
Test script for the study schedule API endpoint.
Demonstrates how to create and optimize study schedules.
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_create_custom_schedule():
    """
    Test creating a custom study schedule with specific chapters and dates.
    """
    print("\n=== Testing Custom Study Schedule Creation ===")
    
    # Prepare schedule data
    schedule_data = {
        "textbook_id": None,  # Optional, can link to existing textbook
        "chapters": [
            {
                "chapter_name": "Introduction to Python",
                "target_completion_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "estimated_hours": 10,
                "priority": "high"
            },
            {
                "chapter_name": "Data Types and Variables",
                "target_completion_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "estimated_hours": 8,
                "priority": "high"
            },
            {
                "chapter_name": "Control Flow",
                "target_completion_date": (datetime.now() + timedelta(days=21)).isoformat(),
                "estimated_hours": 12,
                "priority": "medium"
            },
            {
                "chapter_name": "Functions and Modules",
                "target_completion_date": (datetime.now() + timedelta(days=28)).isoformat(),
                "estimated_hours": 15,
                "priority": "medium"
            },
            {
                "chapter_name": "Object-Oriented Programming",
                "target_completion_date": (datetime.now() + timedelta(days=35)).isoformat(),
                "estimated_hours": 20,
                "priority": "low"
            }
        ],
        "start_date": datetime.now().isoformat(),
        "study_hours_per_day": 2.5,
        "include_weekends": False,
        "break_days": [
            (datetime.now() + timedelta(days=10)).isoformat(),  # Example break day
            (datetime.now() + timedelta(days=20)).isoformat()   # Another break day
        ]
    }
    
    # Send request
    response = requests.post(f"{BASE_URL}/schedule/create", json=schedule_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Schedule created successfully!")
        print(f"Total chapters: {result['total_chapters']}")
        print(f"Study period: {result['start_date'][:10]} to {result['end_date'][:10]}")
        print(f"Total study days: {result['total_study_days']}")
        
        print("\n📅 Schedule Details:")
        for chapter in result['schedule']:
            print(f"\n  📖 {chapter['chapter_name']}")
            print(f"     Priority: {chapter['priority']}")
            print(f"     Start: {chapter['suggested_start_date'][:10]}")
            print(f"     Target completion: {chapter['target_completion_date'][:10]}")
            print(f"     Study days: {chapter['estimated_study_days']}")
            print(f"     Daily hours: {chapter['daily_hours']:.1f}")
            
            if chapter.get('study_tips'):
                print(f"     Tips: {', '.join(chapter['study_tips'][:2])}")
        
        if result.get('weekly_breakdown'):
            print("\n📊 Weekly Breakdown:")
            for week, chapters in result['weekly_breakdown'].items():
                print(f"  {week}: {', '.join(chapters)}")
        
        if result.get('conflicts'):
            print("\n⚠️ Conflicts/Warnings:")
            for conflict in result['conflicts']:
                print(f"  - {conflict}")
        
        if result.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  - {rec}")
    else:
        print(f"❌ Failed to create schedule: {response.status_code}")
        print(response.json())

def test_optimize_existing_textbook():
    """
    Test optimizing a schedule for an existing textbook.
    """
    print("\n=== Testing Optimized Schedule for Existing Textbook ===")
    
    # First, check if there are any textbooks
    response = requests.get(f"{BASE_URL}/textbooks")
    if response.status_code == 200:
        textbooks = response.json()
        if textbooks:
            textbook_id = textbooks[0]['id']
            print(f"Using textbook ID: {textbook_id} - {textbooks[0]['title']}")
            
            # Create optimized schedule
            target_date = (datetime.now() + timedelta(days=60)).isoformat()
            
            response = requests.post(
                f"{BASE_URL}/schedule/optimize/{textbook_id}",
                params={
                    "target_completion_date": target_date,
                    "study_hours_per_day": 3.0,
                    "include_weekends": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Optimized schedule created!")
                print(f"Total chapters: {result['total_chapters']}")
                print(f"Study period: {result['start_date'][:10]} to {result['end_date'][:10]}")
                print(f"Total study days: {result['total_study_days']}")
                
                # Show first 3 chapters as sample
                print("\n📚 Sample Schedule (first 3 chapters):")
                for chapter in result['schedule'][:3]:
                    print(f"  - {chapter['chapter_name']}: {chapter['suggested_start_date'][:10]} ({chapter['estimated_study_days']} days)")
                
                if result.get('recommendations'):
                    print("\n💡 Recommendations:")
                    for rec in result['recommendations']:
                        print(f"  - {rec}")
            else:
                print(f"❌ Failed to create optimized schedule: {response.status_code}")
                print(response.json())
        else:
            print("No textbooks found. Upload a textbook first to test this feature.")
    else:
        print(f"❌ Failed to fetch textbooks: {response.status_code}")

def test_schedule_with_existing_chapters():
    """
    Test creating a schedule linking to existing chapters in the database.
    """
    print("\n=== Testing Schedule with Existing Chapters ===")
    
    # First, get existing chapters
    response = requests.get(f"{BASE_URL}/textbooks")
    if response.status_code == 200:
        textbooks = response.json()
        if textbooks:
            textbook_id = textbooks[0]['id']
            
            # Get chapters for this textbook
            response = requests.get(f"{BASE_URL}/chapters/textbook/{textbook_id}")
            if response.status_code == 200:
                chapters = response.json()
                if chapters:
                    # Create schedule using first 3 chapters
                    schedule_data = {
                        "textbook_id": textbook_id,
                        "chapters": [
                            {
                                "chapter_name": ch['title'],
                                "chapter_id": ch['id'],
                                "target_completion_date": (datetime.now() + timedelta(days=7*(i+1))).isoformat(),
                                "estimated_hours": 5 + i*2,
                                "priority": "high" if i == 0 else "medium"
                            }
                            for i, ch in enumerate(chapters[:3])
                        ],
                        "study_hours_per_day": 2.0,
                        "include_weekends": True
                    }
                    
                    response = requests.post(f"{BASE_URL}/schedule/create", json=schedule_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Schedule created with existing chapters!")
                        print(f"Textbook ID: {result['textbook_id']}")
                        print(f"Scheduled {len(result['schedule'])} chapters")
                        
                        for chapter in result['schedule']:
                            print(f"  - {chapter['chapter_name']} (ID: {chapter['chapter_id']})")
                    else:
                        print(f"❌ Failed: {response.status_code}")
                        print(response.json())
                else:
                    print("No chapters found for this textbook.")
            else:
                print(f"❌ Failed to fetch chapters: {response.status_code}")
        else:
            print("No textbooks found. Upload a textbook first.")

if __name__ == "__main__":
    print("🎯 Testing Study Schedule API Endpoints")
    print("=" * 50)
    
    # Run tests
    try:
        test_create_custom_schedule()
        test_optimize_existing_textbook()
        test_schedule_with_existing_chapters()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API.")
        print("Make sure the FastAPI server is running (python -m uvicorn app.main:app --reload)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")