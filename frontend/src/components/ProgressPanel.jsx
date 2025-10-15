import { Card, CardContent, Typography, Box, LinearProgress, Button, Alert } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

function ProgressPanel({ progress, status, message, logs, error }) {
  const isCompleted = status === 'completed';
  const isError = status === 'error';
  const isGenerating = status === 'generating' || status === 'starting';

  const getStatusColor = () => {
    if (isError) return '#EF4444';
    if (isCompleted) return '#10B981';
    return '#2563EB';
  };

  const handleDownload = () => {
    window.open('http://localhost:8000/questions?limit=999999', '_blank');
  };

  return (
    <Card sx={{ borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.12)' }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1F2937' }}>
          📊 Generation Progress
        </Typography>

        {/* Status Message */}
        {status !== 'idle' && (
          <Box sx={{ mb: 2 }}>
            {isCompleted && (
              <Alert
                icon={<CheckCircleIcon />}
                severity="success"
                sx={{ borderRadius: '8px' }}
              >
                Generation completed successfully!
              </Alert>
            )}
            {isError && (
              <Alert
                icon={<ErrorIcon />}
                severity="error"
                sx={{ borderRadius: '8px' }}
              >
                {error || 'Generation failed'}
              </Alert>
            )}
            {isGenerating && (
              <Box sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="body2" sx={{ color: '#6B7280', mb: 1 }}>
                  {message || 'Processing...'}
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {/* Progress Bar */}
        {(isGenerating || isCompleted) && (
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: '#6B7280', fontWeight: 500 }}>
                {isCompleted ? 'Completed' : 'In Progress'}
              </Typography>
              <Typography variant="body2" sx={{ color: '#6B7280', fontWeight: 600 }}>
                {progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: '8px',
                backgroundColor: '#E5E7EB',
                '& .MuiLinearProgress-bar': {
                  borderRadius: '8px',
                  backgroundColor: getStatusColor()
                }
              }}
            />
          </Box>
        )}

        {/* Log Panel */}
        {logs && logs.length > 0 && (
          <Box
            sx={{
              backgroundColor: '#F9FAFB',
              borderRadius: '8px',
              p: 2,
              maxHeight: '300px',
              overflow: 'auto',
              border: '1px solid #E5E7EB',
              mb: 2
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: '#6B7280',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 1,
                display: 'block'
              }}
            >
              Activity Log
            </Typography>
            {logs.map((log, index) => (
              <Typography
                key={index}
                component="pre"
                sx={{
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                  color: '#374151',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  mb: 0.5
                }}
              >
                {log}
              </Typography>
            ))}
          </Box>
        )}

        {/* Download Button */}
        {isCompleted && (
          <Button
            fullWidth
            variant="contained"
            size="large"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
            sx={{
              bgcolor: '#10B981',
              '&:hover': { bgcolor: '#059669' },
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            Download Questions JSON
          </Button>
        )}

        {/* Idle State */}
        {status === 'idle' && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
              Upload files and configure settings to start generation
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default ProgressPanel;

