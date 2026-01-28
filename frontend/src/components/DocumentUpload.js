import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
  Info,
  Refresh
} from '@mui/icons-material';
import { uploadPDFWithProgress, getUploadProgress } from '../services/api';

const DocumentUpload = ({ onUploadComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);
    setUploadProgress({ progress: 0, message: 'Starting upload...' });

    try {
      const response = await uploadPDFWithProgress(file);
      
      if (response.error) {
        setError(response.error);
        setUploading(false);
        return;
      }

      const taskId = response.task_id;
      
      // Poll for progress
      const pollProgress = async () => {
        try {
          const progressData = await getUploadProgress(taskId);
          setUploadProgress(progressData);
          
          if (progressData.completed) {
            if (progressData.error) {
              setError(progressData.error);
            } else {
              setUploadResult({
                filename: file.name,
                chunks_count: progressData.details?.chunks_count || 0,
                pages_count: progressData.details?.pages_count || 0,
                status: 'completed'
              });
              onUploadComplete && onUploadComplete();
            }
            setUploading(false);
          } else {
            // Continue polling
            setTimeout(pollProgress, 2000);
          }
        } catch (err) {
          setError('Failed to get upload progress: ' + err.message);
          setUploading(false);
        }
      };

      // Start polling
      setTimeout(pollProgress, 1000);
      
    } catch (err) {
      setError('Upload failed: ' + err.message);
      setUploading(false);
    }
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const resetUpload = () => {
    setUploading(false);
    setUploadProgress(null);
    setUploadResult(null);
    setError(null);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider', flexShrink: 0 }}>
        <Typography variant="h5" gutterBottom>
          Document Upload
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Upload your clinical protocol PDF for AI analysis
        </Typography>
      </Box>

      <Box sx={{ 
        flex: 1, 
        p: 3,
        minHeight: 0
      }}>
        {/* Upload Area */}
        {!uploading && !uploadResult && (
          <Paper
            sx={{
              p: 4,
              textAlign: 'center',
              border: dragActive ? '2px dashed #2563eb' : '2px dashed #e2e8f0',
              backgroundColor: dragActive ? '#f0f9ff' : 'transparent',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: '#2563eb',
                backgroundColor: '#f8fafc'
              }
            }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <CloudUpload sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Drop your PDF here or click to browse
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Supports PDF files up to 50MB
            </Typography>
            <Button variant="contained" sx={{ mt: 2 }}>
              Select PDF File
            </Button>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </Paper>
        )}

        {/* Upload Progress */}
        {uploading && uploadProgress && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <CloudUpload sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Processing Document
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {uploadProgress.message}
              </Typography>
            </Box>
            
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress.progress || 0} 
              sx={{ mb: 2, height: 8, borderRadius: 4 }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {uploadProgress.stage || 'Processing'}
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {uploadProgress.progress || 0}%
              </Typography>
            </Box>

            {uploadProgress.details && (
              <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Progress Details:
                </Typography>
                <List dense>
                  {uploadProgress.details.pages_count && (
                    <ListItem sx={{ py: 0 }}>
                      <ListItemText 
                        primary={`Pages extracted: ${uploadProgress.details.pages_count}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  )}
                  {uploadProgress.details.chunks_count && (
                    <ListItem sx={{ py: 0 }}>
                      <ListItemText 
                        primary={`Text chunks: ${uploadProgress.details.chunks_count}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  )}
                  {uploadProgress.details.embedded_chunks && (
                    <ListItem sx={{ py: 0 }}>
                      <ListItemText 
                        primary={`Embeddings created: ${uploadProgress.details.embedded_chunks}/${uploadProgress.details.chunks_count}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  )}
                </List>
              </Box>
            )}
          </Paper>
        )}

        {/* Upload Success */}
        {uploadResult && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Document Processed Successfully!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your protocol is ready for AI analysis
              </Typography>
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary.main" fontWeight="bold">
                      {uploadResult.pages_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Pages Processed
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main" fontWeight="bold">
                      {uploadResult.chunks_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Text Chunks
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="info.main" fontWeight="bold">
                      <CheckCircle />
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Ready for Analysis
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>{uploadResult.filename}</strong> has been successfully processed. 
                You can now use the Chat Assistant and Document Analysis features.
              </Typography>
            </Alert>

            <Box sx={{ textAlign: 'center' }}>
              <Button variant="outlined" onClick={resetUpload} startIcon={<Refresh />}>
                Upload Another Document
              </Button>
            </Box>
          </Paper>
        )}

        {/* Error State */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
            <Button onClick={resetUpload} sx={{ ml: 2 }}>
              Try Again
            </Button>
          </Alert>
        )}

        {/* Guidelines */}
        <Paper sx={{ p: 3, mt: 3, backgroundColor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Upload Guidelines
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <Description color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="PDF Format Only" 
                secondary="Upload clinical protocol documents in PDF format"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Info color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="File Size Limit" 
                secondary="Maximum file size is 50MB for optimal processing"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Text-Based PDFs" 
                secondary="Ensure your PDF contains searchable text (not scanned images)"
              />
            </ListItem>
          </List>
        </Paper>
      </Box>
    </Box>
  );
};

export default DocumentUpload;