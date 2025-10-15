"""
JSON Saver Module - Phase 3
Saves question data to JSON files with validation and proper formatting.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def validate_question_structure(question: Dict[str, Any]) -> bool:
    """
    Validate that a question has all required fields and proper structure.
    
    Args:
        question: Question dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["question", "options", "answer", "category", "difficulty", "explanation"]
    
    # Check all required fields exist
    if not all(field in question for field in required_fields):
        return False
    
    # Validate options is a dict with A, B, C, D
    if not isinstance(question["options"], dict):
        return False
    
    required_options = ["A", "B", "C", "D"]
    if not all(opt in question["options"] for opt in required_options):
        return False
    
    # Validate answer is one of the options
    if question["answer"] not in required_options:
        return False
    
    # Validate difficulty is one of the expected values
    valid_difficulties = ["easy", "medium", "hard", "Easy", "Medium", "Hard"]
    if question["difficulty"] not in valid_difficulties:
        return False
    
    return True


def save_questions_to_json(
    questions: List[Dict[str, Any]], 
    output_path: str,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Save questions to a JSON file with validation.
    Validates structure before saving to ensure data integrity.
    
    Args:
        questions: List of question dictionaries
        output_path: Path to output JSON file
        validate: Whether to validate questions before saving (default: True)
        
    Returns:
        Dictionary with save statistics
        
    Raises:
        ValueError: If questions fail validation
    """
    output_file = Path(output_path)
    
    # Create parent directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Validate questions if requested
    if validate:
        invalid_count = 0
        valid_questions = []
        
        for i, q in enumerate(questions):
            if validate_question_structure(q):
                valid_questions.append(q)
            else:
                invalid_count += 1
                print(f"[WARNING] Question {i+1} failed validation, skipping")
        
        if invalid_count > 0:
            print(f"[WARNING] {invalid_count} questions failed validation and were skipped")
        
        questions = valid_questions
    
    if not questions:
        raise ValueError("No valid questions to save")
    
    # Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(
                questions, 
                f, 
                ensure_ascii=False,  # Allow UTF-8 characters
                indent=2
            )
        
        file_size = output_file.stat().st_size
        
        # Print success summary
        print(f"\n[SUCCESS] Successfully generated {len(questions):,} questions saved to {output_path}")
        print(f"  File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print(f"  Location: {output_file.absolute()}")
        
        return {
            "questions_saved": len(questions),
            "file_size_bytes": file_size,
            "output_path": str(output_file.absolute())
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to save questions: {e}")
        raise


# Alias for backward compatibility
def save_questions(
    questions: List[Dict[str, Any]], 
    output_file: str,
    ensure_utf8: bool = True,
    indent: int = 2
) -> None:
    """
    Legacy function - calls save_questions_to_json.
    For backward compatibility with existing code.
    
    Args:
        questions: List of question dictionaries
        output_file: Path to output file
        ensure_utf8: Ensure UTF-8 encoding (default: True)
        indent: JSON indentation level (default: 2)
    """
    save_questions_to_json(questions, output_file, validate=True)


def load_questions(input_file: str) -> List[Dict[str, Any]]:
    """
    Load questions from a JSON file.
    
    Args:
        input_file: Path to input file
        
    Returns:
        List of question dictionaries
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        if not isinstance(questions, list):
            raise ValueError("Invalid format: expected a list of questions")
        
        return questions
        
    except Exception as e:
        print(f"Error loading questions: {e}")
        raise


def get_question_stats(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics about the questions.
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        Dictionary with statistics
    """
    if not questions:
        return {
            "total": 0,
            "by_category": {},
            "by_difficulty": {}
        }
    
    stats = {
        "total": len(questions),
        "by_category": {},
        "by_difficulty": {}
    }
    
    for q in questions:
        # Count by category
        category = q.get("category", "Unknown")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Count by difficulty
        difficulty = q.get("difficulty", "Unknown")
        stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
    
    return stats


if __name__ == "__main__":
    # Test the saver
    test_questions = [
        {
            "question": "What is the capital of Cameroon?",
            "options": {"A": "Douala", "B": "Yaoundé", "C": "Buea", "D": "Bamenda"},
            "answer": "B",
            "category": "Geography",
            "difficulty": "easy",
            "explanation": "Yaoundé is the political capital of Cameroon."
        }
    ]
    
    save_questions(test_questions, "test_output.json")
    loaded = load_questions("test_output.json")
    stats = get_question_stats(loaded)
    print(f"Stats: {stats}")

