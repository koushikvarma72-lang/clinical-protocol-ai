# DocumentAnalysis.js - Line-by-Line Explanation

**File Purpose**: React component that extracts key sections from clinical protocols using AI, allows users to review and approve sections, and generates executive summaries.

**Complexity Level**: ⭐⭐ Intermediate (280 lines)

---

## Import Statements (Lines 1-25)

```javascript
import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Paper, Grid, Card, ... } from '@mui/material';
import { AutoAwesome, Visibility, CheckCircle, Cancel, ... } from '@mui/icons-material';
import { extractKeySections, submitReview, submitFeedback } from '../services/api';
```
- Imports React hooks for state and side effects
- Imports Material-UI components for UI layout
- Imports icons for visual elements
- Imports API functions for backend communication

---

## Component Definition (Lines 27-29)

```javascript
const DocumentAnalysis = ({ 
  documentReady, 
  onSectionsExtracted, 
  extractedSections, 
  onSummaryGenerated 
}) => {
```
- Receives props:
  - `documentReady`: boolean indicating if document is loaded
  - `onSectionsExtracted`: callback when sections are extracted
  - `extractedSections`: previously extracted sections
  - `onSummaryGenerated`: callback when summary is generated

---

## State Management (Lines 30-40)

```javascript
const [loading, setLoading] = useState(false);
```
- Tracks if AI is currently extracting sections

```javascript
const [sections, setSections] = useState(extractedSections || []);
```
- Stores extracted sections from the document
- Initializes with previously extracted sections if available

```javascript
const [error, setError] = useState(null);
```
- Stores error messages if extraction fails

```javascript
const [selectedSection, setSelectedSection] = useState(null);
const [dialogOpen, setDialogOpen] = useState(false);
```
- Manages section detail dialog state

```javascript
const [generating, setGenerating] = useState(false);
```
- Tracks if summary is being generated

```javascript
const [analysisComplete, setAnalysisComplete] = useState(false);
```
- Indicates if analysis has been run

```javascript
const [userSession] = useState(() => `analysis_${Date.now()}_${Math.random()...}`);
```
- Creates unique session ID for tracking

---

## Effect Hook (Lines 42-48)

```javascript
useEffect(() => {
  if (extractedSections && extractedSections.length > 0) {
    setSections(extractedSections);
    setAnalysisComplete(true);
  }
}, [extractedSections]);
```
- Syncs component state with prop changes
- Updates sections when new ones are passed in
- Marks analysis as complete if sections exist

---

## Extract Sections Function (Lines 50-75)

```javascript
const handleExtractSections = async () => {
  if (!documentReady) {
    setError('Please upload a document first');
    return;
  }

  console.log('🚀 Starting document analysis...');
  setLoading(true);
  setError(null);
  
  try {
    console.log('📡 Calling extractKeySections API...');
    const response = await extractKeySections();
    console.log('📊 API Response:', response);
    
    if (response.error) {
      console.error('❌ API returned error:', response.error);
      setError(response.error);
    } else {
      const sectionsData = response.sections || [];
      console.log('✅ Extracted sections:', sectionsData.length);
      setSections(sectionsData);
      onSectionsExtracted(sectionsData);
      setAnalysisComplete(true);
    }
  } catch (err) {
    console.error('❌ Extract sections failed:', err);
    setError('Failed to extract sections: ' + err.message);
  } finally {
    setLoading(false);
  }
};
```
- Validates document is loaded
- Calls backend API to extract key sections
- Handles success and error cases
- Logs detailed debug information
- Updates parent component via callback

**Real-World Analogy**: Like using a highlighter to mark important sections in a document - AI identifies key parts automatically.

---

## Approval Change Function (Lines 77-110)

```javascript
const handleApprovalChange = async (index, approved) => {
  const updatedSections = sections.map((section, i) => 
    i === index ? { ...section, approved } : section
  );
  setSections(updatedSections);
  onSectionsExtracted(updatedSections);
  
  // Record feedback for approval/rejection
  const section = sections[index];
  try {
    await submitFeedback({
      message_id: `approval_${section.title}_${Date.now()}`,
      question: `Section approval: ${section.title}`,
      answer: section.content,
      reaction_type: approved ? 'approve_section' : 'reject_section',
      user_session: userSession,
      sources: section.sources || [],
      evidence_count: section.evidence_count || 0,
      confidence_score: section.confidence || 0.0,
      additional_data: {
        section_title: section.title,
        section_index: index,
        approved: approved
      }
    });
  } catch (error) {
    console.error('Failed to record approval feedback:', error);
  }
};
```
- Updates section approval status
- Records user feedback about approval
- Silently fails if feedback submission fails
- Notifies parent component of changes

---

## View Section Function (Lines 112-140)

```javascript
const handleViewSection = async (section) => {
  setSelectedSection(section);
  setDialogOpen(true);
  
  // Record feedback for section viewing
  try {
    await submitFeedback({
      message_id: `section_${section.title}_${Date.now()}`,
      question: `View section: ${section.title}`,
      answer: section.content,
      reaction_type: 'view_section',
      user_session: userSession,
      sources: section.sources || [],
      evidence_count: section.evidence_count || 0,
      confidence_score: section.confidence || 0.0,
      additional_data: {
        section_title: section.title,
        section_description: section.description
      }
    });
  } catch (error) {
    console.error('Failed to record section view feedback:', error);
  }
};
```
- Opens dialog showing full section details
- Records that user viewed the section
- Tracks which sections users are interested in

---

## Generate Summary Function (Lines 142-165)

```javascript
const handleGenerateSummary = async () => {
  const approvedSections = sections.filter(section => section.approved);
  
  if (approvedSections.length === 0) {
    setError('Please approve at least one section to generate a summary');
    return;
  }

  setGenerating(true);
  setError(null);
  
  try {
    const response = await submitReview(sections);
    
    if (response.error) {
      setError(response.error);
    } else {
      onSummaryGenerated(response.final_summary);
      // Show success message or redirect to summary tab
    }
  } catch (err) {
    setError('Failed to generate summary: ' + err.message);
  } finally {
    setGenerating(false);
  }
};
```
- Validates at least one section is approved
- Calls backend to generate summary
- Notifies parent component of generated summary
- Handles errors gracefully

---

## Get Confidence Color Function (Lines 167-173)

```javascript
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.6) return 'warning';
  return 'error';
};
```
- Returns color based on confidence score
- Green (success) for high confidence (80%+)
- Yellow (warning) for medium confidence (60-80%)
- Red (error) for low confidence (<60%)

---

## Main JSX Return (Lines 175+)

### Header Section (Lines 177-210)
```javascript
<Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider', flexShrink: 0 }}>
  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <Box>
      <Typography variant="h5" gutterBottom>
        Document Analysis
      </Typography>
      <Typography variant="body2" color="text.secondary">
        AI-powered extraction and analysis of key protocol sections
      </Typography>
    </Box>
    
    <Box sx={{ display: 'flex', gap: 1 }}>
      {analysisComplete && (
        <Tooltip title="Re-analyze document">
          <IconButton onClick={handleExtractSections} disabled={loading}>
            <Refresh />
          </IconButton>
        </Tooltip>
      )}
      
      {!analysisComplete && (
        <Button
          variant="contained"
          startIcon={<AutoAwesome />}
          onClick={handleExtractSections}
          disabled={!documentReady || loading}
        >
          {loading ? 'Analyzing...' : 'Start Analysis'}
        </Button>
      )}
    </Box>
  </Box>

  {!documentReady && (
    <Alert severity="warning" sx={{ mt: 2 }}>
      No document loaded. Upload a protocol document to start analysis.
    </Alert>
  )}

  {error && (
    <Alert severity="error" sx={{ mt: 2 }}>
      {error}
    </Alert>
  )}
</Box>
```
- Shows page title and description
- Displays "Start Analysis" button or "Re-analyze" button
- Shows warnings if no document loaded
- Displays error messages

### Loading State (Lines 212-230)
```javascript
{loading && (
  <Box sx={{ 
    flex: 1, 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center',
    p: 3 
  }}>
    <Paper sx={{ p: 4, textAlign: 'center', maxWidth: 500 }}>
      <AutoAwesome sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
      <Typography variant="h6" gutterBottom>
        Analyzing Protocol Document
      </Typography>
      <LinearProgress sx={{ mt: 2, mb: 2 }} />
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        AI is extracting key sections like objectives, criteria, endpoints, and safety measures...
      </Typography>
      <Typography variant="caption" color="text.secondary">
        This may take 1-2 minutes depending on document complexity
      </Typography>
    </Paper>
  </Box>
)}
```
- Shows loading spinner and message
- Explains what AI is doing
- Sets expectations for processing time

### Analysis Results (Lines 232-350)
```javascript
{analysisComplete && sections.length > 0 && (
  <Box sx={{ flex: 1, p: 3, minHeight: 0 }}>
    {/* Summary Stats */}
    <Paper sx={{ p: 3, mb: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={4}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary.main" fontWeight="bold">
              {totalSections}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Sections Extracted
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="success.main" fontWeight="bold">
              {approvedCount}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Approved Sections
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="info.main" fontWeight="bold">
              {Math.round((sections.reduce((sum, s) => sum + s.confidence, 0) / sections.length) * 100)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg. Confidence
            </Typography>
          </Box>
        </Grid>
      </Grid>
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Review and approve sections to generate executive summary
        </Typography>
        <Button
          variant="contained"
          startIcon={generating ? <CircularProgress size={16} /> : <Analytics />}
          onClick={handleGenerateSummary}
          disabled={approvedCount === 0 || generating}
        >
          {generating ? 'Generating...' : `Generate Summary (${approvedCount})`}
        </Button>
      </Box>
    </Paper>

    {/* Extracted Sections */}
    <Grid container spacing={2}>
      {sections.map((section, index) => (
        <Grid item xs={12} md={6} key={index}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Typography variant="h6" component="h3" gutterBottom>
                  {section.title}
                </Typography>
                <Chip
                  label={`${Math.round(section.confidence * 100)}%`}
                  color={getConfidenceColor(section.confidence)}
                  size="small"
                />
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {section.description}
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 2 }}>
                {section.content.length > 200 
                  ? `${section.content.substring(0, 200)}...` 
                  : section.content
                }
              </Typography>
              
              {section.sources && section.sources.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Sources:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {section.sources.slice(0, 3).map((source, idx) => (
                      <Chip key={idx} label={source} size="small" variant="outlined" />
                    ))}
                    {section.sources.length > 3 && (
                      <Chip label={`+${section.sources.length - 3} more`} size="small" variant="outlined" />
                    )}
                  </Box>
                </Box>
              )}
            </CardContent>
            
            <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
              <Button
                size="small"
                startIcon={<Visibility />}
                onClick={() => handleViewSection(section)}
              >
                View Full
              </Button>
              
              <FormControlLabel
                control={
                  <Checkbox
                    checked={section.approved || false}
                    onChange={(e) => handleApprovalChange(index, e.target.checked)}
                    icon={<Cancel />}
                    checkedIcon={<CheckCircle />}
                    color="success"
                  />
                }
                label={section.approved ? 'Approved' : 'Approve'}
              />
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
)}
```
- Shows statistics (total sections, approved count, average confidence)
- Displays each extracted section in a card
- Shows section title, description, preview, and sources
- Confidence score with color coding
- "View Full" button to see complete section
- Checkbox to approve/reject section
- "Generate Summary" button (enabled only if sections approved)

### Section Detail Dialog (Lines 352-390)
```javascript
<Dialog 
  open={dialogOpen} 
  onClose={() => setDialogOpen(false)}
  maxWidth="md"
  fullWidth
>
  <DialogTitle>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      {selectedSection?.title}
      <Chip
        label={`${Math.round((selectedSection?.confidence || 0) * 100)}% confidence`}
        color={getConfidenceColor(selectedSection?.confidence || 0)}
        size="small"
      />
    </Box>
  </DialogTitle>
  <DialogContent>
    <Typography variant="body2" color="text.secondary" gutterBottom>
      {selectedSection?.description}
    </Typography>
    <Divider sx={{ my: 2 }} />
    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
      {selectedSection?.content}
    </Typography>
    
    {selectedSection?.sources && selectedSection.sources.length > 0 && (
      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Sources:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {selectedSection.sources.map((source, index) => (
            <Chip key={index} label={source} variant="outlined" />
          ))}
        </Box>
      </Box>
    )}
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setDialogOpen(false)}>
      Close
    </Button>
  </DialogActions>
</Dialog>
```
- Modal dialog showing full section details
- Displays complete section content
- Shows all sources
- Displays confidence score

---

## Analysis Workflow

```
1. User clicks "Start Analysis"
   ↓
2. Component calls extractKeySections API
   ↓
3. Show loading spinner
   ↓
4. Backend extracts key sections (objectives, criteria, etc.)
   ↓
5. Display extracted sections in cards
   ↓
6. User reviews and approves sections
   ↓
7. User clicks "Generate Summary"
   ↓
8. Backend generates executive summary
   ↓
9. Summary displayed in ProtocolSummary tab
```

---

## Key Features

| Feature | Purpose |
|---------|---------|
| **Auto-extraction** | AI identifies key sections automatically |
| **Confidence scoring** | Shows how confident AI is about each section |
| **Section preview** | Shows first 200 characters of each section |
| **Full view dialog** | Allows viewing complete section content |
| **Approval workflow** | Users can approve/reject sections |
| **Source tracking** | Shows where information came from |
| **Summary generation** | Creates executive summary from approved sections |
| **Feedback recording** | Tracks user interactions for improvement |

---

## Real-World Use Cases

1. **Quick review**: User sees extracted sections and approves relevant ones
2. **Verification**: User checks if AI extracted correct information
3. **Customization**: User rejects irrelevant sections before summary
4. **Learning**: User sees what AI considers important
5. **Documentation**: User generates summary for stakeholders

---

## Error Handling

- **No document**: Shows error if user tries to analyze without uploading
- **API errors**: Displays error message and allows retry
- **No sections**: Shows message if extraction finds nothing
- **Feedback errors**: Silently fails without interrupting workflow

---

## Performance Considerations

1. **Lazy rendering**: Only renders visible sections
2. **Memoization**: Prevents unnecessary re-renders
3. **Async operations**: Non-blocking analysis
4. **Pagination**: Could be added for many sections

---

## Related Files

- `api.js` - Backend API communication
- `App.js` - Main application component
- `ProtocolSummary.js` - Displays generated summary
- `ChatInterface.js` - Chat component
