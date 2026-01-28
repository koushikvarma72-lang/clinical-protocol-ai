import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  Avatar,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Fade,
  Slide,
  Card,
  CardContent,
  Divider,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  Send,
  Person,
  SmartToy,
  Clear,
  ContentCopy,
  ThumbUp,
  ThumbDown,
  ExpandMore,
  Visibility,
  AutoAwesome,
  MenuBook,
  Science,
  CheckCircle,
  Schedule,
  TrendingUp,
  Psychology
} from '@mui/icons-material';
import { askQuestion, submitFeedback } from '../services/api';

// Memoized components for better performance
const SuggestedQuestionCard = React.memo(({ question, onClick }) => (
  <Card 
    sx={{ 
      cursor: 'pointer',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      border: '1px solid #e2e8f0',
      background: 'linear-gradient(135deg, #ffffff 0%, #fefefe 100%)',
      '&:hover': { 
        transform: 'translateY(-4px) scale(1.02)', 
        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        borderColor: `${question.color}.300`,
        '& .question-icon': {
          transform: 'scale(1.1)',
          boxShadow: `0 8px 16px -4px rgb(37 99 235 / 0.3)`
        }
      },
      '&:active': {
        transform: 'translateY(-2px) scale(1.01)',
      }
    }}
    onClick={() => onClick(question.text)}
  >
    <CardContent sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
        <Box 
          className="question-icon"
          sx={{ 
            width: 44, 
            height: 44,
            borderRadius: 2,
            background: `linear-gradient(135deg, ${question.color}.main 0%, ${question.color}.dark 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: `0 4px 6px -1px rgb(37 99 235 / 0.2)`
          }}
        >
          {React.cloneElement(question.icon, { 
            fontSize: 'medium', 
            sx: { color: 'white' }
          })}
        </Box>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="body1" sx={{ 
            fontWeight: 600, 
            mb: 1.5,
            lineHeight: 1.4,
            color: 'text.primary'
          }}>
            {question.text}
          </Typography>
          <Chip 
            label={question.category} 
            size="small" 
            sx={{
              backgroundColor: `${question.color}.50`,
              color: `${question.color}.700`,
              fontWeight: 600,
              fontSize: '0.75rem',
              height: 24,
              border: `1px solid ${question.color}.200`,
              '& .MuiChip-label': {
                px: 1.5
              }
            }}
          />
        </Box>
      </Box>
    </CardContent>
  </Card>
));

const ChatInterface = ({ documentReady }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: documentReady 
        ? "Hello! I'm your Clinical Protocol AI Assistant. I've analyzed your protocol document and I'm ready to answer questions about it. Try asking me about the study objectives, inclusion criteria, or safety measures."
        : "Hello! I'm your Clinical Protocol AI Assistant. Please upload a protocol document first so I can help you analyze it.",
      timestamp: new Date(),
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [evidenceDialogOpen, setEvidenceDialogOpen] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [userSession] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [feedbackStatus, setFeedbackStatus] = useState({});
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Memoized suggested questions
  const suggestedQuestions = useMemo(() => [
    { 
      text: "What drug is being tested in this study?", 
      icon: <Science />, 
      category: "Drug Information",
      color: "primary"
    },
    { 
      text: "What are the primary endpoints?", 
      icon: <TrendingUp />, 
      category: "Study Design",
      color: "secondary"
    },
    { 
      text: "What are the inclusion criteria?", 
      icon: <CheckCircle />, 
      category: "Eligibility",
      color: "success"
    },
    { 
      text: "What safety measures are in place?", 
      icon: <Psychology />, 
      category: "Safety",
      color: "warning"
    },
    { 
      text: "How long is the study duration?", 
      icon: <Schedule />, 
      category: "Timeline",
      color: "info"
    },
    { 
      text: "What are the exclusion criteria?", 
      icon: <CheckCircle />, 
      category: "Eligibility",
      color: "success"
    },
    { 
      text: "What is the study design?", 
      icon: <MenuBook />, 
      category: "Study Design",
      color: "secondary"
    },
    { 
      text: "What are the secondary endpoints?", 
      icon: <TrendingUp />, 
      category: "Study Design",
      color: "secondary"
    }
  ], []);

  // Optimized feedback recording function
  const recordFeedback = useCallback(async (message, reactionType) => {
    try {
      await submitFeedback({
        message_id: message.id.toString(),
        question: message.question || '',
        answer: message.content || '',
        reaction_type: reactionType,
        user_session: userSession,
        sources: message.sources || [],
        evidence_count: message.evidence?.length || 0,
        confidence_score: message.confidence || 0.0,
        additional_data: {
          timestamp: message.timestamp?.toISOString(),
          message_type: message.type
        }
      });
    } catch (error) {
      console.error('Failed to record feedback:', error);
    }
  }, [userSession]);

  // Optimized scroll function with debouncing
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeoutId);
  }, [messages, scrollToBottom]);

  // Optimized message sending with error handling
  const handleSendMessage = useCallback(async (messageText = currentMessage) => {
    if (!messageText.trim() || isLoading) return;
    
    if (!documentReady) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'assistant',
        content: "Please upload a protocol document first. Go to the 'Upload Document' tab to get started.",
        timestamp: new Date(),
        error: true
      }]);
      return;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await askQuestion(messageText);
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer || 'I apologize, but I couldn\'t find relevant information for your question.',
        timestamp: new Date(),
        sources: response.sources || [],
        evidence: response.evidence || [],
        confidence: response.confidence || 0.5,
        question: messageText
      };

      // Simulate typing delay for better UX
      setTimeout(() => {
        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 500);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'I apologize, but I encountered an error while processing your question. Please try again.',
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
    } finally {
      setIsLoading(false);
    }
  }, [currentMessage, isLoading, documentReady]);

  // Optimized keyboard handling
  const handleKeyPress = useCallback((event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  // Optimized clear function
  const clearChat = useCallback(() => {
    setMessages([{
      id: 1,
      type: 'assistant',
      content: documentReady 
        ? "Chat cleared! How can I help you with the protocol document?"
        : "Chat cleared! Please upload a protocol document to get started.",
      timestamp: new Date(),
    }]);
    setFeedbackStatus({});
  }, [documentReady]);

  // Optimized clipboard function
  const copyToClipboard = useCallback(async (text, message) => {
    try {
      await navigator.clipboard.writeText(text);
      
      await recordFeedback(message, 'copy');
      
      setFeedbackStatus(prev => ({
        ...prev,
        [message.id]: { ...prev[message.id], copied: true }
      }));
      
      setTimeout(() => {
        setFeedbackStatus(prev => ({
          ...prev,
          [message.id]: { ...prev[message.id], copied: false }
        }));
      }, 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  }, [recordFeedback]);

  const showEvidence = useCallback(async (message) => {
    setSelectedEvidence(message);
    setEvidenceDialogOpen(true);
    await recordFeedback(message, 'view_evidence');
  }, [recordFeedback]);

  const handleReaction = useCallback(async (message, reactionType) => {
    await recordFeedback(message, reactionType);
    
    setFeedbackStatus(prev => ({
      ...prev,
      [message.id]: { 
        ...prev[message.id], 
        [reactionType]: true,
        [reactionType === 'like' ? 'dislike' : 'like']: false
      }
    }));
  }, [recordFeedback]);

  // Memoized suggested questions handler
  const handleSuggestedQuestion = useCallback((questionText) => {
    handleSendMessage(questionText);
  }, [handleSendMessage]);

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      bgcolor: 'grey.50',
      minHeight: '100vh'
    }}>
      {/* Professional Header */}
      <Paper elevation={0} sx={{ 
        borderRadius: 0,
        background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          opacity: 0.3
        }
      }}>
        <Box sx={{ p: 3, position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Box sx={{
                width: 56,
                height: 56,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <AutoAwesome sx={{ fontSize: 32, color: '#2563eb' }} />
              </Box>
              <Box>
                <Typography variant="h4" gutterBottom sx={{ 
                  fontWeight: 700, 
                  mb: 0.5,
                  color: 'white',
                  fontSize: { xs: '1.5rem', sm: '2rem' },
                  textShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  AI Chat Assistant
                </Typography>
                <Typography variant="body1" sx={{ 
                  opacity: 0.95,
                  color: 'rgba(255,255,255,0.9)',
                  fontSize: '1rem',
                  fontWeight: 500
                }}>
                  {documentReady 
                    ? "I've analyzed your protocol document and I'm ready to answer your questions"
                    : "Upload a protocol document to start our conversation"
                  }
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1.5 }}>
              <Tooltip title="Clear conversation">
                <IconButton 
                  onClick={clearChat} 
                  sx={{ 
                    color: 'white', 
                    bgcolor: 'rgba(255,255,255,0.15)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    '&:hover': { 
                      bgcolor: 'rgba(255,255,255,0.25)',
                      transform: 'scale(1.05)'
                    }
                  }}
                >
                  <Clear />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {!documentReady && (
            <Alert 
              severity="info" 
              sx={{ 
                mt: 3, 
                bgcolor: 'rgba(255,255,255,0.15)', 
                color: 'white',
                border: '1px solid rgba(255,255,255,0.2)',
                backdropFilter: 'blur(10px)',
                '& .MuiAlert-icon': { color: 'white' },
                '& .MuiAlert-message': { fontWeight: 500 }
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                📄 No document loaded. Upload a clinical protocol to unlock the full power of AI analysis.
              </Typography>
            </Alert>
          )}
        </Box>
      </Paper>

      {/* Professional Suggested Questions */}
      {documentReady && messages.length <= 1 && (
        <Slide direction="down" in={true} mountOnEnter unmountOnExit>
          <Paper elevation={0} sx={{ 
            m: 3, 
            p: 3, 
            borderRadius: 4,
            flexShrink: 0,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '1px solid #e2e8f0',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.02) 0%, rgba(124, 58, 237, 0.02) 100%)',
            }
          }}>
            <Box sx={{ position: 'relative', zIndex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Box sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 6px -1px rgb(37 99 235 / 0.3)'
                }}>
                  <AutoAwesome sx={{ color: 'white', fontSize: 24 }} />
                </Box>
                <Box>
                  <Typography variant="h5" sx={{ 
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    mb: 0.5
                  }}>
                    Quick Start Questions
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    Get started with these common clinical protocol questions
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', 
                gap: 2.5,
                pr: 1
              }}>
                {suggestedQuestions.slice(0, 6).map((question, index) => (
                  <SuggestedQuestionCard
                    key={index}
                    question={question}
                    onClick={handleSuggestedQuestion}
                  />
                ))}
              </Box>
            </Box>
          </Paper>
        </Slide>
      )}

      {/* Enhanced Messages */}
      <Box sx={{ 
        flex: 1, 
        p: 1,
        minHeight: 0 // Important for flex child with overflow
      }}>
        <List sx={{ py: 0 }}>
          {messages.map((message, index) => (
            <Fade key={message.id} in={true} timeout={500} style={{ transitionDelay: `${index * 100}ms` }}>
              <ListItem sx={{ px: 0, py: 2, alignItems: 'flex-start' }}>
                <Box sx={{ display: 'flex', width: '100%', gap: 2 }}>
                  <Avatar sx={{ 
                    bgcolor: message.type === 'user' 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                      : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    width: 40, 
                    height: 40,
                    boxShadow: 2
                  }}>
                    {message.type === 'user' ? <Person /> : <SmartToy />}
                  </Avatar>
                  
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {message.type === 'user' ? 'You' : 'AI Assistant'}
                      </Typography>
                      <Chip 
                        label={message.timestamp.toLocaleTimeString()} 
                        size="small" 
                        variant="outlined"
                        sx={{ fontSize: '0.7rem', height: 20 }}
                      />
                    </Box>
                    
                    <Paper 
                      elevation={message.type === 'user' ? 2 : 3}
                      sx={{ 
                        p: 2, 
                        background: message.type === 'user' 
                          ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                          : 'white',
                        color: message.type === 'user' ? 'white' : 'text.primary',
                        borderRadius: 3,
                        position: 'relative',
                        '&::before': message.type === 'assistant' ? {
                          content: '""',
                          position: 'absolute',
                          top: -8,
                          left: 20,
                          width: 0,
                          height: 0,
                          borderLeft: '8px solid transparent',
                          borderRight: '8px solid transparent',
                          borderBottom: '8px solid white',
                        } : {}
                      }}
                    >
                      <Typography variant="body1" sx={{ 
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6,
                        '& strong': { fontWeight: 600 }
                      }}>
                        {message.content}
                      </Typography>
                      
                      {/* Enhanced Sources and Evidence Display */}
                      {message.type === 'assistant' && !message.error && (message.sources?.length > 0 || message.evidence?.length > 0) && (
                        <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'grey.200' }}>
                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <Box sx={{ mb: 2 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                <MenuBook color="primary" fontSize="small" />
                                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                                  Sources ({message.sources.length})
                                </Typography>
                              </Box>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {message.sources.map((source, index) => (
                                  <Chip 
                                    key={index} 
                                    label={source} 
                                    size="small" 
                                    color="primary"
                                    variant="filled"
                                    sx={{ 
                                      fontWeight: 500,
                                      '& .MuiChip-label': { px: 1.5 }
                                    }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          )}
                          
                          {/* Evidence Count and View Button */}
                          {message.evidence && message.evidence.length > 0 && (
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Visibility color="info" fontSize="small" />
                                <Typography variant="body2" color="text.secondary">
                                  Based on {message.evidence.length} evidence pieces
                                </Typography>
                              </Box>
                              <Button 
                                size="small" 
                                variant="outlined" 
                                startIcon={<Visibility />}
                                onClick={() => showEvidence(message)}
                                sx={{ borderRadius: 2 }}
                              >
                                View Evidence
                              </Button>
                            </Box>
                          )}
                          
                          {/* Method indicator */}
                          {message.method && (
                            <Box sx={{ mt: 1 }}>
                              <Chip 
                                label={`Method: ${message.method.replace(/_/g, ' ')}`}
                                size="small"
                                color="info"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem', height: 20 }}
                              />
                            </Box>
                          )}
                        </Box>
                      )}
                    </Paper>
                    
                    {/* Enhanced Action Buttons */}
                    {message.type === 'assistant' && !message.error && (
                      <Box sx={{ display: 'flex', gap: 1, mt: 2, justifyContent: 'flex-end' }}>
                        <Tooltip title={feedbackStatus[message.id]?.copied ? "Copied!" : "Copy response"}>
                          <IconButton 
                            size="small" 
                            onClick={() => copyToClipboard(message.content, message)}
                            sx={{
                              bgcolor: feedbackStatus[message.id]?.copied ? 'success.light' : 'grey.100',
                              color: feedbackStatus[message.id]?.copied ? 'success.dark' : 'text.secondary',
                              '&:hover': { bgcolor: feedbackStatus[message.id]?.copied ? 'success.light' : 'grey.200' }
                            }}
                          >
                            <ContentCopy fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Helpful response">
                          <IconButton 
                            size="small"
                            onClick={() => handleReaction(message, 'like')}
                            sx={{
                              bgcolor: feedbackStatus[message.id]?.like ? 'success.light' : 'grey.100',
                              color: feedbackStatus[message.id]?.like ? 'success.dark' : 'text.secondary',
                              '&:hover': { bgcolor: feedbackStatus[message.id]?.like ? 'success.light' : 'grey.200' }
                            }}
                          >
                            <ThumbUp fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Not helpful">
                          <IconButton 
                            size="small"
                            onClick={() => handleReaction(message, 'dislike')}
                            sx={{
                              bgcolor: feedbackStatus[message.id]?.dislike ? 'error.light' : 'grey.100',
                              color: feedbackStatus[message.id]?.dislike ? 'error.dark' : 'text.secondary',
                              '&:hover': { bgcolor: feedbackStatus[message.id]?.dislike ? 'error.light' : 'grey.200' }
                            }}
                          >
                            <ThumbDown fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    )}
                  </Box>
                </Box>
              </ListItem>
            </Fade>
          ))}
          
          {/* Enhanced Loading State with Typing Indicator */}
          {(isLoading || isTyping) && (
            <Fade in={true}>
              <ListItem sx={{ px: 0, py: 2, alignItems: 'flex-start' }}>
                <Box sx={{ display: 'flex', width: '100%', gap: 2 }}>
                  <Avatar sx={{ 
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    width: 40, 
                    height: 40,
                    boxShadow: 2
                  }}>
                    <SmartToy />
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                      AI Assistant
                    </Typography>
                    <Paper elevation={3} sx={{ p: 2, bgcolor: 'white', borderRadius: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <CircularProgress size={20} />
                        <Typography variant="body1" color="text.secondary">
                          {isTyping ? 'Typing response...' : 'Reading through the protocol document...'}
                        </Typography>
                      </Box>
                      {!isTyping && (
                        <>
                          <LinearProgress 
                            sx={{ 
                              borderRadius: 1,
                              '& .MuiLinearProgress-bar': {
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                              }
                            }} 
                          />
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            Analyzing relevant sections and preparing your answer...
                          </Typography>
                        </>
                      )}
                    </Paper>
                  </Box>
                </Box>
              </ListItem>
            </Fade>
          )}
        </List>
        <div ref={messagesEndRef} />
      </Box>

      {/* Professional Input */}
      <Paper elevation={0} sx={{ 
        m: 3, 
        borderRadius: 4, 
        overflow: 'hidden',
        flexShrink: 0,
        background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        border: '1px solid #e2e8f0',
        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
      }}>
        <Box sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
            <TextField
              ref={inputRef}
              fullWidth
              multiline
              maxRows={4}
              placeholder={documentReady ? "Ask me anything about the clinical protocol..." : "Upload a document first to start chatting"}
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!documentReady || isLoading}
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: '#ffffff',
                  fontSize: '1rem',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  border: '2px solid #e2e8f0',
                  '&:hover': { 
                    backgroundColor: '#ffffff',
                    borderColor: '#cbd5e1',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      border: 'none'
                    }
                  },
                  '&.Mui-focused': { 
                    backgroundColor: '#ffffff',
                    borderColor: '#2563eb',
                    boxShadow: '0 0 0 4px rgba(37, 99, 235, 0.1)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      border: 'none'
                    }
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                    border: 'none'
                  }
                },
                '& .MuiInputBase-input': {
                  padding: '16px 20px',
                  '&::placeholder': {
                    color: '#94a3b8',
                    opacity: 1,
                    fontWeight: 500
                  }
                }
              }}
            />
            <Button
              variant="contained"
              onClick={() => handleSendMessage()}
              disabled={!currentMessage.trim() || !documentReady || isLoading}
              sx={{ 
                minWidth: 64,
                height: 64,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                boxShadow: '0 10px 15px -3px rgb(37 99 235 / 0.4)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%)',
                  boxShadow: '0 20px 25px -5px rgb(37 99 235 / 0.4)',
                  transform: 'translateY(-2px) scale(1.05)'
                },
                '&:active': {
                  transform: 'translateY(0) scale(1.02)'
                },
                '&:disabled': {
                  background: '#e2e8f0',
                  color: '#94a3b8',
                  boxShadow: 'none',
                  transform: 'none'
                }
              }}
            >
              <Send sx={{ fontSize: 24 }} />
            </Button>
          </Box>
          {documentReady && (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              mt: 2,
              pt: 2,
              borderTop: '1px solid #e2e8f0'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  backgroundColor: '#10b981',
                  animation: 'pulse 2s infinite'
                }} />
                <Typography variant="caption" sx={{ 
                  color: 'text.secondary',
                  fontWeight: 500,
                  fontSize: '0.8rem'
                }}>
                  💡 Ask specific questions about objectives, criteria, safety measures, or study design
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ 
                color: currentMessage.length > 400 ? 'warning.main' : 'text.secondary',
                fontWeight: 600,
                fontSize: '0.75rem',
                px: 2,
                py: 0.5,
                borderRadius: 2,
                backgroundColor: currentMessage.length > 400 ? 'warning.50' : 'grey.100'
              }}>
                {currentMessage.length}/500
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Enhanced Evidence Dialog */}
      <Dialog 
        open={evidenceDialogOpen} 
        onClose={() => setEvidenceDialogOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, maxHeight: '80vh' }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <Visibility />
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Evidence Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedEvidence?.evidence?.length || 0} pieces of supporting evidence
                </Typography>
              </Box>
            </Box>
            <Badge badgeContent={selectedEvidence?.evidence?.length || 0} color="primary">
              <MenuBook color="action" />
            </Badge>
          </Box>
        </DialogTitle>
        <Divider />
        <DialogContent sx={{ pt: 2 }}>
          {selectedEvidence?.evidence && selectedEvidence.evidence.length > 0 ? (
            <Box>
              {/* Question Context */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.50', borderLeft: 4, borderColor: 'primary.main' }}>
                <Typography variant="subtitle2" color="primary" gutterBottom sx={{ fontWeight: 600 }}>
                  Original Question:
                </Typography>
                <Typography variant="body1">
                  {selectedEvidence.question || 'N/A'}
                </Typography>
              </Paper>
              
              {/* Evidence Items */}
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Supporting Evidence:
              </Typography>
              
              {selectedEvidence.evidence.map((evidence, index) => (
                <Accordion 
                  key={index} 
                  sx={{ 
                    mb: 2, 
                    borderRadius: 2,
                    '&:before': { display: 'none' },
                    boxShadow: 1
                  }}
                >
                  <AccordionSummary 
                    expandIcon={<ExpandMore />}
                    sx={{ 
                      bgcolor: 'grey.50',
                      borderRadius: '8px 8px 0 0',
                      '&.Mui-expanded': { borderRadius: '8px 8px 0 0' }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {index + 1}
                        </Typography>
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          Evidence Piece {index + 1}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                          <Chip 
                            label={evidence.source || `Page ${evidence.page_number}`} 
                            size="small" 
                            color="primary" 
                            variant="filled"
                          />
                          <Chip 
                            label={`${Math.round((evidence.relevance_score || 0) * 100)}% relevant`} 
                            size="small" 
                            color={
                              evidence.relevance_score > 0.7 ? 'success' : 
                              evidence.relevance_score > 0.4 ? 'warning' : 'error'
                            }
                            variant="filled"
                          />
                        </Box>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 2 }}>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="body1" sx={{ 
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6,
                        fontFamily: 'monospace',
                        fontSize: '0.9rem'
                      }}>
                        {evidence.text}
                      </Typography>
                    </Paper>
                    {evidence.distance && (
                      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Similarity Score: {(1 - (evidence.distance / 500)).toFixed(3)}
                        </Typography>
                      </Box>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Avatar sx={{ bgcolor: 'grey.100', width: 64, height: 64, mx: 'auto', mb: 2 }}>
                <MenuBook sx={{ fontSize: 32, color: 'grey.400' }} />
              </Avatar>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Evidence Available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No detailed evidence was found for this response.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button 
            onClick={() => setEvidenceDialogOpen(false)}
            variant="contained"
            sx={{ borderRadius: 2 }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatInterface;