import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel,
  Divider,
  IconButton,
  Tooltip,
  TextField
} from '@mui/material';
import {
  AutoAwesome,
  Visibility,
  CheckCircle,
  Cancel,
  Refresh,
  Analytics,
  ThumbUp,
  ThumbDown
} from '@mui/icons-material';
import { extractKeySections, submitReview, submitFeedback } from '../services/api';

const DocumentAnalysis = ({ documentReady, onSectionsExtracted, extractedSections, onSummaryGenerated }) => {
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState(extractedSections || []);
  const [error, setError] = useState(null);
  const [selectedSection, setSelectedSection] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [userSession] = useState(() => `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [disapprovalDialogOpen, setDisapprovalDialogOpen] = useState(false);
  const [disapprovalReason, setDisapprovalReason] = useState('');
  const [selectedSectionIndex, setSelectedSectionIndex] = useState(null);

  useEffect(() => {
    if (extractedSections && extractedSections.length > 0) {
      setSections(extractedSections);
      setAnalysisComplete(true);
    }
  }, [extractedSections]);

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

  const handleApprovalChange = async (index, approved) => {
    const updatedSections = sections.map((section, i) => 
      i === index ? { ...section, approved, disapprovalReason: null } : section
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

  const handleDisapproveClick = (index) => {
    setSelectedSectionIndex(index);
    setDisapprovalReason('');
    setDisapprovalDialogOpen(true);
  };

  const handleSubmitDisapproval = async () => {
    if (!disapprovalReason.trim()) {
      alert('Please provide a reason for disapproval');
      return;
    }

    const index = selectedSectionIndex;
    const updatedSections = sections.map((section, i) => 
      i === index ? { ...section, approved: false, disapprovalReason } : section
    );
    setSections(updatedSections);
    onSectionsExtracted(updatedSections);

    // Record feedback for disapproval with reason
    const section = sections[index];
    try {
      await submitFeedback({
        message_id: `disapproval_${section.title}_${Date.now()}`,
        question: `Section disapproval: ${section.title}`,
        answer: section.content,
        reaction_type: 'disapprove_section',
        user_session: userSession,
        sources: section.sources || [],
        evidence_count: section.evidence_count || 0,
        confidence_score: section.confidence || 0.0,
        additional_data: {
          section_title: section.title,
          section_index: index,
          disapproval_reason: disapprovalReason,
          approved: false
        }
      });
      
    } catch (error) {
      console.error('Failed to record disapproval feedback:', error);
    }

    setDisapprovalDialogOpen(false);
    setDisapprovalReason('');
    setSelectedSectionIndex(null);
  };

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

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const approvedCount = sections.filter(section => section.approved).length;
  const totalSections = sections.length;

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh'
    }}>
      {/* Header */}
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

      {/* Loading State */}
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

      {/* Analysis Results */}
      {analysisComplete && sections.length > 0 && (
        <Box sx={{ 
          flex: 1, 
          p: 3,
          minHeight: 0
        }}>
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
                  
                  <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2, flexWrap: 'wrap', gap: 1 }}>
                    <Button
                      size="small"
                      startIcon={<Visibility />}
                      onClick={() => handleViewSection(section)}
                    >
                      View Full
                    </Button>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant={section.approved ? 'contained' : 'outlined'}
                        color="success"
                        startIcon={<ThumbUp />}
                        onClick={() => handleApprovalChange(index, true)}
                        disabled={section.approved}
                      >
                        Approve
                      </Button>
                      <Button
                        size="small"
                        variant={section.approved === false && section.disapprovalReason ? 'contained' : 'outlined'}
                        color="error"
                        startIcon={<ThumbDown />}
                        onClick={() => handleDisapproveClick(index)}
                        disabled={section.approved === false && section.disapprovalReason}
                      >
                        Disapprove
                      </Button>
                    </Box>
                  </CardActions>
                  
                  {section.disapprovalReason && (
                    <Box sx={{ px: 2, pb: 2, backgroundColor: '#ffebee', borderRadius: 1 }}>
                      <Typography variant="caption" color="error" fontWeight="bold">
                        Disapproval Reason:
                      </Typography>
                      <Typography variant="body2" color="error" sx={{ mt: 0.5 }}>
                        {section.disapprovalReason}
                      </Typography>
                    </Box>
                  )}
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* No Results */}
      {analysisComplete && sections.length === 0 && (
        <Box sx={{ p: 3 }}>
          <Alert severity="warning">
            No key sections could be extracted from the document. 
            This might indicate an issue with the document format or content.
          </Alert>
        </Box>
      )}

      {/* Section Detail Dialog */}
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

      {/* Disapproval Reason Dialog */}
      <Dialog 
        open={disapprovalDialogOpen} 
        onClose={() => setDisapprovalDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Why are you disapproving this section?
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Please provide a reason for disapproving this section (e.g., inaccurate information, missing details, unclear content, etc.)"
            value={disapprovalReason}
            onChange={(e) => setDisapprovalReason(e.target.value)}
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDisapprovalDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitDisapproval}
            variant="contained"
            color="error"
            disabled={!disapprovalReason.trim()}
          >
            Submit Disapproval
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentAnalysis;