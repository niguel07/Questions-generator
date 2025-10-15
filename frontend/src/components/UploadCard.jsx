import { useState, useRef } from 'react';
import { Card, CardContent, Typography, Box, Button, List, ListItem, ListItemText, IconButton, Chip } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

function UploadCard({ onFilesUploaded }) {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    );
    
    if (droppedFiles.length > 0) {
      setFiles(prev => [...prev, ...droppedFiles]);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (result.uploaded && result.uploaded.length > 0) {
        onFilesUploaded && onFilesUploaded(result);
        setFiles([]);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload files. Make sure the backend server is running.');
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Card sx={{ borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.12)' }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1F2937' }}>
          📚 Upload PDF Books
        </Typography>

        {/* Drag and Drop Area */}
        <Box
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          sx={{
            border: `2px dashed ${isDragging ? '#2563EB' : '#D1D5DB'}`,
            borderRadius: '8px',
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragging ? '#EFF6FF' : '#F9FAFB',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: '#2563EB',
              backgroundColor: '#EFF6FF'
            }
          }}
        >
          <CloudUploadIcon sx={{ fontSize: 48, color: '#9CA3AF', mb: 2 }} />
          <Typography variant="body1" sx={{ color: '#6B7280', mb: 1 }}>
            Drag and drop PDF files here
          </Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
            or click to browse (max 50MB per file)
          </Typography>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </Box>

        {/* File List */}
        {files.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#6B7280' }}>
              Selected Files ({files.length})
            </Typography>
            <List dense>
              {files.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <IconButton edge="end" onClick={() => handleRemoveFile(index)} size="small">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  }
                  sx={{ 
                    backgroundColor: '#F9FAFB',
                    borderRadius: '4px',
                    mb: 0.5
                  }}
                >
                  <ListItemText
                    primary={file.name}
                    secondary={formatFileSize(file.size)}
                    primaryTypographyProps={{ fontSize: '0.9rem' }}
                    secondaryTypographyProps={{ fontSize: '0.75rem' }}
                  />
                </ListItem>
              ))}
            </List>

            <Button
              fullWidth
              variant="contained"
              onClick={handleUpload}
              disabled={uploading}
              sx={{
                mt: 2,
                bgcolor: '#2563EB',
                '&:hover': { bgcolor: '#1D4ED8' },
                textTransform: 'none',
                fontWeight: 600
              }}
            >
              {uploading ? 'Uploading...' : `Upload ${files.length} File${files.length > 1 ? 's' : ''}`}
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default UploadCard;

