import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Menu,
  MenuItem,
  Typography,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { motion } from 'framer-motion';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import HistoryIcon from '@mui/icons-material/History';
import DownloadIcon from '@mui/icons-material/Download';
import UploadIcon from '@mui/icons-material/Upload';
import axios from 'axios';
import AuthDialog from './AuthDialog';

const API_BASE_URL = 'http://localhost:8000';

function UserMenu() {
  const [anchorEl, setAnchorEl] = useState(null);
  const [user, setUser] = useState(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
        fetchUserStats(JSON.parse(storedUser).username);
      } catch (e) {
        localStorage.removeItem('user');
        localStorage.removeItem('session_token');
      }
    }
  }, []);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    fetchUserStats(userData.username);
  };

  const handleLogout = async () => {
    try {
      const sessionToken = localStorage.getItem('session_token');
      if (sessionToken) {
        await axios.post(`${API_BASE_URL}/auth/logout`, {
          session_token: sessionToken
        });
      }
      
      localStorage.removeItem('user');
      localStorage.removeItem('session_token');
      setUser(null);
      setStats(null);
      setSessions([]);
      handleClose();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const fetchUserStats = async (username) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/user-stats?username=${username}`);
      setStats(response.data);
    } catch (error) {
      console.error('Stats error:', error);
    }
  };

  const fetchSessions = async () => {
    if (!user) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/sessions?username=${user}&limit=50`);
      setSessions(response.data.sessions || []);
      setHistoryOpen(true);
    } catch (error) {
      console.error('Sessions error:', error);
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `questions_export_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      handleClose();
    } catch (error) {
      console.error('Export error:', error);
      alert('No questions to export');
    }
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post(`${API_BASE_URL}/import`, formData);
        alert(response.data.message);
        handleClose();
      } catch (error) {
        console.error('Import error:', error);
        alert('Import failed');
      }
    };
    input.click();
  };

  return (
    <>
      <Box>
        {user ? (
          <Button
            variant="contained"
            startIcon={<PersonIcon />}
            onClick={handleClick}
            sx={{
              bgcolor: 'white',
              color: '#2563EB',
              '&:hover': { bgcolor: '#F9FAFB' },
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            {user.username || user}
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={() => setAuthOpen(true)}
            sx={{
              bgcolor: 'white',
              color: '#2563EB',
              '&:hover': { bgcolor: '#F9FAFB' },
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            Sign Up / Login
          </Button>
        )}
      </Box>

      {/* User Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            borderRadius: '8px',
            minWidth: 250,
            mt: 1
          }
        }}
      >
        {stats && (
          <Box sx={{ px: 2, py: 1.5 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#1F2937' }}>
              {user}
            </Typography>
            <Typography variant="caption" sx={{ color: '#6B7280' }}>
              {stats.total_sessions} sessions • {stats.total_questions_generated} questions
            </Typography>
          </Box>
        )}
        <Divider />
        <MenuItem onClick={fetchSessions}>
          <HistoryIcon fontSize="small" sx={{ mr: 1, color: '#6B7280' }} />
          View History
        </MenuItem>
        <MenuItem onClick={handleExport}>
          <DownloadIcon fontSize="small" sx={{ mr: 1, color: '#6B7280' }} />
          Export Dataset
        </MenuItem>
        <MenuItem onClick={handleImport}>
          <UploadIcon fontSize="small" sx={{ mr: 1, color: '#6B7280' }} />
          Import Dataset
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <LogoutIcon fontSize="small" sx={{ mr: 1, color: '#EF4444' }} />
          <Typography sx={{ color: '#EF4444' }}>Logout</Typography>
        </MenuItem>
      </Menu>

      {/* Auth Dialog (Signup/Login) */}
      <AuthDialog
        open={authOpen}
        onClose={() => setAuthOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* History Dialog */}
      <Dialog
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: '12px' } }}
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Generation History
          </Typography>
          <Typography variant="body2" sx={{ color: '#6B7280', mt: 0.5 }}>
            {user?.username || user}'s generation sessions
          </Typography>
        </DialogTitle>
        <DialogContent>
          {sessions.length === 0 ? (
            <Typography variant="body2" sx={{ color: '#9CA3AF', textAlign: 'center', py: 4 }}>
              No generation history yet
            </Typography>
          ) : (
            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Topics</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Questions</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Quality</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sessions.map((session, idx) => (
                    <TableRow key={idx}>
                      <TableCell>
                        {new Date(session.timestamp).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Box display="flex" flexWrap="wrap" gap={0.5}>
                          {(session.topics || []).map((topic, i) => (
                            <Chip
                              key={i}
                              label={topic}
                              size="small"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell>{session.questions_generated || 0}</TableCell>
                      <TableCell sx={{ color: '#2563EB', fontWeight: 600 }}>
                        {session.avg_quality?.toFixed(2) || 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default UserMenu;

