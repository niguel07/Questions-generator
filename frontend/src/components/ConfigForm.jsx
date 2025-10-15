import { useState } from 'react';
import { Card, CardContent, Typography, TextField, Slider, Box, Button } from '@mui/material';

function ConfigForm({ onGenerate, isGenerating }) {
  const [topic, setTopic] = useState('Cameroon');
  const [totalQuestions, setTotalQuestions] = useState(1000);

  const handleSliderChange = (event, newValue) => {
    setTotalQuestions(newValue);
  };

  const handleInputChange = (event) => {
    const value = event.target.value === '' ? 100 : Number(event.target.value);
    setTotalQuestions(Math.min(10000, Math.max(100, value)));
  };

  const handleGenerate = () => {
    if (topic.trim() && totalQuestions >= 100 && totalQuestions <= 10000) {
      onGenerate({ topic: topic.trim(), total_questions: totalQuestions });
    }
  };

  return (
    <Card sx={{ borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.12)' }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#1F2937' }}>
          ⚙️ Generation Settings
        </Typography>

        {/* Topic Input */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, color: '#6B7280', fontWeight: 500 }}>
            Topic
          </Typography>
          <TextField
            fullWidth
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter topic (e.g., Cameroon, Python Programming, World History)"
            variant="outlined"
            size="small"
            disabled={isGenerating}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
                '&:hover fieldset': {
                  borderColor: '#2563EB'
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#2563EB'
                }
              }
            }}
          />
          <Typography variant="caption" sx={{ color: '#9CA3AF', mt: 0.5, display: 'block' }}>
            Questions will be generated about this topic
          </Typography>
        </Box>

        {/* Question Count Slider */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, color: '#6B7280', fontWeight: 500 }}>
            Number of Questions: {totalQuestions.toLocaleString()}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Slider
              value={totalQuestions}
              onChange={handleSliderChange}
              min={100}
              max={10000}
              step={100}
              disabled={isGenerating}
              sx={{
                flex: 1,
                color: '#2563EB',
                '& .MuiSlider-thumb': {
                  '&:hover, &.Mui-focusVisible': {
                    boxShadow: '0 0 0 8px rgba(37, 99, 235, 0.16)'
                  }
                }
              }}
            />
            <TextField
              value={totalQuestions}
              onChange={handleInputChange}
              type="number"
              size="small"
              disabled={isGenerating}
              sx={{
                width: 100,
                '& .MuiOutlinedInput-root': {
                  borderRadius: '8px'
                }
              }}
              inputProps={{
                min: 100,
                max: 10000,
                step: 100
              }}
            />
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
              100 (minimum)
            </Typography>
            <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
              10,000 (maximum)
            </Typography>
          </Box>
        </Box>

        {/* Generate Button */}
        <Button
          fullWidth
          variant="contained"
          size="large"
          onClick={handleGenerate}
          disabled={isGenerating || !topic.trim()}
          sx={{
            bgcolor: '#2563EB',
            '&:hover': { bgcolor: '#1D4ED8' },
            textTransform: 'none',
            fontWeight: 600,
            py: 1.5,
            fontSize: '1rem'
          }}
        >
          {isGenerating ? '⏳ Generating...' : '🚀 Generate Questions'}
        </Button>

        {/* Info Text */}
        <Typography variant="caption" sx={{ color: '#9CA3AF', mt: 2, display: 'block', textAlign: 'center' }}>
          Estimated time: {Math.ceil(totalQuestions / 300)} - {Math.ceil(totalQuestions / 150)} minutes
        </Typography>
      </CardContent>
    </Card>
  );
}

export default ConfigForm;

