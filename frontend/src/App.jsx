import { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, Tabs, Tab, Alert } from '@mui/material';
import { motion } from 'framer-motion';
import axios from 'axios';
import StatsCard from './components/StatsCard';
import ChartCard from './components/ChartCard';
import ReportPanel from './components/ReportPanel';
import UploadCard from './components/UploadCard';
import ConfigForm from './components/ConfigForm';
import ProgressPanel from './components/ProgressPanel';
import CompletionModal from './components/CompletionModal';
import ReviewerPanel from './components/ReviewerPanel';
import UserMenu from './components/UserMenu';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  // Dashboard state
  const [summary, setSummary] = useState(null);
  const [validationReport, setValidationReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Generation state
  const [currentTab, setCurrentTab] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [progress, setProgress] = useState({
    status: 'idle',
    progress: 0,
    message: '',
    logs: [],
    error: null
  });
  const [pollInterval, setPollInterval] = useState(null);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [completionData, setCompletionData] = useState(null);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    if (currentTab !== 0) return; // Only fetch when on dashboard tab
    
    setLoading(true);
    setError(null);
    
    try {
      const summaryResponse = await axios.get(`${API_BASE_URL}/summary`);
      setSummary(summaryResponse.data);
      
      const reportResponse = await axios.get(`${API_BASE_URL}/validation-report`);
      setValidationReport(reportResponse.data);
      
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.response?.data?.detail || 'Failed to fetch data. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch generation progress
  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/progress`);
      setProgress(response.data);
      
      // If completed or error, stop polling
      if (response.data.status === 'completed' || response.data.status === 'error') {
        setIsGenerating(false);
        if (pollInterval) {
          clearInterval(pollInterval);
          setPollInterval(null);
        }
        
        // Show completion modal if completed
        if (response.data.status === 'completed') {
          setTimeout(async () => {
            const summaryData = await axios.get(`${API_BASE_URL}/summary`);
            setCompletionData({
              totalQuestions: summaryData.data.total_questions,
              avgQuality: summaryData.data.avg_quality_score
            });
            setShowCompletionModal(true);
            fetchDashboardData();
          }, 1000);
        }
      }
    } catch (err) {
      console.error('Error fetching progress:', err);
    }
  };

  // Fetch uploaded files
  const fetchUploadedFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files`);
      setUploadedFiles(response.data.files || []);
    } catch (err) {
      console.error('Error fetching files:', err);
    }
  };

  // Handle file upload
  const handleFilesUploaded = (result) => {
    if (result.uploaded && result.uploaded.length > 0) {
      alert(`Successfully uploaded ${result.uploaded.length} file(s)!`);
      fetchUploadedFiles(); // Refresh file list
    }
    if (result.errors && result.errors.length > 0) {
      alert(`Errors: ${result.errors.join(', ')}`);
    }
  };

  // Handle generation start
  const handleGenerate = async (config) => {
    try {
      setIsGenerating(true);
      
      const response = await axios.post(`${API_BASE_URL}/generate`, {
        topics: config.topics,  // Multi-topic support
        total_questions: config.total_questions
      });
      
      // Start polling for progress
      const interval = setInterval(fetchProgress, 2000);
      setPollInterval(interval);
      
    } catch (err) {
      setIsGenerating(false);
      alert(err.response?.data?.detail || 'Failed to start generation');
    }
  };

  // Handle completion modal actions
  const handleDownload = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `questions_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Close modal after download
      setShowCompletionModal(false);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file. Please try again.');
    }
  };

  const handleRestart = () => {
    setShowCompletionModal(false);
    setCompletionData(null);
    setProgress({
      status: 'idle',
      progress: 0,
      message: '',
      logs: [],
      error: null
    });
    // Switch to Generate tab
    setCurrentTab(1);
  };

  // Tab change handler
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  // Initial load and auto-refresh for dashboard
  useEffect(() => {
    if (currentTab === 0) {
      fetchDashboardData();
      const interval = setInterval(fetchDashboardData, 60000); // Refresh every 60 seconds
      return () => clearInterval(interval);
    } else if (currentTab === 1) {
      fetchUploadedFiles(); // Fetch uploaded files when on generate tab
    }
  }, [currentTab]);

  // Cleanup poll interval on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <Container maxWidth="lg">
          <Box display="flex" justifyContent="space-between" alignItems="center" py={2}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Typography variant="h4" component="h1" sx={{ fontWeight: 700, color: 'white' }}>
                Question Generator AI
              </Typography>
            </motion.div>
            <Box display="flex" gap={2} alignItems="center">
              <Button
                variant="contained"
                onClick={fetchDashboardData}
                disabled={loading || currentTab !== 0}
                sx={{ 
                  bgcolor: 'white', 
                  color: '#2563EB',
                  '&:hover': { bgcolor: '#F9FAFB' },
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                🔄 Refresh
              </Button>
              <UserMenu />
            </Box>
          </Box>
          
          {/* Tabs */}
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            sx={{
              '& .MuiTab-root': {
                color: 'rgba(255,255,255,0.7)',
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 500,
                '&.Mui-selected': {
                  color: 'white'
                }
              },
              '& .MuiTabs-indicator': {
                backgroundColor: 'white'
              }
            }}
          >
            <Tab label="📊 Dashboard" />
            <Tab label="🚀 Generate" />
            <Tab label="🤖 AI Review" />
          </Tabs>
        </Container>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <Container maxWidth="lg">
          {/* Dashboard Tab */}
          {currentTab === 0 && (
            <>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {summary && (
                <>
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
              )}
            </>
          )}

          {/* Generate Tab */}
          {currentTab === 1 && (
            <Box maxWidth="800px" mx="auto">
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, color: '#1F2937' }}>
                Generate New Questions
              </Typography>

              {/* Upload Section */}
              <Box mb={3}>
                <UploadCard onFilesUploaded={handleFilesUploaded} />
              </Box>

              {/* Configuration Section */}
              <Box mb={3}>
                <ConfigForm 
                  onGenerate={handleGenerate} 
                  isGenerating={isGenerating} 
                  hasUploadedFiles={uploadedFiles.length > 0}
                />
              </Box>

              {/* Progress Section */}
              <Box>
                <ProgressPanel
                  progress={progress.progress}
                  status={progress.status}
                  message={progress.message}
                  logs={progress.logs}
                  error={progress.error}
                />
              </Box>
            </Box>
          )}

          {/* AI Review Tab */}
          {currentTab === 2 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Box maxWidth="1200px" mx="auto">
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, color: '#1F2937' }}>
                  AI-Powered Question Review
                </Typography>
                <ReviewerPanel />
              </Box>
            </motion.div>
          )}
        </Container>
      </main>

      {/* Completion Modal */}
      <CompletionModal
        open={showCompletionModal}
        onClose={() => setShowCompletionModal(false)}
        totalQuestions={completionData?.totalQuestions}
        avgQuality={completionData?.avgQuality}
        onDownload={handleDownload}
        onRestart={handleRestart}
      />

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
