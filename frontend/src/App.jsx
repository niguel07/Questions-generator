import { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, CircularProgress, Alert } from '@mui/material';
import axios from 'axios';
import StatsCard from './components/StatsCard';
import ChartCard from './components/ChartCard';
import ReportPanel from './components/ReportPanel';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [summary, setSummary] = useState(null);
  const [validationReport, setValidationReport] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch summary statistics
      const summaryResponse = await axios.get(`${API_BASE_URL}/summary`);
      setSummary(summaryResponse.data);
      
      // Fetch validation report
      const reportResponse = await axios.get(`${API_BASE_URL}/validation-report`);
      setValidationReport(reportResponse.data);
      
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.response?.data?.detail || 'Failed to fetch data. Make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchData, 60000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <Container maxWidth="lg">
          <Box display="flex" justifyContent="space-between" alignItems="center" py={2}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700, color: 'white' }}>
              Question Generator Dashboard
            </Typography>
            <Button
              variant="contained"
              onClick={fetchData}
              disabled={loading}
              sx={{ 
                bgcolor: 'white', 
                color: '#2563EB',
                '&:hover': { bgcolor: '#F9FAFB' }
              }}
            >
              🔄 Refresh
            </Button>
          </Box>
        </Container>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <Container maxWidth="lg">
          {loading && !summary ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
              <CircularProgress size={60} sx={{ color: '#2563EB' }} />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mt: 3 }}>
              {error}
            </Alert>
          ) : summary ? (
            <>
              {/* Last Update Info */}
              {lastUpdate && (
                <Typography variant="body2" sx={{ color: '#6B7280', mb: 2, textAlign: 'right' }}>
                  Last updated: {lastUpdate.toLocaleTimeString()}
                </Typography>
              )}

              {/* Stats Cards */}
              <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: '1fr 1fr' }} gap={3} mb={4}>
                <StatsCard
                  title="Total Questions"
                  value={summary.total_questions.toLocaleString()}
                  icon="📊"
                />
                <StatsCard
                  title="Average Quality Score"
                  value={summary.avg_quality_score.toFixed(3)}
                  subtitle="Out of 1.000"
                  icon="⭐"
                />
              </Box>

              {/* Charts */}
              <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: '1fr 1fr' }} gap={3} mb={4}>
                <ChartCard
                  title="Category Distribution"
                  data={summary.categories}
                  type="bar"
                />
                <ChartCard
                  title="Difficulty Distribution"
                  data={summary.difficulty}
                  type="pie"
                />
              </Box>

              {/* Quality Distribution */}
              <Box mb={4}>
                <ChartCard
                  title="Quality Distribution"
                  data={summary.quality_distribution}
                  type="bar"
                />
              </Box>

              {/* Validation Report */}
              <ReportPanel report={validationReport} />
            </>
          ) : null}
        </Container>
      </main>

      {/* Footer */}
      <footer className="footer">
        <Container maxWidth="lg">
          <Typography variant="body2" align="center" sx={{ py: 3, color: '#6B7280' }}>
            Niguel Clark © 2025
          </Typography>
        </Container>
      </footer>
    </div>
  );
}

export default App;
