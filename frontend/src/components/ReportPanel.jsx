import { Card, CardContent, Typography, Box } from '@mui/material';

function ReportPanel({ report }) {
  return (
    <Card 
      sx={{ 
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
        backgroundColor: '#F9FAFB'
      }}
    >
      <CardContent>
        <Typography 
          variant="h6" 
          sx={{ mb: 2, fontWeight: 600, color: '#1F2937' }}
        >
          Validation Report
        </Typography>
        
        <Box 
          sx={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            p: 2,
            maxHeight: '400px',
            overflow: 'auto',
            border: '1px solid #E5E7EB'
          }}
        >
          <Typography 
            component="pre" 
            sx={{ 
              fontFamily: 'monospace',
              fontSize: '0.85rem',
              color: '#374151',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              margin: 0
            }}
          >
            {report || 'No validation report available.'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default ReportPanel;

