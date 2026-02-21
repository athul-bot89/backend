"""
AI service for OpenAI API integration.
Handles chapter detection and content generation.
"""

from openai import OpenAI, AzureOpenAI
from typing import List, Dict, Optional
import json
from app.config import settings

class AIService:
    """Service for AI-powered operations using OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI client (Azure or standard)."""
        if settings.use_azure_openai:
            # Use Azure OpenAI
            if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
                raise ValueError("Azure OpenAI credentials not found. Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env file")
            
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
            self.model_name = settings.azure_openai_deployment
        else:
            # Use standard OpenAI
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file")
            
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model_name = "gpt-3.5-turbo"
    
    def detect_chapters_from_toc(self, toc_text: str) -> List[Dict[str, str]]:
        """
        Analyze table of contents text and detect chapter names.
        
        Args:
            toc_text: Extracted text from table of contents pages
            
        Returns:
            List of dictionaries containing chapter information
        """
        try:
            # Create a prompt for chapter detection
            prompt = """
            Analyze the following table of contents text and extract all chapter titles.
            Return ONLY a JSON array of chapter objects with the following structure:
            [
                {
                    "chapter_number": 1,
                    "title": "Chapter Title Here",
                    "detected_page": "page number if visible in TOC, otherwise null"
                }
            ]
            
            Rules:
            1. Include only main chapters, not subsections
            2. Number chapters sequentially starting from 1
            3. Clean up the titles (remove page numbers, dots, etc.)
            4. If you can detect page numbers from the TOC, include them
            
            Table of Contents Text:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from text."},
                    {"role": "user", "content": prompt + toc_text}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            # Sometimes the model might include markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            chapters = json.loads(result_text)
            
            return chapters
        
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            # Return a basic structure if AI fails to provide proper JSON
            return [{"chapter_number": 1, "title": "Unable to parse chapters", "detected_page": None}]
        
        except Exception as e:
            print(f"Error detecting chapters: {e}")
            raise Exception(f"Failed to detect chapters: {str(e)}")
    
    def generate_chapter_summary(self, chapter_text: str, chapter_title: str) -> str:
        """
        Generate a summary for a chapter.
        
        Args:
            chapter_text: Full text content of the chapter
            chapter_title: Title of the chapter
            
        Returns:
            Generated summary as a string
        """
        try:
            prompt = f"""
            Create a comprehensive summary of the following chapter titled "{chapter_title}".
            
            The summary should:
            1. Be 200-300 words
            2. Capture the main concepts and key points
            3. Be written in clear, educational language
            4. Include the most important examples or applications mentioned
            
            Chapter text:
            {chapter_text[:4000]}  # Limit text to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an educational content specialist creating summaries for teaching purposes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def extract_key_concepts(self, chapter_text: str) -> List[str]:
        """
        Extract key concepts from chapter text.
        
        Args:
            chapter_text: Full text content of the chapter
            
        Returns:
            List of key concepts
        """
        try:
            prompt = f"""
            Extract the 5-10 most important key concepts or terms from this chapter.
            Return ONLY a JSON array of strings, each being a key concept.
            
            Example format: ["concept 1", "concept 2", "concept 3"]
            
            Chapter text:
            {chapter_text[:3000]}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an educational expert identifying key learning concepts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up the response if needed
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            concepts = json.loads(result_text)
            return concepts
        
        except Exception as e:
            print(f"Error extracting key concepts: {e}")
            return []  # Return empty list if extraction fails