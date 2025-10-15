import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Tabs,
  Tab,
  Alert,
  InputAdornment,
  IconButton
} from '@mui/material';
import { motion } from 'framer-motion';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import LoginIcon from '@mui/icons-material/Login';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function AuthDialog({ open, onClose, onSuccess }) {
  const [tab, setTab] = useState(0); // 0 = Login, 1 = Signup
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Login form
  const [loginData, setLoginData] = useState({
    username_or_email: '',
    password: ''
  });
  
  // Signup form
  const [signupData, setSignupData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: ''
  });

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setError(null);
  };

  const handleLogin = async () => {
    setError(null);
    
    if (!loginData.username_or_email || !loginData.password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, loginData);
      
      if (response.data.success) {
        // Store session token
        localStorage.setItem('session_token', response.data.session_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        onSuccess && onSuccess(response.data.user);
        onClose();
      } else {
        setError(response.data.error || 'Login failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    setError(null);
    
    // Validation
    if (!signupData.username || !signupData.email || !signupData.password) {
      setError('Please fill in all required fields');
      return;
    }
    
    if (signupData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }
    
    if (!signupData.email.includes('@')) {
      setError('Please enter a valid email');
      return;
    }
    
    if (signupData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    if (signupData.password !== signupData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/signup`, {
        username: signupData.username,
        email: signupData.email,
        password: signupData.password,
        full_name: signupData.full_name || signupData.username
      });
      
      if (response.data.success) {
        // Store session token
        localStorage.setItem('session_token', response.data.session_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        onSuccess && onSuccess(response.data.user);
        onClose();
      } else {
        setError(response.data.error || 'Signup failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '12px'
        }
      }}
    >
      <DialogTitle sx={{ pb: 0 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, textAlign: 'center', color: '#1F2937' }}>
          Welcome to Question Generator AI
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs
            value={tab}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem'
              }
            }}
          >
            <Tab label="Login" icon={<LoginIcon />} iconPosition="start" />
            <Tab label="Sign Up" icon={<PersonAddIcon />} iconPosition="start" />
          </Tabs>
        </Box>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Alert severity="error" sx={{ mb: 2, borderRadius: '8px' }}>
              {error}
            </Alert>
          </motion.div>
        )}

        {/* Login Form */}
        {tab === 0 && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Username or Email"
                value={loginData.username_or_email}
                onChange={(e) => setLoginData({ ...loginData, username_or_email: e.target.value })}
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                variant="outlined"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Box>
          </motion.div>
        )}

        {/* Signup Form */}
        {tab === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box component="form" sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Username *"
                value={signupData.username}
                onChange={(e) => setSignupData({ ...signupData, username: e.target.value })}
                variant="outlined"
                sx={{ mb: 2 }}
                helperText="At least 3 characters"
              />
              <TextField
                fullWidth
                label="Email *"
                type="email"
                value={signupData.email}
                onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Full Name (Optional)"
                value={signupData.full_name}
                onChange={(e) => setSignupData({ ...signupData, full_name: e.target.value })}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Password *"
                type={showPassword ? 'text' : 'password'}
                value={signupData.password}
                onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                variant="outlined"
                sx={{ mb: 2 }}
                helperText="At least 6 characters"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              <TextField
                fullWidth
                label="Confirm Password *"
                type={showPassword ? 'text' : 'password'}
                value={signupData.confirmPassword}
                onChange={(e) => setSignupData({ ...signupData, confirmPassword: e.target.value })}
                onKeyPress={(e) => e.key === 'Enter' && handleSignup()}
                variant="outlined"
              />
            </Box>
          </motion.div>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <Button
          onClick={onClose}
          disabled={loading}
          sx={{
            textTransform: 'none',
            color: '#6B7280'
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={tab === 0 ? handleLogin : handleSignup}
          disabled={loading}
          variant="contained"
          sx={{
            bgcolor: '#2563EB',
            '&:hover': { bgcolor: '#1D4ED8' },
            textTransform: 'none',
            fontWeight: 600,
            px: 4
          }}
        >
          {loading ? 'Processing...' : tab === 0 ? 'Login' : 'Create Account'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default AuthDialog;

