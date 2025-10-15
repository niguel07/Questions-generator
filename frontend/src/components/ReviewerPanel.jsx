import { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Button, CircularProgress, Alert } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import QuestionList from './QuestionList';
import ReviewModal from './ReviewModal';

const API_BASE_URL = 'http://localhost:8000';

function ReviewerPanel() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [reviewing, setReviewing] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Fetch questions
  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/questions?limit=100`);
      setQuestions(response.data.questions || []);
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewClick = async (question, index) => {
    setSelectedQuestion({ ...question, index });
    setReviewing(true);
    setShowModal(true);
    setReviewResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/review`, {
        question: question.question,
        options: question.options,
        answer: question.answer,
        explanation: question.explanation,
        category: question.category,
        difficulty: question.difficulty
      });

      setReviewResult(response.data);
    } catch (error) {
      console.error('Review error:', error);
      setReviewResult({
        success: false,
        error: 'Failed to review question'
      });
    } finally {
      setReviewing(false);
    }
  };

  const handleApplySuggestion = async (suggestion) => {
    if (!selectedQuestion) return;

    try {
      await axios.patch(`${API_BASE_URL}/update-question/${selectedQuestion.index}`, suggestion);
      
      // Update local state
      const updatedQuestions = [...questions];
      updatedQuestions[selectedQuestion.index] = {
        ...updatedQuestions[selectedQuestion.index],
        ...suggestion
      };
      setQuestions(updatedQuestions);
      
      setShowModal(false);
      alert('Question updated successfully!');
    } catch (error) {
      console.error('Update error:', error);
      alert('Failed to update question');
    }
  };

  const handleReject = () => {
    setShowModal(false);
    setReviewResult(null);
    setSelectedQuestion(null);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.12)', mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1F2937' }}>
              🤖 AI Question Reviewer
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={fetchQuestions}
              disabled={loading}
              sx={{
                borderColor: '#2563EB',
                color: '#2563EB',
                '&:hover': {
                  borderColor: '#1D4ED8',
                  bgcolor: '#EFF6FF'
                },
                textTransform: 'none'
              }}
            >
              {loading ? <CircularProgress size={20} /> : 'Refresh'}
            </Button>
          </Box>

          <Alert severity="info" sx={{ mb: 3, borderRadius: '8px' }}>
            Select any question below to get Claude's expert review. The AI will evaluate accuracy,
            clarity, difficulty, and suggest improvements.
          </Alert>

          {loading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : questions.length === 0 ? (
            <Typography variant="body2" sx={{ color: '#9CA3AF', textAlign: 'center', py: 4 }}>
              No questions available. Generate some questions first.
            </Typography>
          ) : (
            <QuestionList questions={questions} onReview={handleReviewClick} />
          )}
        </CardContent>
      </Card>

      <ReviewModal
        open={showModal}
        onClose={() => setShowModal(false)}
        question={selectedQuestion}
        reviewing={reviewing}
        reviewResult={reviewResult}
        onApply={handleApplySuggestion}
        onReject={handleReject}
      />
    </motion.div>
  );
}

export default ReviewerPanel;

