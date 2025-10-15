"""
Question Validator Module - Phase 4
Validates, cleans, and filters generated questions to ensure data quality.
Implements duplicate detection, schema validation, and data normalization.
"""

import re
import json
import difflib
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from collections import Counter
from datetime import datetime


# Validation report file path
VALIDATION_REPORT_PATH = "output/validation_report.txt"


class QuestionValidator:
    """
    Validates and cleans generated questions.
    Filters duplicates, normalizes data, and ensures schema integrity.
    """
    
    def __init__(self, report_path: str = VALIDATION_REPORT_PATH):
        """
        Initialize the validator.
        
        Args:
            report_path: Path to validation report file
        """
        self.report_path = report_path
        self.seen_questions: Set[str] = set()
        self.stats = {
            "total_input": 0,
            "total_output": 0,
            "missing_keys": 0,
            "invalid_length": 0,
            "invalid_options": 0,
            "invalid_answer": 0,
            "duplicates": 0,
            "factual_issues": 0,
            "auto_corrected": 0
        }
        
        # Ensure report directory exists
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        Removes punctuation, converts to lowercase, removes extra spaces.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _is_duplicate(self, question_text: str, threshold: float = 0.85) -> bool:
        """
        Check if question is a duplicate using fuzzy matching.
        
        Args:
            question_text: Question text to check
            threshold: Similarity threshold (default: 0.85 = 85%)
            
        Returns:
            True if duplicate, False otherwise
        """
        normalized = self._normalize_text(question_text)
        
        # Quick exact match check
        if normalized in self.seen_questions:
            return True
        
        # Fuzzy match against existing questions
        for seen_q in self.seen_questions:
            similarity = difflib.SequenceMatcher(None, normalized, seen_q).ratio()
            if similarity >= threshold:
                return True
        
        # Not a duplicate - add to seen set
        self.seen_questions.add(normalized)
        return False
    
    def _validate_schema(self, question: Dict[str, Any]) -> bool:
        """
        Check if question has all required fields.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid schema, False otherwise
        """
        required_fields = ["question", "options", "answer", "category", "difficulty", "explanation"]
        
        if not all(field in question for field in required_fields):
            self.stats["missing_keys"] += 1
            return False
        
        return True
    
    def _validate_text_length(self, question: Dict[str, Any]) -> bool:
        """
        Check if question text is within acceptable length range.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid length, False otherwise
        """
        q_text = question.get("question", "")
        
        if len(q_text) < 20 or len(q_text) > 300:
            self.stats["invalid_length"] += 1
            return False
        
        return True
    
    def _validate_and_fix_options(self, question: Dict[str, Any]) -> bool:
        """
        Validate options structure and remove duplicates.
        Ensures exactly 4 unique options.
        
        Args:
            question: Question dictionary (modified in place)
            
        Returns:
            True if valid/fixed, False if unfixable
        """
        options = question.get("options", {})
        
        # Convert to dict if it's a list (handle both formats)
        if isinstance(options, list):
            if len(options) != 4:
                self.stats["invalid_options"] += 1
                return False
            options = {"A": options[0], "B": options[1], "C": options[2], "D": options[3]}
            question["options"] = options
        
        # Validate dict structure
        if not isinstance(options, dict):
            self.stats["invalid_options"] += 1
            return False
        
        required_keys = ["A", "B", "C", "D"]
        if not all(key in options for key in required_keys):
            self.stats["invalid_options"] += 1
            return False
        
        # Check for empty options
        for key in required_keys:
            if not options[key] or not str(options[key]).strip():
                self.stats["invalid_options"] += 1
                return False
        
        # Remove duplicate options
        option_values = list(options.values())
        if len(option_values) != len(set(option_values)):
            # Has duplicates - this is invalid
            self.stats["invalid_options"] += 1
            return False
        
        return True
    
    def _validate_and_fix_answer(self, question: Dict[str, Any]) -> bool:
        """
        Validate answer matches one of the options.
        Auto-correct using fuzzy matching if possible.
        
        Args:
            question: Question dictionary (modified in place)
            
        Returns:
            True if valid/fixed, False if unfixable
        """
        answer = question.get("answer", "")
        options = question.get("options", {})
        
        # Normalize answer (could be "A", "a", "Option A", etc.)
        answer_clean = answer.strip().upper()
        
        # Check if answer is a valid key (A, B, C, D)
        if answer_clean in ["A", "B", "C", "D"]:
            question["answer"] = answer_clean
            return True
        
        # Try to find the answer in option values
        option_values = {k: v for k, v in options.items()}
        
        # Try exact match
        for key, value in option_values.items():
            if str(value).strip().lower() == answer.strip().lower():
                question["answer"] = key
                self.stats["auto_corrected"] += 1
                return True
        
        # Try fuzzy match
        matches = difflib.get_close_matches(
            answer, 
            [str(v) for v in option_values.values()], 
            n=1, 
            cutoff=0.8
        )
        
        if matches:
            # Find the key for this value
            for key, value in option_values.items():
                if str(value) == matches[0]:
                    question["answer"] = key
                    self.stats["auto_corrected"] += 1
                    return True
        
        # Couldn't fix
        self.stats["invalid_answer"] += 1
        return False
    
    def _normalize_category(self, question: Dict[str, Any]) -> None:
        """
        Normalize category to title case.
        
        Args:
            question: Question dictionary (modified in place)
        """
        category = question.get("category", "")
        if category:
            question["category"] = category.strip().title()
    
    def _normalize_difficulty(self, question: Dict[str, Any]) -> bool:
        """
        Normalize difficulty level.
        Accepts only Easy, Medium, or Hard.
        
        Args:
            question: Question dictionary (modified in place)
            
        Returns:
            True if valid/fixed, False if unfixable
        """
        difficulty = question.get("difficulty", "").strip().lower()
        
        valid_difficulties = {
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard",
            "intermediate": "Medium",
            "difficult": "Hard",
            "simple": "Easy",
            "basic": "Easy",
            "advanced": "Hard",
            "challenging": "Hard"
        }
        
        if difficulty in valid_difficulties:
            question["difficulty"] = valid_difficulties[difficulty]
            return True
        
        # Default to Medium if unrecognized
        question["difficulty"] = "Medium"
        return True
    
    def _check_factual_issues(self, question: Dict[str, Any]) -> bool:
        """
        Check for obvious factual or formatting issues.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid, False if has issues
        """
        q_text = question.get("question", "")
        
        # Question starts with punctuation
        if q_text.startswith("?") or q_text.startswith("."):
            self.stats["factual_issues"] += 1
            return False
        
        # Question is only numbers
        if q_text.strip().replace(" ", "").isdigit():
            self.stats["factual_issues"] += 1
            return False
        
        # Question has no letters
        if not re.search(r'[a-zA-Z]', q_text):
            self.stats["factual_issues"] += 1
            return False
        
        return True
    
    def validate_question(self, question: Dict[str, Any]) -> bool:
        """
        Validate a single question through all checks.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid, False if should be filtered
        """
        # Schema validation
        if not self._validate_schema(question):
            return False
        
        # Length validation
        if not self._validate_text_length(question):
            return False
        
        # Options validation
        if not self._validate_and_fix_options(question):
            return False
        
        # Answer validation and auto-correction
        if not self._validate_and_fix_answer(question):
            return False
        
        # Factual issues
        if not self._check_factual_issues(question):
            return False
        
        # Duplicate detection
        if self._is_duplicate(question["question"]):
            self.stats["duplicates"] += 1
            return False
        
        # Normalization (always succeeds)
        self._normalize_category(question)
        self._normalize_difficulty(question)
        
        return True
    
    def validate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean a list of questions.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of validated and cleaned questions
        """
        self.stats["total_input"] = len(questions)
        self.seen_questions.clear()
        
        print("\n" + "=" * 70)
        print("PHASE 4: QUESTION VALIDATION & QUALITY CONTROL")
        print("=" * 70)
        print(f"Validating {len(questions):,} generated questions...")
        print()
        
        validated = []
        
        for question in questions:
            if self.validate_question(question):
                validated.append(question)
        
        self.stats["total_output"] = len(validated)
        
        # Generate report
        self._generate_report()
        
        # Print summary
        dropped = self.stats["total_input"] - self.stats["total_output"]
        print(f"\n[SUCCESS] Validation complete - {self.stats['total_output']:,} valid questions retained")
        print(f"  Dropped: {dropped:,} invalid entries")
        print(f"  Duplicates removed: {self.stats['duplicates']}")
        print(f"  Auto-corrected answers: {self.stats['auto_corrected']}")
        print(f"  Validation report: {self.report_path}")
        print()
        
        return validated
    
    def _generate_report(self) -> None:
        """
        Generate a detailed validation report.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
{'=' * 70}
QUESTION VALIDATION REPORT
{'=' * 70}
Generated: {timestamp}

SUMMARY:
  Total input questions: {self.stats['total_input']:,}
  Valid questions retained: {self.stats['total_output']:,}
  Questions dropped: {self.stats['total_input'] - self.stats['total_output']:,}
  Success rate: {(self.stats['total_output'] / self.stats['total_input'] * 100) if self.stats['total_input'] > 0 else 0:.1f}%

DROPPED QUESTIONS BREAKDOWN:
  - Missing required keys: {self.stats['missing_keys']}
  - Invalid question length: {self.stats['invalid_length']}
  - Invalid options structure: {self.stats['invalid_options']}
  - Invalid/unfixable answer: {self.stats['invalid_answer']}
  - Duplicate questions: {self.stats['duplicates']}
  - Factual/formatting issues: {self.stats['factual_issues']}

AUTO-CORRECTIONS:
  - Answers auto-corrected: {self.stats['auto_corrected']}

VALIDATION CHECKS PERFORMED:
  ✓ Schema validation (required fields)
  ✓ Question length (20-300 characters)
  ✓ Options integrity (4 unique options)
  ✓ Answer matching with auto-correction
  ✓ Duplicate detection (85% similarity threshold)
  ✓ Category normalization (title case)
  ✓ Difficulty normalization (Easy/Medium/Hard)
  ✓ Factual content checks

{'=' * 70}
"""
        
        try:
            with open(self.report_path, 'w', encoding='utf-8') as f:
                f.write(report)
        except Exception as e:
            print(f"[WARNING] Could not write validation report: {e}")


def validate_questions(questions: List[Dict[str, Any]], report_path: str = VALIDATION_REPORT_PATH) -> List[Dict[str, Any]]:
    """
    Validate and clean a list of questions.
    Convenience function that creates a validator and processes questions.
    
    Args:
        questions: List of question dictionaries
        report_path: Path to validation report file
        
    Returns:
        List of validated and cleaned questions
    """
    validator = QuestionValidator(report_path)
    return validator.validate_questions(questions)


if __name__ == "__main__":
    # Test the validator
    test_questions = [
        {
            "question": "What is the capital of Cameroon?",
            "options": {"A": "Douala", "B": "Yaoundé", "C": "Buea", "D": "Bamenda"},
            "answer": "B",
            "category": "geography",
            "difficulty": "easy",
            "explanation": "Yaoundé is the political capital."
        },
        {
            "question": "What is the capital of Cameroon?",  # Duplicate
            "options": {"A": "Douala", "B": "Yaoundé", "C": "Buea", "D": "Bamenda"},
            "answer": "B",
            "category": "Geography",
            "difficulty": "Easy",
            "explanation": "Yaoundé is the capital."
        },
        {
            "question": "Test",  # Too short
            "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
            "answer": "A",
            "category": "Test",
            "difficulty": "Easy",
            "explanation": "Test"
        }
    ]
    
    validated = validate_questions(test_questions)
    print(f"\nTest: {len(validated)} valid questions out of {len(test_questions)}")

