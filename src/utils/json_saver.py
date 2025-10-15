"""
JSON Saver Module
Saves question data to JSON files with proper formatting.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def save_questions(
    questions: List[Dict[str, Any]], 
    output_file: str,
    ensure_utf8: bool = True,
    indent: int = 2
) -> None:
    """
    Save questions to a JSON file.
    
    Args:
        questions: List of question dictionaries
        output_file: Path to output file
        ensure_utf8: Ensure UTF-8 encoding (default: True)
        indent: JSON indentation level (default: 2)
    """
    output_path = Path(output_file)
    
    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                questions, 
                f, 
                ensure_ascii=not ensure_utf8,
                indent=indent
            )
        
        print(f"\n✓ Saved {len(questions)} questions to {output_file}")
        print(f"  File size: {output_path.stat().st_size:,} bytes")
        
    except Exception as e:
        print(f"Error saving questions: {e}")
        raise


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

