"""
Quality Scorer Module - Phase 4
Assigns quality scores to questions based on multiple criteria.
Scores range from 0.0 to 1.0, with higher scores indicating better quality.
"""

from typing import List, Dict, Any
import re
from tqdm import tqdm


class QualityScorer:
    """
    Assigns quality scores to questions based on multiple quality criteria.
    """
    
    # Quality scoring weights
    WEIGHTS = {
        "question_clarity": 0.2,
        "balanced_options": 0.2,
        "valid_answer": 0.2,
        "explanation_quality": 0.2,
        "metadata_quality": 0.2
    }
    
    def __init__(self):
        """Initialize the quality scorer."""
        pass
    
    def _score_question_clarity(self, question: Dict[str, Any]) -> float:
        """
        Score question clarity based on length and structure.
        Optimal length: 30-200 characters.
        
        Args:
            question: Question dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        q_text = question.get("question", "")
        length = len(q_text)
        
        # Optimal range: 30-200 characters
        if 30 <= length <= 200:
            score = 1.0
        elif length < 30:
            # Too short - penalize proportionally
            score = length / 30.0
        else:  # length > 200
            # Too long - penalize proportionally
            excess = length - 200
            penalty = min(excess / 100.0, 1.0)
            score = max(0.0, 1.0 - penalty)
        
        # Bonus for ending with question mark
        if q_text.strip().endswith("?"):
            score = min(1.0, score + 0.1)
        
        return score
    
    def _score_balanced_options(self, question: Dict[str, Any]) -> float:
        """
        Score option quality based on distinctness and balance.
        
        Args:
            question: Question dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        options = question.get("options", {})
        
        if not isinstance(options, dict) or len(options) != 4:
            return 0.0
        
        score = 0.0
        
        # Check for 4 distinct values
        values = list(options.values())
        if len(set(values)) == 4:
            score += 0.5
        else:
            score += len(set(values)) / 8.0  # Partial credit
        
        # Check length balance (options should be reasonably similar in length)
        lengths = [len(str(v)) for v in values]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            # Calculate variance
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            std_dev = variance ** 0.5
            
            # Lower std_dev is better (more balanced)
            if std_dev < 10:
                score += 0.5
            elif std_dev < 20:
                score += 0.3
            elif std_dev < 30:
                score += 0.1
        
        return min(1.0, score)
    
    def _score_valid_answer(self, question: Dict[str, Any]) -> float:
        """
        Score answer validity.
        
        Args:
            question: Question dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        answer = question.get("answer", "")
        options = question.get("options", {})
        
        # Check if answer is a valid key
        if answer in ["A", "B", "C", "D"] and answer in options:
            return 1.0
        
        return 0.0
    
    def _score_explanation_quality(self, question: Dict[str, Any]) -> float:
        """
        Score explanation quality based on presence and length.
        
        Args:
            question: Question dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        explanation = question.get("explanation", "")
        
        if not explanation or not explanation.strip():
            return 0.0
        
        length = len(explanation.strip())
        
        # Optimal: at least 15 characters
        if length >= 50:
            score = 1.0
        elif length >= 15:
            score = 0.8
        else:
            score = length / 15.0 * 0.5
        
        # Bonus for complete sentences
        if explanation.strip().endswith("."):
            score = min(1.0, score + 0.1)
        
        return score
    
    def _score_metadata_quality(self, question: Dict[str, Any]) -> float:
        """
        Score metadata quality (category and difficulty).
        
        Args:
            question: Question dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check category
        category = question.get("category", "")
        if category and category.strip() and len(category) >= 3:
            score += 0.5
        
        # Check difficulty
        difficulty = question.get("difficulty", "")
        valid_difficulties = ["Easy", "Medium", "Hard"]
        if difficulty in valid_difficulties:
            score += 0.5
        
        return score
    
    def score_question_quality(self, question: Dict[str, Any]) -> float:
        """
        Calculate overall quality score for a question.
        
        Args:
            question: Question dictionary
            
        Returns:
            Overall quality score between 0.0 and 1.0
        """
        # Calculate individual scores
        clarity_score = self._score_question_clarity(question)
        options_score = self._score_balanced_options(question)
        answer_score = self._score_valid_answer(question)
        explanation_score = self._score_explanation_quality(question)
        metadata_score = self._score_metadata_quality(question)
        
        # Calculate weighted total
        total_score = (
            clarity_score * self.WEIGHTS["question_clarity"] +
            options_score * self.WEIGHTS["balanced_options"] +
            answer_score * self.WEIGHTS["valid_answer"] +
            explanation_score * self.WEIGHTS["explanation_quality"] +
            metadata_score * self.WEIGHTS["metadata_quality"]
        )
        
        return round(total_score, 3)
    
    def score_all_questions(
        self, 
        questions: List[Dict[str, Any]], 
        sort_by_quality: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Score all questions and optionally sort by quality.
        
        Args:
            questions: List of question dictionaries
            sort_by_quality: Whether to sort by descending quality score
            
        Returns:
            List of questions with quality_score added
        """
        print("=" * 70)
        print("QUALITY SCORING")
        print("=" * 70)
        print(f"Scoring {len(questions):,} questions...")
        print()
        
        # Score each question
        for question in questions:
            score = self.score_question_quality(question)
            question["quality_score"] = score
        
        # Sort by quality if requested
        if sort_by_quality:
            questions.sort(key=lambda q: q.get("quality_score", 0.0), reverse=True)
        
        # Calculate statistics
        if questions:
            scores = [q.get("quality_score", 0.0) for q in questions]
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            # Count by quality tiers
            excellent = sum(1 for s in scores if s >= 0.9)
            good = sum(1 for s in scores if 0.7 <= s < 0.9)
            fair = sum(1 for s in scores if 0.5 <= s < 0.7)
            poor = sum(1 for s in scores if s < 0.5)
            
            print(f"[SUCCESS] Quality scoring complete")
            print(f"  Average quality score: {avg_score:.3f}")
            print(f"  Score range: {min_score:.3f} - {max_score:.3f}")
            print()
            print("Quality Distribution:")
            print(f"  Excellent (0.9-1.0): {excellent:,} ({excellent/len(questions)*100:.1f}%)")
            print(f"  Good (0.7-0.9): {good:,} ({good/len(questions)*100:.1f}%)")
            print(f"  Fair (0.5-0.7): {fair:,} ({fair/len(questions)*100:.1f}%)")
            print(f"  Poor (0.0-0.5): {poor:,} ({poor/len(questions)*100:.1f}%)")
            print()
        
        return questions


def score_question_quality(question: Dict[str, Any]) -> float:
    """
    Score a single question's quality.
    Convenience function that creates a scorer and processes one question.
    
    Args:
        question: Question dictionary
        
    Returns:
        Quality score between 0.0 and 1.0
    """
    scorer = QualityScorer()
    return scorer.score_question_quality(question)


def score_all_questions(
    questions: List[Dict[str, Any]], 
    sort_by_quality: bool = True
) -> List[Dict[str, Any]]:
    """
    Score all questions and optionally sort by quality.
    Convenience function that creates a scorer and processes all questions.
    
    Args:
        questions: List of question dictionaries
        sort_by_quality: Whether to sort by descending quality score
        
    Returns:
        List of questions with quality_score added
    """
    scorer = QualityScorer()
    return scorer.score_all_questions(questions, sort_by_quality)


if __name__ == "__main__":
    # Test the scorer
    test_question = {
        "question": "What is the capital of Cameroon?",
        "options": {"A": "Douala", "B": "Yaoundé", "C": "Buea", "D": "Bamenda"},
        "answer": "B",
        "category": "Geography",
        "difficulty": "Easy",
        "explanation": "Yaoundé is the political capital of Cameroon."
    }
    
    score = score_question_quality(test_question)
    print(f"Test question quality score: {score:.3f}")
    
    # Test batch scoring
    test_questions = [test_question] * 5
    scored = score_all_questions(test_questions)
    print(f"\nScored {len(scored)} questions")

