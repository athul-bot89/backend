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
    
    def detect_chapters_from_toc(self, toc_text: str) -> Dict[str, List[Dict]]:
        """
        Analyze table of contents text and detect chapter names.
        
        Args:
            toc_text: Extracted text from table of contents pages
            
        Returns:
            Dictionary with 'chapters' key containing list of chapter information
        """
        try:
            # Create a prompt for chapter detection
            prompt = """
            IMPORTANT: Detect the language of the input text and respond with chapter titles in the SAME language.
            CRITICAL SPELLING ACCURACY: Ensure all chapter titles have CORRECT SPELLING in the detected language. 
            - For non-English languages, pay special attention to diacritical marks, accents, and special characters
            - Preserve exact spelling from the source text, including language-specific characters
            - Do NOT translate or anglicize any terms
            
            Analyze the following table of contents text and extract all chapter titles.
            Return ONLY a JSON object with the following EXACT structure:
            {
                "chapters": [
                    {
                        "title": "Chapter Title Here",
                        "chapter_number": 1,
                        "start_page": 10,
                        "end_page": 25
                    }
                ]
            }
            
            Rules:
            1. Include only main chapters, not subsections
            2. Number chapters sequentially starting from 1
            3. Clean up the titles (remove page numbers, dots, etc.)
            4. If you can detect the starting page number from the TOC, use it as start_page
            5. Estimate end_page as the page before the next chapter starts (or use 0 if unknown)
            6. Use 0 for start_page and end_page if page numbers cannot be determined
            7. The response MUST be a JSON object with a "chapters" array, not just an array
            8. CRITICAL: Keep chapter titles in the SAME LANGUAGE as the source text with PERFECT SPELLING
            9. IMPORTANT: Maintain all language-specific characters, accents, and diacritical marks exactly as they appear
            
            Table of Contents Text:
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from text. Always return valid JSON in the exact format requested. IMPORTANT: Always respond in the SAME LANGUAGE as the input text with CORRECT SPELLING, including all diacritical marks, accents, and special characters."},
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
            
            result = json.loads(result_text)
            
            # Ensure the response has the correct structure
            if isinstance(result, list):
                # If AI returns just an array, wrap it in the expected format
                result = {"chapters": result}
            
            # Ensure all required fields are present with proper types
            for chapter in result.get("chapters", []):
                if "title" not in chapter:
                    chapter["title"] = "Untitled Chapter"
                if "chapter_number" not in chapter:
                    chapter["chapter_number"] = 0
                if "start_page" not in chapter:
                    chapter["start_page"] = 0
                if "end_page" not in chapter:
                    chapter["end_page"] = 0
                
                # Ensure proper types
                chapter["chapter_number"] = int(chapter.get("chapter_number", 0))
                chapter["start_page"] = int(chapter.get("start_page", 0))
                chapter["end_page"] = int(chapter.get("end_page", 0))
            
            return result
        
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            # Return a basic structure if AI fails to provide proper JSON
            return {
                "chapters": [
                    {
                        "title": "Unable to parse chapters",
                        "chapter_number": 1,
                        "start_page": 0,
                        "end_page": 0
                    }
                ]
            }
        
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
            IMPORTANT: Detect the language of the chapter text and provide your summary in the SAME LANGUAGE.
            CRITICAL SPELLING: Ensure PERFECT SPELLING in the detected language, including:
            - All diacritical marks, accents, and special characters
            - Language-specific letter combinations and spelling rules
            - Proper capitalization according to the language's conventions
            
            Create a comprehensive summary of the following chapter titled "{chapter_title}".
            
            The summary should:
            1. Be 200-300 words
            2. Capture the main concepts and key points
            3. Be written in clear, educational language
            4. Include the most important examples or applications mentioned
            5. MUST be written in the SAME LANGUAGE as the chapter text with CORRECT SPELLING
            6. CRITICAL: Use ONLY plain text - do NOT use any markdown formatting like **, ##, *, -, backticks, or other special characters for formatting
            7. Write in simple paragraphs without any bold, italic, or heading markers
            
            Chapter text:
            {chapter_text[:4000]}  # Limit text to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a multilingual educational content specialist creating summaries for teaching purposes. ALWAYS provide summaries in the SAME LANGUAGE as the input text with PERFECT SPELLING, including all diacritical marks and special characters. IMPORTANT: Generate ONLY plain text without any markdown formatting symbols."},
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
            IMPORTANT: Detect the language of the chapter text and provide concepts in the SAME LANGUAGE.
            CRITICAL SPELLING: Ensure all concepts have CORRECT SPELLING in the detected language:
            - Preserve all diacritical marks, accents, and special characters
            - Use proper spelling according to the language's rules
            - Do NOT anglicize or simplify terms
            
            Extract the 5-10 most important key concepts or terms from this chapter.
            Return ONLY a JSON array of strings, each being a key concept.
            
            Example format: ["concept 1", "concept 2", "concept 3"]
            
            Note: Keep all concepts in the SAME LANGUAGE as the source text with PERFECT SPELLING.
            CRITICAL: Use plain text only - do NOT include any markdown formatting like **, ##, *, or special characters in the concepts.
            
            Chapter text:
            {chapter_text[:3000]}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a multilingual educational expert identifying key learning concepts. ALWAYS extract concepts in the SAME LANGUAGE as the input text with CORRECT SPELLING, preserving all diacritical marks and special characters. Return plain text concepts without any formatting symbols."},
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
    
    def generate_worksheet_questions(self, chapter_text: str, chapter_title: str, num_questions: int = 10) -> List[Dict]:
        """
        Generate worksheet questions from chapter text.
        
        Args:
            chapter_text: Full text content of the chapter
            chapter_title: Title of the chapter
            num_questions: Number of questions to generate (default 10)
            
        Returns:
            List of question dictionaries
        """
        try:
            prompt = f"""
            IMPORTANT: Detect the language of the chapter text and create ALL questions, options, and answers in the SAME LANGUAGE.
            CRITICAL SPELLING ACCURACY: Ensure PERFECT SPELLING throughout:
            - All questions, options, and answers must have correct spelling in the detected language
            - Preserve all diacritical marks, accents, and language-specific characters
            - Follow proper spelling and grammar rules of the detected language
            - Do NOT translate or anglicize any terms
            
            Create a worksheet with {num_questions} questions based on the chapter titled "{chapter_title}".
            
            CRITICAL FORMATTING RULE: Use ONLY plain text in all questions, options, and answers. Do NOT use any markdown formatting like **, ##, *, -, backticks, or other special characters for emphasis or formatting.
            
            Generate a mix of question types:
            - Multiple choice questions (4 options each)
            - True/False questions
            - Short answer questions
            - Essay/long answer questions (1-2 only)
            
            Return ONLY a JSON array with questions in this EXACT format:
            [
                {{
                    "question": "Question text here",
                    "question_type": "multiple_choice",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "difficulty": "medium"
                }},
                {{
                    "question": "True or False: Statement here",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "difficulty": "easy"
                }},
                {{
                    "question": "Short answer question here",
                    "question_type": "short_answer",
                    "options": null,
                    "correct_answer": "Expected answer or key points",
                    "difficulty": "medium"
                }},
                {{
                    "question": "Essay question here",
                    "question_type": "essay",
                    "options": null,
                    "correct_answer": "Key points to cover in the answer",
                    "difficulty": "hard"
                }}
            ]
            
            Rules:
            1. Questions should test understanding of key concepts
            2. Include a variety of difficulty levels
            3. Make questions clear and unambiguous
            4. For multiple choice, make all options plausible
            5. Base all questions on the actual content provided
            6. CRITICAL: ALL questions, options, and answers MUST be in the SAME LANGUAGE as the chapter text with PERFECT SPELLING
            7. IMPORTANT: Use only plain text - absolutely NO markdown formatting symbols (no **, ##, *, -, or backticks)
            8. ESSENTIAL: Maintain correct spelling with all language-specific characters and diacritical marks
            
            Chapter text:
            {chapter_text[:4000]}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a multilingual educational assessment expert creating comprehensive worksheets for students. ALWAYS create questions and answers in the SAME LANGUAGE as the input text with PERFECT SPELLING, including all diacritical marks and special characters. IMPORTANT: Generate plain text only - do NOT use any markdown formatting symbols in your output."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,  # Slightly higher for variety in questions
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up the response if needed
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            questions = json.loads(result_text)
            
            # Ensure all questions have required fields
            for q in questions:
                if "question" not in q:
                    q["question"] = "Question text missing"
                if "question_type" not in q:
                    q["question_type"] = "short_answer"
                if "difficulty" not in q:
                    q["difficulty"] = "medium"
                if "options" not in q:
                    q["options"] = None
                if "correct_answer" not in q:
                    q["correct_answer"] = None
            
            return questions
        
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            # Return a basic set of questions if AI fails
            return [
                {
                    "question": "What are the main concepts covered in this chapter?",
                    "question_type": "essay",
                    "options": None,
                    "correct_answer": "Key concepts should be listed and explained",
                    "difficulty": "medium"
                }
            ]
        
        except Exception as e:
            print(f"Error generating worksheet: {e}")
            raise Exception(f"Failed to generate worksheet: {str(e)}")
    
    def answer_chapter_question(self, chapter_text: str, chapter_title: str, question: str, 
                               conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict:
        """
        Answer a question about a specific chapter.
        
        Args:
            chapter_text: Full text content of the chapter
            chapter_title: Title of the chapter
            question: User's question about the chapter
            conversation_history: Optional previous Q&A for context
            
        Returns:
            Dictionary containing answer and related information
        """
        try:
            # Build conversation context
            messages = [
                {"role": "system", "content": f"""You are a multilingual intelligent teaching assistant helping students understand the chapter '{chapter_title}'. 
                Answer questions based on the chapter content provided. Be helpful, accurate, and educational.
                If the question is not clearly answered in the chapter, acknowledge this and provide the best possible guidance.
                Keep answers concise but comprehensive.
                CRITICAL: ALWAYS detect the language of the student's question and provide your ENTIRE response in the SAME LANGUAGE with PERFECT SPELLING.
                SPELLING ACCURACY: Ensure correct spelling including all diacritical marks, accents, and language-specific characters.
                IMPORTANT: Use ONLY plain text in your responses. Do NOT use any markdown formatting like **, ##, *, -, backticks, or other special characters for emphasis or formatting."""}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for entry in conversation_history[-5:]:  # Limit to last 5 exchanges for context
                    if "question" in entry:
                        messages.append({"role": "user", "content": entry["question"]})
                    if "answer" in entry:
                        messages.append({"role": "assistant", "content": entry["answer"]})
            
            # Add current context and question
            prompt = f"""
            IMPORTANT: Respond in the SAME LANGUAGE as the student's question.
            CRITICAL SPELLING: Ensure PERFECT SPELLING in your response:
            - Use correct spelling with all diacritical marks and accents
            - Follow the spelling conventions of the detected language
            - Preserve language-specific characters exactly
            
            Based on the following chapter content, please answer the student's question.
            
            Chapter Title: {chapter_title}
            
            Chapter Content:
            {chapter_text[:4000]}  # Limit to manage token count
            
            Student's Question: {question}
            
            Please provide:
            1. A clear and helpful answer to the question
            2. Any relevant examples from the chapter if applicable
            3. Related concepts that might help understanding
            4. Your ENTIRE response MUST be in the SAME LANGUAGE as the question with CORRECT SPELLING
            5. CRITICAL: Use ONLY plain text - do NOT use markdown formatting (no **, ##, *, -, backticks, etc.)
            """
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,  # Balanced for informative yet natural responses
                max_tokens=800
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Extract related concepts (optional enhancement)
            related_concepts = self._extract_related_concepts(chapter_text, question)
            
            return {
                "answer": answer_text,
                "related_concepts": related_concepts,
                "confidence_score": 0.85  # You could implement a more sophisticated scoring system
            }
        
        except Exception as e:
            print(f"Error answering question: {e}")
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def _extract_related_concepts(self, chapter_text: str, question: str) -> List[str]:
        """
        Extract concepts related to the question from the chapter.
        
        Args:
            chapter_text: Chapter content
            question: User's question
            
        Returns:
            List of related concepts
        """
        try:
            prompt = f"""
            IMPORTANT: Detect the language of the question and provide concepts in the SAME LANGUAGE.
            CRITICAL SPELLING: Ensure all concepts have CORRECT SPELLING:
            - Preserve all diacritical marks, accents, and special characters
            - Use proper spelling according to the language's conventions
            - Do NOT anglicize or simplify terms
            
            Based on this question: "{question}"
            
            Extract 3-5 related key concepts or terms from the chapter that are relevant to understanding the answer.
            Return ONLY a JSON array of strings.
            
            Note: Keep all concepts in the SAME LANGUAGE as the question with PERFECT SPELLING.
            CRITICAL: Use plain text only - do NOT include any markdown formatting symbols in the concepts.
            
            Chapter excerpt:
            {chapter_text[:2000]}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a multilingual expert at identifying related educational concepts. ALWAYS provide concepts in the SAME LANGUAGE as the input question with CORRECT SPELLING, preserving all diacritical marks and special characters. Return plain text concepts without any formatting symbols."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean and parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            concepts = json.loads(result_text)
            return concepts if isinstance(concepts, list) else []
        
        except Exception as e:
            print(f"Error extracting related concepts: {e}")
            return []  # Return empty list if extraction fails