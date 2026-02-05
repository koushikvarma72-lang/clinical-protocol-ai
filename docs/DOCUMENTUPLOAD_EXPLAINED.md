# DocumentUpload.js - Line-by-Line Explanation

**File Purpose**: React component that handles PDF file uploads with drag-and-drop support, progress tracking, and success/error feedback. Allows users to upload clinical protocol documents for analysis.

**Complexity Level**: ⭐⭐ Intermediate (180 lines)

---

## Import Statements (Lines 1-20)

```javascript
import React, { useState, useCallback } from 'react';
```
- Imports React and hooks for state management and performance optimization

```javascript
import { Box, Typography, Button, Paper, Alert, LinearProgress, ... } from '@mui/material';
```
- Imports Material-UI components for UI layout and elements

```javascript
import { CloudUpload, Description, CheckCircle, Info, Refresh } from '@mui/icons-material';
```
- Imports icons for visual feedback (cloud upload, file, checkmark, etc.)

```javascript
import { uploadPDFWithProgress, getUploadProgress } from '../services/api';
```
- Imports API functions to upload files and check upload progress

---

## Component Definition (Lines 22-24)

```javascript
const DocumentUpload = ({ onUploadComplete }) => {
```
- Main component that receives `onUploadComplete` callback prop
- Called when file upload finishes successfully

---

## State Management (Lines 25-31)

```javascript
const [dragActive, setDragActive] = useState(false);
```
- Tracks whether user is dragging a file over the upload area
- Used to highlight the drop zone

```javascript
const [uploading, setUploading] = useState(false);
```
- Indicates if an upload is currently in progress
- Shows/hides progress bar

```javascript
const [uploadProgress, setUploadProgress] = useState(null);
```
- Stores upload progress data:
  - `progress`: percentage (0-100)
  - `message`: status message
  - `stage`: current processing stage
  - `details`: pages, chunks, embeddings count

```javascript
const [uploadResult, setUploadResult] = useState(null);
```
- Stores successful upload result:
  - `filename`: uploaded file name
  - `chunks_count`: number of text chunks created
  - `pages_count`: number of pages extracted
  - `status`: 'completed'

```javascript
const [error, setError] = useState(null);
```
- Stores error message if upload fails

---

## Handle File Upload Function (Lines 33-68)

```javascript
const handleFileUpload = async (file) => {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    setError('Please select a PDF file');
    return;
  }
```
- Validates that uploaded file is a PDF
- Shows error if wrong file type

```javascript
  setUploading(true);
  setError(null);
  setUploadResult(null);
  setUploadProgress({ progress: 0, message: 'Starting upload...' });
```
- Resets state and shows initial progress

```javascript
  try {
    const response = await uploadPDFWithProgress(file);
    
    if (response.error) {
      setError(response.error);
      setUploading(false);
      return;
    }

    const taskId = response.task_id;
```
- Calls backend API to start upload
- Gets task ID for polling progress

```javascript
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
```
- Polls backend every 2 seconds to check upload progress
- Updates progress bar and status message
- When complete, shows success result or error
- Calls `onUploadComplete` callback on success

**Real-World Analogy**: Like uploading a file to Google Drive - shows progress bar and waits for completion.

---

## Handle Drag Events (Lines 70-82)

```javascript
const handleDrag = useCallback((e) => {
  e.preventDefault();
  e.stopPropagation();
  if (e.type === "dragenter" || e.type === "dragover") {
    setDragActive(true);
  } else if (e.type === "dragleave") {
    setDragActive(false);
  }
}, []);
```
- Handles drag enter/over/leave events
- Prevents default browser behavior
- Highlights drop zone when file is dragged over it
- Uses `useCallback` for performance

---

## Handle Drop Event (Lines 84-93)

```javascript
const handleDrop = useCallback((e) => {
  e.preventDefault();
  e.stopPropagation();
  setDragActive(false);
  
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    handleFileUpload(e.dataTransfer.files[0]);
  }
}, []);
```
- Handles file drop on the upload area
- Extracts dropped file and calls upload handler
- Prevents default browser file opening behavior

**Real-World Analogy**: Like dragging a file into a folder on your computer.

---

## Handle File Select (Lines 95-99)

```javascript
const handleFileSelect = (e) => {
  if (e.target.files && e.target.files[0]) {
    handleFileUpload(e.target.files[0]);
  }
};
```
- Handles file selection from file picker dialog
- Calls upload handler with selected file

---

## Reset Upload Function (Lines 101-107)

```javascript
const resetUpload = () => {
  setUploading(false);
  setUploadProgress(null);
  setUploadResult(null);
  setError(null);
};
```
- Clears all upload state
- Allows user to upload another file
- Called when "Upload Another Document" button is clicked

---

## Main JSX Return (Lines 109+)

### Header Section (Lines 111-120)
```javascript
<Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider', flexShrink: 0 }}>
  <Typography variant="h5" gutterBottom>
    Document Upload
  </Typography>
  <Typography variant="body2" color="text.secondary">
    Upload your clinical protocol PDF for AI analysis
  </Typography>
</Box>
```
- Displays page title and description
- Fixed height header that doesn't scroll

### Upload Area (Lines 122-160)
```javascript
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
```
- Shows upload area with drag-and-drop support
- Highlights when file is dragged over
- Hidden file input triggered by button click
- Only shows when not uploading and no result yet

**Real-World Analogy**: Like the upload area in Gmail - drag files or click to browse.

### Upload Progress Section (Lines 162-200)
```javascript
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
```
- Shows progress bar with percentage
- Displays current processing stage
- Shows detailed progress (pages, chunks, embeddings)
- Updates in real-time as upload progresses

### Upload Success Section (Lines 202-250)
```javascript
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
```
- Shows success message with checkmark icon
- Displays statistics (pages, chunks, ready status)
- Shows filename and success alert
- Provides button to upload another document

### Error State (Lines 252-259)
```javascript
{error && (
  <Alert severity="error" sx={{ mb: 3 }}>
    {error}
    <Button onClick={resetUpload} sx={{ ml: 2 }}>
      Try Again
    </Button>
  </Alert>
)}
```
- Shows error message if upload fails
- Provides "Try Again" button to reset and retry

### Guidelines Section (Lines 261-285)
```javascript
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
```
- Shows helpful guidelines for users
- Explains file format requirements
- Lists size limits and best practices

---

## Upload Process Flow

```
1. User drags/selects PDF file
   ↓
2. Validate file is PDF
   ↓
3. Call uploadPDFWithProgress API
   ↓
4. Get task ID from response
   ↓
5. Poll getUploadProgress every 2 seconds
   ↓
6. Update progress bar and status
   ↓
7. When complete, show success or error
   ↓
8. Call onUploadComplete callback
```

---

## Key Features

| Feature | Purpose |
|---------|---------|
| **Drag & Drop** | Intuitive file upload |
| **File Validation** | Ensures only PDFs are uploaded |
| **Progress Tracking** | Shows real-time upload progress |
| **Detailed Stats** | Displays pages, chunks, embeddings |
| **Error Handling** | Shows errors and allows retry |
| **Success Feedback** | Confirms successful upload |
| **Guidelines** | Helps users upload correct files |

---

## Real-World Use Cases

1. **First-time upload**: User uploads their first clinical protocol
2. **Multiple documents**: User uploads different protocols for analysis
3. **Large files**: User sees progress for large PDF files
4. **Error recovery**: User retries after failed upload
5. **Verification**: User sees statistics confirming successful processing

---

## Error Handling

- **Wrong file type**: Shows error if not PDF
- **Upload failure**: Displays error message with retry option
- **Progress polling failure**: Shows error and stops polling
- **Network errors**: Handled by API layer

---

## Performance Considerations

1. **Polling interval**: 2 seconds between progress checks (balances responsiveness and server load)
2. **File size limit**: 50MB to prevent memory issues
3. **Async operations**: Non-blocking upload process
4. **useCallback**: Memoizes event handlers for performance

---

## Related Files

- `api.js` - Backend API communication
- `App.js` - Main application component
- `ChatInterface.js` - Chat component that uses uploaded document
- `DocumentAnalysis.js` - Analyzes uploaded document
