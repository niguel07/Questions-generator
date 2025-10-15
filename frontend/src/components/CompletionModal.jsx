import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box } from '@mui/material';
import { motion } from 'framer-motion';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';

function CompletionModal({ open, onClose, totalQuestions, avgQuality, onDownload, onRestart }) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '16px',
          p: 2
        }
      }}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <DialogTitle sx={{ textAlign: 'center', pt: 3 }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
          >
            <CheckCircleIcon sx={{ fontSize: 80, color: '#10B981', mb: 2 }} />
          </motion.div>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#1F2937' }}>
            Generation Complete!
          </Typography>
        </DialogTitle>

        <DialogContent sx={{ textAlign: 'center', py: 3 }}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h2" sx={{ fontWeight: 700, color: '#2563EB', mb: 1 }}>
              {totalQuestions?.toLocaleString() || 0}
            </Typography>
            <Typography variant="body1" sx={{ color: '#6B7280' }}>
              Questions Generated
            </Typography>
          </Box>

          {avgQuality && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#10B981', mb: 0.5 }}>
                {avgQuality.toFixed(3)}
              </Typography>
              <Typography variant="body2" sx={{ color: '#6B7280' }}>
                Average Quality Score
              </Typography>
            </Box>
          )}

          <Typography variant="body2" sx={{ color: '#9CA3AF', mt: 3 }}>
            Your questions have been validated, scored, and are ready for download!
          </Typography>
        </DialogContent>

        <DialogActions sx={{ justifyContent: 'center', gap: 2, pb: 3, px: 3 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<DownloadIcon />}
            onClick={onDownload}
            sx={{
              bgcolor: '#2563EB',
              '&:hover': { bgcolor: '#1D4ED8' },
              textTransform: 'none',
              fontWeight: 600,
              px: 4,
              py: 1.5,
              transition: 'all 0.2s'
            }}
          >
            Download JSON
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<RefreshIcon />}
            onClick={onRestart}
            sx={{
              borderColor: '#D1D5DB',
              color: '#6B7280',
              '&:hover': {
                borderColor: '#2563EB',
                bgcolor: '#EFF6FF',
                color: '#2563EB'
              },
              textTransform: 'none',
              fontWeight: 600,
              px: 4,
              py: 1.5,
              transition: 'all 0.2s'
            }}
          >
            Start New Session
          </Button>
        </DialogActions>
      </motion.div>
    </Dialog>
  );
}

export default CompletionModal;

