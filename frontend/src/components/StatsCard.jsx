import { Card, CardContent, Typography, Box } from '@mui/material';

function StatsCard({ title, value, subtitle, icon }) {
  return (
    <Card 
      sx={{ 
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 6px rgba(37,99,235,0.15)'
        }
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography 
              variant="subtitle2" 
              sx={{ color: '#6B7280', mb: 1, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.5px' }}
            >
              {title}
            </Typography>
            <Typography 
              variant="h3" 
              sx={{ fontWeight: 700, color: '#2563EB', mb: subtitle ? 0.5 : 0 }}
            >
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ fontSize: '3rem', opacity: 0.3 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default StatsCard;

