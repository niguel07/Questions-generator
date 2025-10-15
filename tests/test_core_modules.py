"""
Comprehensive Tests for Question Generator AI - Phase 10
Tests core modules: parser, chunker, generator, validator, quality_scorer, reviewer, users
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chunker import chunk_text
from validator import validate_questions
from quality_scorer import score_all_questions
from users import UserManager


class TestChunker(unittest.TestCase):
    """Test text chunking functionality."""
    
    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        text = " ".join(["word"] * 2000)
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(isinstance(chunk, str) for chunk in chunks))
    
    def test_chunk_text_empty(self):
        """Test chunking with empty text."""
        chunks = chunk_text("", chunk_size=1000, overlap=100)
        self.assertEqual(len(chunks), 0)
    
    def test_chunk_text_small(self):
        """Test chunking with text smaller than chunk size."""
        text = " ".join(["word"] * 50)
        chunks = chunk_text(text, chunk_size=1000, overlap=100)
        self.assertEqual(len(chunks), 1)


class TestValidator(unittest.TestCase):
    """Test question validation."""
    
    def test_validate_valid_questions(self):
        """Test validation with valid questions."""
        questions = [
            {
                "question": "What is the capital of France?",
                "options": {"A": "Paris", "B": "London", "C": "Berlin", "D": "Rome"},
                "answer": "A",
                "category": "Geography",
                "difficulty": "Easy",
                "explanation": "Paris is the capital."
            }
        ]
        
        validated = validate_questions(questions)
        self.assertEqual(len(validated), 1)
    
    def test_validate_invalid_questions(self):
        """Test validation with invalid questions."""
        questions = [
            {
                "question": "Too short",  # Too short
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "answer": "A",
                "category": "Test",
                "difficulty": "Easy",
                "explanation": "Test"
            }
        ]
        
        validated = validate_questions(questions)
        self.assertEqual(len(validated), 0)
    
    def test_validate_duplicate_detection(self):
        """Test duplicate question detection."""
        questions = [
            {
                "question": "What is the capital of France?",
                "options": {"A": "Paris", "B": "London", "C": "Berlin", "D": "Rome"},
                "answer": "A",
                "category": "Geography",
                "difficulty": "Easy",
                "explanation": "Paris is the capital."
            },
            {
                "question": "What is the capital of France?",  # Duplicate
                "options": {"A": "Paris", "B": "London", "C": "Berlin", "D": "Rome"},
                "answer": "A",
                "category": "Geography",
                "difficulty": "Easy",
                "explanation": "Paris is the capital."
            }
        ]
        
        validated = validate_questions(questions)
        self.assertEqual(len(validated), 1)  # Only one should remain


class TestQualityScorer(unittest.TestCase):
    """Test quality scoring."""
    
    def test_score_high_quality_question(self):
        """Test scoring a high-quality question."""
        questions = [
            {
                "question": "What is the capital of France and why is it historically significant?",
                "options": {
                    "A": "Paris - center of French Revolution",
                    "B": "London",
                    "C": "Berlin",
                    "D": "Rome"
                },
                "answer": "A",
                "category": "Geography",
                "difficulty": "Medium",
                "explanation": "Paris is the capital of France and played a central role in the French Revolution."
            }
        ]
        
        scored = score_all_questions(questions, sort_by_quality=False)
        self.assertEqual(len(scored), 1)
        self.assertIn("quality_score", scored[0])
        self.assertGreater(scored[0]["quality_score"], 0.7)
    
    def test_score_all_questions(self):
        """Test scoring multiple questions."""
        questions = [
            {
                "question": "What is 2+2?",
                "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                "answer": "B",
                "category": "Math",
                "difficulty": "Easy",
                "explanation": "Basic addition."
            },
            {
                "question": "What is the Pythagorean theorem and how is it used?",
                "options": {
                    "A": "a² + b² = c²",
                    "B": "E = mc²",
                    "C": "F = ma",
                    "D": "PV = nRT"
                },
                "answer": "A",
                "category": "Mathematics",
                "difficulty": "Medium",
                "explanation": "The Pythagorean theorem relates the sides of a right triangle."
            }
        ]
        
        scored = score_all_questions(questions, sort_by_quality=True)
        self.assertEqual(len(scored), 2)
        # Should be sorted by quality (descending)
        self.assertGreaterEqual(scored[0]["quality_score"], scored[1]["quality_score"])


class TestUserManager(unittest.TestCase):
    """Test user management."""
    
    def setUp(self):
        """Set up test user manager."""
        self.manager = UserManager("output/test_users.json")
    
    def tearDown(self):
        """Clean up test file."""
        test_file = Path("output/test_users.json")
        if test_file.exists():
            test_file.unlink()
    
    def test_login(self):
        """Test user login."""
        result = self.manager.login("test_user")
        self.assertTrue(result["success"])
        self.assertEqual(result["username"], "test_user")
    
    def test_add_session(self):
        """Test adding a session."""
        self.manager.login("test_user")
        self.manager.add_session("test_user", {
            "topics": ["Cameroon", "AI"],
            "questions_generated": 1000,
            "avg_quality": 0.92
        })
        
        sessions = self.manager.get_sessions("test_user")
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["topics"], ["Cameroon", "AI"])
    
    def test_get_stats(self):
        """Test getting user stats."""
        self.manager.login("test_user")
        self.manager.add_session("test_user", {
            "topics": ["Math"],
            "questions_generated": 500,
            "avg_quality": 0.85
        })
        
        stats = self.manager.get_stats("test_user")
        self.assertEqual(stats["total_sessions"], 1)
        self.assertEqual(stats["total_questions_generated"], 500)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestChunker))
    suite.addTests(loader.loadTestsFromTestCase(TestValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestUserManager))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

