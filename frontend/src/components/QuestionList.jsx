import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import RateReviewIcon from '@mui/icons-material/RateReview';

function QuestionList({ questions, onReview }) {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return '#10B981';
      case 'medium':
        return '#F59E0B';
      case 'hard':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  return (
    <TableContainer
      component={Paper}
      sx={{
        maxHeight: 600,
        borderRadius: '8px',
        border: '1px solid #E5E7EB'
      }}
    >
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600, bgcolor: '#F9FAFB', width: '5%' }}>#</TableCell>
            <TableCell sx={{ fontWeight: 600, bgcolor: '#F9FAFB', width: '45%' }}>Question</TableCell>
            <TableCell sx={{ fontWeight: 600, bgcolor: '#F9FAFB', width: '15%' }}>Category</TableCell>
            <TableCell sx={{ fontWeight: 600, bgcolor: '#F9FAFB', width: '12%' }}>Difficulty</TableCell>
            <TableCell sx={{ fontWeight: 600, bgcolor: '#F9FAFB', width: '10%' }}>Quality</TableCell>
            <TableCell sx={{ fontWeight: 600, bgcolor: '#F9FAFB', width: '13%' }}>Action</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {questions.map((q, index) => (
            <motion.tr
              key={index}
              component={TableRow}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.02 }}
              sx={{
                '&:hover': {
                  bgcolor: '#F9FAFB'
                }
              }}
            >
              <TableCell>{index + 1}</TableCell>
              <TableCell sx={{ fontSize: '0.875rem' }}>
                {q.question?.substring(0, 80)}{q.question?.length > 80 ? '...' : ''}
              </TableCell>
              <TableCell>
                <Chip
                  label={q.category || 'Unknown'}
                  size="small"
                  sx={{
                    bgcolor: '#EFF6FF',
                    color: '#2563EB',
                    fontWeight: 500,
                    fontSize: '0.75rem'
                  }}
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={q.difficulty || 'Unknown'}
                  size="small"
                  sx={{
                    bgcolor: `${getDifficultyColor(q.difficulty)}15`,
                    color: getDifficultyColor(q.difficulty),
                    fontWeight: 500,
                    fontSize: '0.75rem'
                  }}
                />
              </TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#2563EB' }}>
                {q.quality_score?.toFixed(2) || 'N/A'}
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<RateReviewIcon fontSize="small" />}
                  onClick={() => onReview(q, index)}
                  sx={{
                    borderColor: '#D1D5DB',
                    color: '#6B7280',
                    textTransform: 'none',
                    fontSize: '0.75rem',
                    '&:hover': {
                      borderColor: '#2563EB',
                      color: '#2563EB',
                      bgcolor: '#EFF6FF'
                    }
                  }}
                >
                  Review
                </Button>
              </TableCell>
            </motion.tr>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default QuestionList;

