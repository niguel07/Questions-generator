import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  CircularProgress,
  Divider,
  Chip,
  Alert
} from '@mui/material';
import { motion } from 'framer-motion';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import StarIcon from '@mui/icons-material/Star';

function ReviewModal({ open, onClose, question, reviewing, reviewResult, onApply, onReject }) {
  if (!question) return null;

  const getRatingColor = (rating) => {
    if (rating >= 0.8) return '#10B981';
    if (rating >= 0.6) return '#F59E0B';
    return '#EF4444';
  };

  const renderReviewContent = () => {
    if (reviewing) {
      return (
        <Box display="flex" flexDirection="column" alignItems="center" py={4}>
          <CircularProgress size={60} sx={{ color: '#2563EB', mb: 2 }} />
          <Typography variant="body1" sx={{ color: '#6B7280' }}>
            Claude is reviewing this question...
          </Typography>
          <Typography variant="caption" sx={{ color: '#9CA3AF', mt: 1 }}>
            This may take a few seconds
          </Typography>
        </Box>
      );
    }

    if (!reviewResult) return null;

    if (!reviewResult.success) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {reviewResult.error || 'Failed to review question'}
        </Alert>
      );
    }

    const review = reviewResult.review;

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Rating */}
        <Box sx={{ textAlign: 'center', mb: 3, p: 3, bgcolor: '#F9FAFB', borderRadius: '8px' }}>
          <Box display="flex" alignItems="center" justifyContent="center" gap={1} mb={1}>
            <StarIcon sx={{ color: getRatingColor(review.rating), fontSize: 32 }} />
            <Typography variant="h3" sx={{ fontWeight: 700, color: getRatingColor(review.rating) }}>
              {(review.rating * 100).toFixed(0)}%
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ color: '#6B7280' }}>
            Overall Quality Rating
          </Typography>
        </Box>

        {/* Feedback */}
        <Box mb={3}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#1F2937' }}>
            📝 Claude's Feedback
          </Typography>
          <Box sx={{ p: 2, bgcolor: '#F9FAFB', borderRadius: '8px', border: '1px solid #E5E7EB' }}>
            <Typography variant="body2" sx={{ color: '#374151', lineHeight: 1.6 }}>
              {review.feedback}
            </Typography>
          </Box>
        </Box>

        {/* Issues */}
        {review.issues && review.issues.length > 0 && (
          <Box mb={3}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#1F2937' }}>
              ⚠️ Issues Identified
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {review.issues.map((issue, idx) => (
                <Chip
                  key={idx}
                  label={issue}
                  size="small"
                  sx={{
                    bgcolor: '#FEF2F2',
                    color: '#EF4444',
                    border: '1px solid #FCA5A5'
                  }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Suggested Fix */}
        {review.suggested_fix && Object.values(review.suggested_fix).some(v => v !== null) && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#1F2937' }}>
                💡 Suggested Improvements
              </Typography>
              
              {review.suggested_fix.question && (
                <Box mb={2}>
                  <Typography variant="caption" sx={{ color: '#6B7280', fontWeight: 600, textTransform: 'uppercase' }}>
                    Question
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#374151', mt: 0.5 }}>
                    {review.suggested_fix.question}
                  </Typography>
                </Box>
              )}

              {review.suggested_fix.options && (
                <Box mb={2}>
                  <Typography variant="caption" sx={{ color: '#6B7280', fontWeight: 600, textTransform: 'uppercase' }}>
                    Options
                  </Typography>
                  <Box sx={{ mt: 0.5 }}>
                    {Object.entries(review.suggested_fix.options).map(([key, value]) => (
                      <Typography key={key} variant="body2" sx={{ color: '#374151', ml: 2 }}>
                        {key}) {value}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              )}

              {review.suggested_fix.explanation && (
                <Box mb={2}>
                  <Typography variant="caption" sx={{ color: '#6B7280', fontWeight: 600, textTransform: 'uppercase' }}>
                    Explanation
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#374151', mt: 0.5 }}>
                    {review.suggested_fix.explanation}
                  </Typography>
                </Box>
              )}
            </Box>
          </>
        )}
      </motion.div>
    );
  };

  const hasSuggestions = reviewResult?.success && reviewResult?.review?.suggested_fix && 
    Object.values(reviewResult.review.suggested_fix).some(v => v !== null);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '12px',
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ borderBottom: '1px solid #E5E7EB' }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          AI Question Review
        </Typography>
        <Typography variant="body2" sx={{ color: '#6B7280', mt: 0.5 }}>
          {question.question}
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        {renderReviewContent()}
      </DialogContent>

      <DialogActions sx={{ borderTop: '1px solid #E5E7EB', p: 2, gap: 1 }}>
        {!reviewing && reviewResult?.success && hasSuggestions && (
          <Button
            variant="contained"
            startIcon={<CheckCircleIcon />}
            onClick={() => onApply(reviewResult.review.suggested_fix)}
            sx={{
              bgcolor: '#10B981',
              '&:hover': { bgcolor: '#059669' },
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            Apply Suggestions
          </Button>
        )}
        <Button
          variant="outlined"
          startIcon={reviewing ? null : <CancelIcon />}
          onClick={onReject}
          disabled={reviewing}
          sx={{
            borderColor: '#D1D5DB',
            color: '#6B7280',
            '&:hover': {
              borderColor: '#9CA3AF',
              bgcolor: '#F9FAFB'
            },
            textTransform: 'none',
            fontWeight: 600
          }}
        >
          {reviewing ? 'Please wait...' : 'Close'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ReviewModal;

