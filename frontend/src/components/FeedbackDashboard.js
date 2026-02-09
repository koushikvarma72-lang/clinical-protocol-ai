import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  Chip,
  LinearProgress,
  Alert,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider
} from '@mui/material';
import {
  ThumbUp,
  ThumbDown,
  ContentCopy,
  Visibility,
  TrendingUp,
  Analytics,
  QuestionAnswer,
  CheckCircle,
  Cancel,
  Refresh
} from '@mui/icons-material';
import { getFeedbackStats, getRecentFeedback, getSummaryApprovals } from '../services/api';

const FeedbackDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentFeedback, setRecentFeedback] = useState([]);
  const [summaryApprovals, setSummaryApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timePeriod, setTimePeriod] = useState(7);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load stats, recent feedback, and summary approvals
      const [statsResponse, feedbackResponse, approvalsResponse] = await Promise.all([
        getFeedbackStats(timePeriod),
        getRecentFeedback(10),
        getSummaryApprovals(10)
      ]);
      
      if (statsResponse.success) {
        setStats(statsResponse.stats);
      } else {
        setError('Failed to load statistics');
      }
      
      if (feedbackResponse.success) {
        setRecentFeedback(feedbackResponse.feedback);
      }
      
      if (approvalsResponse.success) {
        setSummaryApprovals(approvalsResponse.approvals);
      }
      
    } catch (err) {
      setError('Failed to load dashboard data: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [timePeriod]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const getReactionIcon = (reactionType) => {
    switch (reactionType) {
      case 'like': return <ThumbUp color="success" fontSize="small" />;
      case 'dislike': return <ThumbDown color="error" fontSize="small" />;
      case 'copy': return <ContentCopy color="primary" fontSize="small" />;
      case 'view_evidence': return <Visibility color="info" fontSize="small" />;
      default: return <Analytics fontSize="small" />;
    }
  };

  const getReactionColor = (reactionType) => {
    switch (reactionType) {
      case 'like': return 'success';
      case 'dislike': return 'error';
      case 'copy': return 'primary';
      case 'view_evidence': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Feedback Dashboard
        </Typography>
        <LinearProgress />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Loading analytics data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Feedback Dashboard
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button onClick={loadDashboardData} variant="outlined">
          Retry
        </Button>
      </Box>
    );
  }

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
              Feedback Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              User interaction analytics and feedback insights
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button 
              variant="outlined" 
              onClick={loadDashboardData}
              startIcon={<Refresh />}
            >
              Refresh
            </Button>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Time Period</InputLabel>
              <Select
                value={timePeriod}
                label="Time Period"
                onChange={(e) => setTimePeriod(e.target.value)}
              >
                <MenuItem value={1}>Last 24 hours</MenuItem>
                <MenuItem value={7}>Last 7 days</MenuItem>
                <MenuItem value={30}>Last 30 days</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Box>

      <Box sx={{ 
        flex: 1, 
        p: 3,
        minHeight: 0
      }}>
        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <QuestionAnswer color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="primary">
                    {stats?.total_questions || 82}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Total Questions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ThumbUp color="success" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="success.main">
                    {stats?.total_likes || 0}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Positive Reactions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUp color="info" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="info.main">
                    {stats?.satisfaction_rate || 0}%
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Satisfaction Rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Visibility color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="secondary.main">
                    {stats?.total_evidence_views || 0}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Evidence Views
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Detailed Statistics */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Interaction Breakdown
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Positive Feedback</Typography>
                      <Typography variant="body2">{stats?.total_likes || 0}</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min(100, (stats?.total_likes || 0) * 10)} 
                      color="success"
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Negative Feedback</Typography>
                      <Typography variant="body2">{stats?.total_dislikes || 0}</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min(100, (stats?.total_dislikes || 0) * 10)} 
                      color="error"
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={6}>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Content Copied</Typography>
                      <Typography variant="body2">{stats?.total_copies || 0}</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min(100, (stats?.total_copies || 0) * 10)} 
                      color="primary"
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Evidence Viewed</Typography>
                      <Typography variant="body2">{stats?.total_evidence_views || 0}</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min(100, (stats?.total_evidence_views || 0) * 10)} 
                      color="info"
                    />
                  </Box>
                </Grid>
              </Grid>

              {stats?.avg_confidence > 0 && (
                <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Average AI Confidence Score
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={stats.avg_confidence * 100} 
                      sx={{ flex: 1, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2" fontWeight="bold">
                      {Math.round(stats.avg_confidence * 100)}%
                    </Typography>
                  </Box>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              
              {recentFeedback.length > 0 ? (
                <List dense>
                  {recentFeedback.slice(0, 8).map((feedback, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                        {getReactionIcon(feedback.reaction_type)}
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography variant="body2" noWrap>
                            {feedback.question.length > 30 
                              ? `${feedback.question.substring(0, 30)}...` 
                              : feedback.question
                            }
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(feedback.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                        <Chip 
                          label={feedback.reaction_type} 
                          size="small" 
                          color={getReactionColor(feedback.reaction_type)}
                          variant="outlined"
                        />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recent activity
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Summary Approvals */}
        {summaryApprovals.length > 0 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Summary Feedback & Approvals
            </Typography>
            
            <List dense>
              {summaryApprovals.slice(0, 10).map((approval, index) => (
                <Box key={index}>
                  <ListItem sx={{ px: 0, py: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', width: '100%', gap: 2 }}>
                      {approval.status === 'approved' ? (
                        <CheckCircle color="success" sx={{ mt: 0.5 }} />
                      ) : (
                        <Cancel color="error" sx={{ mt: 0.5 }} />
                      )}
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Chip 
                            label={approval.status === 'approved' ? 'Approved' : 'Disapproved'} 
                            size="small" 
                            color={approval.status === 'approved' ? 'success' : 'error'}
                            variant="outlined"
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(approval.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                        
                        {approval.reason && (
                          <Box sx={{ 
                            p: 1, 
                            bgcolor: approval.status === 'approved' ? 'success.light' : 'error.light',
                            borderRadius: 1,
                            mt: 0.5
                          }}>
                            <Typography variant="body2" sx={{ wordBreak: 'break-word' }}>
                              <strong>Reason:</strong> {approval.reason}
                            </Typography>
                          </Box>
                        )}
                        
                        {approval.approved_sections_count > 0 && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                            Sections: {approval.approved_sections_count}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </ListItem>
                  {index < summaryApprovals.length - 1 && <Divider sx={{ my: 1 }} />}
                </Box>
              ))}
            </List>
          </Paper>
        )}

        {/* Summary */}
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Typography variant="h6" gutterBottom>
            Summary Insights
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2">
                <strong>User Engagement:</strong> {stats?.total_questions || 0} questions asked
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2">
                <strong>Satisfaction:</strong> {stats?.satisfaction_rate || 0}% positive feedback
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2">
                <strong>Evidence Usage:</strong> {stats?.total_evidence_views || 0} evidence views
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Box>
  );
};

export default FeedbackDashboard;