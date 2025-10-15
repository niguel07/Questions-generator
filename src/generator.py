"""
Question Generator Module
Uses Claude API to generate multiple-choice questions from text chunks.
"""

import os
import json
import time
from typing import List, Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv
from tqdm import tqdm


# Load environment variables
load_dotenv()


class QuestionGenerator:
    """
    Generate multiple-choice questions using Claude API.
    """
    
    # Category weights for Cameroon topic
    CAMEROON_CATEGORIES = {
        "Geography": 0.25,
        "History": 0.25,
        "Culture": 0.25,
        "General Knowledge": 0.25
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize the question generator.
        
        Args:
            api_key: Claude API key (defaults to CLAUDE_API_KEY from .env)
        """
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def _create_prompt(self, text_chunk: str, topic: str, questions_needed: int) -> str:
        """
        Create a structured prompt for Claude.
        
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
Categories should be balanced as follows:
- Geography: 25%
- History: 25%
- Culture: 25%
- General Knowledge: 25%
"""
        
        prompt = f"""From the following text, create {questions_needed} multiple-choice questions about {topic}.

{category_info}
For each question, provide:
1. A clear question
2. Four answer options (A, B, C, D)
3. The correct answer (letter only)
4. A category
5. A difficulty level (easy, medium, hard)
6. A brief explanation

Return ONLY valid JSON array format without any markdown formatting or code blocks:
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
    "difficulty": "medium",
    "explanation": "Brief explanation of the answer"
  }}
]

TEXT:
{text_chunk}

Remember to return ONLY the JSON array, no other text or formatting."""
        
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
    
    def generate_from_chunk(
        self, 
        chunk: str, 
        topic: str, 
        questions_needed: int,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate questions from a single text chunk.
        
        Args:
            chunk: Text chunk to process
            topic: Topic to focus on
            questions_needed: Number of questions to generate
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of generated questions
        """
        prompt = self._create_prompt(chunk, topic, questions_needed)
        
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
                    return questions
                
                # If parsing failed, retry
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                print(f"API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print("Max retries reached, skipping chunk")
        
        return []
    
    def generate_questions(
        self, 
        chunks: List[str], 
        topic: str, 
        total_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate questions from multiple text chunks.
        
        Args:
            chunks: List of text chunks
            topic: Topic to focus on
            total_questions: Total number of questions to generate
            
        Returns:
            List of generated questions
        """
        if not chunks:
            print("No chunks provided")
            return []
        
        all_questions = []
        questions_per_chunk = max(1, total_questions // len(chunks))
        
        print(f"\nGenerating {total_questions} questions from {len(chunks)} chunks...")
        print(f"Target: ~{questions_per_chunk} questions per chunk\n")
        
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
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
            
            questions = self.generate_from_chunk(chunk, topic, questions_needed)
            all_questions.extend(questions)
            
            # Rate limiting: small delay between requests
            if i < len(chunks) - 1:
                time.sleep(0.5)
        
        # Trim to exact count if we generated too many
        all_questions = all_questions[:total_questions]
        
        print(f"\n✓ Successfully generated {len(all_questions)} questions")
        
        return all_questions


if __name__ == "__main__":
    # Test the generator
    generator = QuestionGenerator()
    test_chunk = "Cameroon is a country in Central Africa. It is known for its diverse geography and culture."
    questions = generator.generate_from_chunk(test_chunk, "Cameroon", 2)
    print(f"Generated {len(questions)} test questions")

