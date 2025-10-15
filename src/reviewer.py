"""
Question Reviewer Module - Phase 8
Uses Claude AI to review and provide feedback on generated questions.
Suggests improvements for accuracy, clarity, and difficulty calibration.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QuestionReviewer:
    """
    AI-powered question reviewer using Claude API.
    Provides ratings, feedback, and suggested improvements.
    """
    
    def __init__(self):
        """Initialize the reviewer with Claude API client."""
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_retries = 3
    
    def _create_review_prompt(self, question: Dict[str, Any]) -> str:
        """
        Create a structured prompt for Claude to review a question.
        
        Args:
            question: Question dictionary with all fields
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a professional educational content reviewer with expertise in multiple-choice question design.

Review the following multiple-choice question for:
1. **Correctness**: Is the answer factually accurate?
2. **Clarity**: Is the question clear and unambiguous?
3. **Difficulty**: Is the difficulty level appropriate?
4. **Options**: Are the distractors plausible but clearly incorrect?
5. **Explanation**: Is the explanation complete and helpful?

QUESTION DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question: {question.get('question', '')}

Options:
  A) {question.get('options', {}).get('A', '')}
  B) {question.get('options', {}).get('B', '')}
  C) {question.get('options', {}).get('C', '')}
  D) {question.get('options', {}).get('D', '')}

Correct Answer: {question.get('answer', '')}
Category: {question.get('category', '')}
Difficulty: {question.get('difficulty', '')}
Explanation: {question.get('explanation', '')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please provide your review as a JSON object with the following structure:
{{
  "rating": 0.0-1.0,
  "feedback": "Detailed textual review explaining strengths and weaknesses",
  "issues": ["issue1", "issue2"],
  "suggested_fix": {{
    "question": "improved question text or null if no change needed",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}} or null,
    "answer": "A|B|C|D or null",
    "category": "category or null",
    "difficulty": "Easy|Medium|Hard or null",
    "explanation": "improved explanation or null"
  }}
}}

Return ONLY the JSON object, no additional text.
"""
        return prompt
    
    def _parse_review_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse Claude's response and extract the review JSON.
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            Parsed review dictionary or None if parsing fails
        """
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Parse JSON
            review = json.loads(text)
            
            # Validate required fields
            if 'rating' not in review or 'feedback' not in review:
                return None
            
            # Ensure rating is between 0 and 1
            review['rating'] = max(0.0, min(1.0, float(review['rating'])))
            
            return review
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing review response: {e}")
            return None
    
    def review_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a question to Claude for review and get structured feedback.
        
        Args:
            question: Question dictionary to review
            
        Returns:
            Review dictionary with rating, feedback, and suggested fixes
        """
        prompt = self._create_review_prompt(question)
        
        for attempt in range(self.max_retries):
            try:
                # Call Claude API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,  # Lower temperature for more consistent reviews
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                # Extract response text
                response_text = response.content[0].text
                
                # Parse the review
                review = self._parse_review_response(response_text)
                
                if review:
                    return {
                        "success": True,
                        "review": review
                    }
                
                # If parsing failed, retry
                print(f"Failed to parse review (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(1)
                
            except Exception as e:
                print(f"Error during review (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {
                        "success": False,
                        "error": str(e)
                    }
        
        return {
            "success": False,
            "error": "Failed to get valid review after multiple attempts"
        }
    
    def batch_review(self, questions: list[Dict[str, Any]], max_questions: int = 10) -> list[Dict[str, Any]]:
        """
        Review multiple questions in batch.
        
        Args:
            questions: List of questions to review
            max_questions: Maximum number of questions to review (rate limiting)
            
        Returns:
            List of review results
        """
        results = []
        questions_to_review = questions[:max_questions]
        
        for i, question in enumerate(questions_to_review):
            print(f"Reviewing question {i + 1}/{len(questions_to_review)}...")
            
            review_result = self.review_question(question)
            results.append({
                "question_index": i,
                "original_question": question,
                "review_result": review_result
            })
            
            # Rate limiting: wait between requests
            if i < len(questions_to_review) - 1:
                time.sleep(2)
        
        return results


if __name__ == "__main__":
    # Test the reviewer
    test_question = {
        "question": "What is the capital of Cameroon?",
        "options": {
            "A": "Douala",
            "B": "Yaoundé",
            "C": "Buea",
            "D": "Bamenda"
        },
        "answer": "B",
        "category": "Geography",
        "difficulty": "Easy",
        "explanation": "Yaoundé is the political capital of Cameroon."
    }
    
    reviewer = QuestionReviewer()
    result = reviewer.review_question(test_question)
    
    if result['success']:
        review = result['review']
        print(f"\nRating: {review['rating']:.2f}")
        print(f"Feedback: {review['feedback']}")
        if review.get('suggested_fix'):
            print("\nSuggested improvements available")
    else:
        print(f"Review failed: {result['error']}")

