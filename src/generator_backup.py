"""
Question Generator Module - Phase 3
Uses Claude API to generate multiple-choice questions from text chunks.
Features robust error handling, retry logic, and comprehensive logging.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime


# Load environment variables
load_dotenv()


# Error log file path
ERROR_LOG_PATH = "output/errors.log"


class QuestionGenerator:
    """
    Generate multiple-choice questions using Claude API.
    Implements robust error handling, retry logic, and comprehensive logging.
    """
    
    # Category weights for Cameroon topic (25% each)
    CAMEROON_CATEGORIES = {
        "Geography": 0.25,
        "History": 0.25,
        "Culture": 0.25,
        "General Knowledge": 0.25
    }
    
    def __init__(self, api_key: str = None, error_log_path: str = ERROR_LOG_PATH):
        """
        Initialize the question generator.
        
        Args:
            api_key: Claude API key (defaults to CLAUDE_API_KEY from .env)
            error_log_path: Path to error log file
        """
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.error_log_path = error_log_path
        self.failed_chunks = []
        self.total_api_calls = 0
        self.successful_calls = 0
        
        # Ensure error log directory exists
        Path(error_log_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _create_prompt(self, text_chunk: str, topic: str, questions_needed: int) -> str:
        """
        Create a structured prompt for Claude API.
        Optimized for reliable JSON output and category balancing.
        
        Args:
            text_chunk: Text to generate questions from
            topic: Topic to focus on
            questions_needed: Number of questions to generate
            
        Returns:
            Formatted prompt string
        """
        category_info = ""
        if topic.lower() == "cameroon":
            category_info = """
IMPORTANT: Distribute questions evenly across these categories:
- Geography: 25% (landmarks, regions, climate, natural resources)
- History: 25% (historical events, independence, colonial period, leaders)
- Culture: 25% (traditions, languages, festivals, food, customs)
- General Knowledge: 25% (economy, politics, sports, notable figures)
"""
        else:
            category_info = f"""
Create questions relevant to {topic}. Choose appropriate categories based on the content.
"""
        
        prompt = f"""From this text, create {questions_needed} factual multiple-choice questions about {topic}.

{category_info}
REQUIREMENTS:
- Each question must have exactly 4 options (A, B, C, D)
- Questions should be clear and unambiguous
- Difficulty should vary (Easy, Medium, Hard)
- Include a brief explanation for each answer

Return ONLY valid JSON with this EXACT schema (no markdown, no code blocks):
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "First option",
      "B": "Second option",
      "C": "Third option",
      "D": "Fourth option"
    }},
    "answer": "B",
    "category": "Category name",
    "difficulty": "Easy",
    "explanation": "Brief explanation"
  }}
]

TEXT:
{text_chunk}

CRITICAL: Return ONLY the JSON array. No additional text, markdown, or formatting."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse Claude's response and extract questions.
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            List of question dictionaries
        """
        try:
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```"):
                # Find the actual JSON content
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            
            # Parse JSON
            questions = json.loads(response_text)
            
            # Validate structure
            if not isinstance(questions, list):
                return []
            
            validated_questions = []
            for q in questions:
                if self._validate_question(q):
                    validated_questions.append(q)
            
            return validated_questions
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return []
        except Exception as e:
            print(f"Error parsing response: {e}")
            return []
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """
        Validate that a question has all required fields.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["question", "options", "answer", "category", "difficulty", "explanation"]
        
        if not all(field in question for field in required_fields):
            return False
        
        # Validate options
        if not isinstance(question["options"], dict):
            return False
        
        required_options = ["A", "B", "C", "D"]
        if not all(opt in question["options"] for opt in required_options):
            return False
        
        # Validate answer is one of the options
        if question["answer"] not in required_options:
            return False
        
        return True
    
    def _log_error(self, error_type: str, chunk_index: int, error_message: str, chunk_preview: str = ""):
        """
        Log errors to the error log file.
        
        Args:
            error_type: Type of error (e.g., "API_ERROR", "JSON_PARSE_ERROR")
            chunk_index: Index of the chunk that failed
            error_message: Error message
            chunk_preview: Preview of the chunk text (first 200 chars)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n[{timestamp}] {error_type}\n"
        log_entry += f"Chunk Index: {chunk_index}\n"
        log_entry += f"Error: {error_message}\n"
        if chunk_preview:
            log_entry += f"Chunk Preview: {chunk_preview[:200]}...\n"
        log_entry += "-" * 70 + "\n"
        
        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to error log: {e}")
    
    def generate_from_chunk(
        self, 
        chunk: str, 
        topic: str, 
        questions_needed: int,
        chunk_index: int = 0,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate questions from a single text chunk with robust error handling.
        Implements retry logic and error logging for failed attempts.
        
        Args:
            chunk: Text chunk to process
            topic: Topic to focus on
            questions_needed: Number of questions to generate
            chunk_index: Index of chunk (for error logging)
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            List of generated questions
        """
        prompt = self._create_prompt(chunk, topic, questions_needed)
        self.total_api_calls += 1
        
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                response_text = response.content[0].text
                questions = self._parse_response(response_text)
                
                if questions:
                    self.successful_calls += 1
                    return questions
                
                # If parsing failed, retry
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except json.JSONDecodeError as e:
                error_msg = f"JSON parsing failed: {str(e)}"
                if attempt == max_retries - 1:
                    self._log_error("JSON_PARSE_ERROR", chunk_index, error_msg, chunk)
                    self.failed_chunks.append(chunk_index)
                else:
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                error_msg = f"API call failed: {str(e)}"
                if attempt == max_retries - 1:
                    self._log_error("API_ERROR", chunk_index, error_msg, chunk)
                    self.failed_chunks.append(chunk_index)
                else:
                    time.sleep(2 ** attempt)
        
        return []
    
    def generate_questions(
        self, 
        chunks: List[str], 
        topic: str, 
        total_questions: int
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generate questions from multiple text chunks with comprehensive statistics.
        Implements rate limiting and error tracking for production use.
        
        Args:
            chunks: List of text chunks
            topic: Topic to focus on
            total_questions: Total number of questions to generate (100-10,000)
            
        Returns:
            Tuple of (questions_list, statistics_dict)
        """
        if not chunks:
            print("[ERROR] No chunks provided")
            return [], {"error": "No chunks provided"}
        
        # Reset statistics
        self.failed_chunks = []
        self.total_api_calls = 0
        self.successful_calls = 0
        start_time = time.time()
        
        all_questions = []
        questions_per_chunk = max(1, total_questions // len(chunks))
        
        print(f"\n" + "=" * 70)
        print(f"CLAUDE QUESTION GENERATION ENGINE - PHASE 3")
        print("=" * 70)
        print(f"Target: {total_questions:,} questions from {len(chunks)} chunks")
        print(f"Strategy: ~{questions_per_chunk} questions per chunk")
        print(f"Topic: {topic}")
        if topic.lower() == "cameroon":
            print("Category Balance: Geography 25%, History 25%, Culture 25%, General 25%")
        print("=" * 70)
        print()
        
        for i, chunk in enumerate(tqdm(chunks, desc="Generating questions", unit="chunk")):
            # Calculate remaining questions needed
            remaining = total_questions - len(all_questions)
            remaining_chunks = len(chunks) - i
            
            if remaining <= 0:
                break
            
            # Adjust questions needed for this chunk
            questions_needed = min(
                questions_per_chunk,
                remaining,
                max(1, remaining // remaining_chunks)
            )
            
            # Generate questions from chunk
            questions = self.generate_from_chunk(chunk, topic, questions_needed, chunk_index=i)
            all_questions.extend(questions)
            
            # Rate limiting: 2-second delay between API calls to avoid rate limits
            if i < len(chunks) - 1:
                time.sleep(2.0)
        
        # Trim to exact count if we generated too many
        all_questions = all_questions[:total_questions]
        
        # Calculate statistics
        end_time = time.time()
        duration = end_time - start_time
        
        stats = {
            "total_generated": len(all_questions),
            "target_count": total_questions,
            "chunks_processed": len(chunks),
            "chunks_failed": len(self.failed_chunks),
            "api_calls_total": self.total_api_calls,
            "api_calls_successful": self.successful_calls,
            "duration_seconds": duration,
            "questions_per_second": len(all_questions) / duration if duration > 0 else 0
        }
        
        # Print summary
        print()
        print("=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"[SUCCESS] Generated {len(all_questions):,} questions")
        print(f"  Target: {total_questions:,}")
        print(f"  Success rate: {len(all_questions)/total_questions*100:.1f}%")
        print(f"  Duration: {self._format_duration(duration)}")
        if self.failed_chunks:
            print(f"  Failed chunks: {len(self.failed_chunks)} (see {self.error_log_path})")
        print("=" * 70)
        
        return all_questions, stats
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "5m 32s")
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


if __name__ == "__main__":
    # Test the generator
    generator = QuestionGenerator()
    test_chunk = "Cameroon is a country in Central Africa. It is known for its diverse geography and culture."
    questions = generator.generate_from_chunk(test_chunk, "Cameroon", 2)
    print(f"Generated {len(questions)} test questions")

