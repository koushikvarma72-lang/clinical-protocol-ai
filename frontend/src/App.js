import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Tabs,
  Tab,
  IconButton,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Switch,
  FormControlLabel,
  FormGroup,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
  Snackbar
} from '@mui/material';
import {
  Chat,
  AutoAwesome,
  Description,
  Upload,
  Settings,
  Help,
  Notifications,
  Menu as MenuIcon,
  Analytics,
  Close,
  Info,
  Api,
  ContactSupport,
  QuestionAnswer,
  CheckCircle,
  Error
} from '@mui/icons-material';
import ChatInterface from './components/ChatInterface';
import DocumentAnalysis from './components/DocumentAnalysis';
import ProtocolSummary from './components/ProtocolSummary';
import DocumentUpload from './components/DocumentUpload';
import FeedbackDashboard from './components/FeedbackDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { getStatus } from './services/api';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2563eb', // Professional blue
      light: '#3b82f6',
      dark: '#1d4ed8',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#7c3aed', // Professional purple
      light: '#8b5cf6',
      dark: '#6d28d9',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f8fafc', // Subtle gray background
      paper: '#ffffff',
    },
    text: {
      primary: '#0f172a', // Rich dark text
      secondary: '#475569', // Medium gray
    },
    success: {
      main: '#059669',
      light: '#10b981',
      dark: '#047857',
    },
    warning: {
      main: '#d97706',
      light: '#f59e0b',
      dark: '#b45309',
    },
    error: {
      main: '#dc2626',
      light: '#ef4444',
      dark: '#b91c1c',
    },
    info: {
      main: '#0284c7',
      light: '#0ea5e9',
      dark: '#0369a1',
    },
    grey: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
    },
  },
  typography: {
    fontFamily: '"Inter", "SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.025em',
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
      letterSpacing: '-0.025em',
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.025em',
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.025em',
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      letterSpacing: '-0.025em',
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      letterSpacing: '-0.025em',
      lineHeight: 1.4,
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 600,
      textTransform: 'none',
      letterSpacing: '0.025em',
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 1.4,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          scrollbarColor: '#cbd5e1 #f1f5f9',
          '&::-webkit-scrollbar': {
            width: 8,
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f5f9',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#cbd5e1',
            borderRadius: 4,
            '&:hover': {
              backgroundColor: '#94a3b8',
            },
          },
        },
        '@keyframes pulse': {
          '0%': {
            opacity: 1,
          },
          '50%': {
            opacity: 0.5,
          },
          '100%': {
            opacity: 1,
          },
        },
        '@keyframes slideInUp': {
          '0%': {
            transform: 'translateY(20px)',
            opacity: 0,
          },
          '100%': {
            transform: 'translateY(0)',
            opacity: 1,
          },
        },
        '@keyframes fadeInScale': {
          '0%': {
            transform: 'scale(0.95)',
            opacity: 0,
          },
          '100%': {
            transform: 'scale(1)',
            opacity: 1,
          },
        },
        '@keyframes shimmer': {
          '0%': {
            backgroundPosition: '-200px 0',
          },
          '100%': {
            backgroundPosition: 'calc(200px + 100%) 0',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid #e2e8f0',
          '&.MuiPaper-elevation1': {
            boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          },
          '&.MuiPaper-elevation2': {
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
          },
          '&.MuiPaper-elevation3': {
            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '0.875rem',
          padding: '12px 24px',
          boxShadow: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
            transition: 'left 0.5s',
          },
          '&:hover': {
            boxShadow: '0 8px 25px -8px rgba(37, 99, 235, 0.3)',
            transform: 'translateY(-2px)',
            '&::before': {
              left: '100%',
            },
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
          color: 'white',
          '&:hover': {
            background: 'linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%)',
            boxShadow: '0 12px 30px -8px rgba(37, 99, 235, 0.4)',
          },
          '&:disabled': {
            background: '#e2e8f0',
            color: '#94a3b8',
          },
        },
        outlined: {
          borderWidth: '2px',
          borderColor: '#e2e8f0',
          color: '#475569',
          '&:hover': {
            borderWidth: '2px',
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.04)',
            color: '#2563eb',
          },
        },
        text: {
          color: '#475569',
          '&:hover': {
            backgroundColor: 'rgba(37, 99, 235, 0.04)',
            color: '#2563eb',
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 0,
            height: 0,
            borderRadius: '50%',
            background: 'rgba(37, 99, 235, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: 'translate(-50%, -50%)',
          },
          '&:hover': {
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            transform: 'scale(1.1)',
            '&::before': {
              width: '100%',
              height: '100%',
            },
          },
          '&:active': {
            transform: 'scale(1.05)',
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '0.875rem',
          minHeight: 48,
          '&.Mui-selected': {
            color: '#2563eb',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
          fontSize: '0.75rem',
          height: 28,
        },
        filled: {
          '&.MuiChip-colorPrimary': {
            backgroundColor: '#dbeafe',
            color: '#1d4ed8',
          },
          '&.MuiChip-colorSecondary': {
            backgroundColor: '#ede9fe',
            color: '#6d28d9',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 16,
            backgroundColor: '#f8fafc',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            border: '2px solid transparent',
            '&:hover': {
              backgroundColor: '#ffffff',
              borderColor: '#cbd5e1',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: 'transparent',
              },
            },
            '&.Mui-focused': {
              backgroundColor: '#ffffff',
              borderColor: '#2563eb',
              boxShadow: '0 0 0 4px rgba(37, 99, 235, 0.1)',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: 'transparent',
              },
            },
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: 'transparent',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#64748b',
            fontWeight: 500,
            '&.Mui-focused': {
              color: '#2563eb',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          border: '1px solid #e2e8f0',
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          background: 'linear-gradient(135deg, #ffffff 0%, #fefefe 100%)',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #2563eb, #7c3aed, #ec4899, #f59e0b)',
            opacity: 0,
            transition: 'opacity 0.3s ease',
          },
          '&:hover': {
            boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
            transform: 'translateY(-8px) scale(1.02)',
            '&::before': {
              opacity: 1,
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #e2e8f0',
          boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 0',
          '&.Mui-selected': {
            backgroundColor: '#dbeafe',
            color: '#1d4ed8',
            '&:hover': {
              backgroundColor: '#bfdbfe',
            },
          },
          '&:hover': {
            backgroundColor: '#f1f5f9',
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: '1px solid',
        },
        standardInfo: {
          backgroundColor: '#eff6ff',
          borderColor: '#bfdbfe',
          color: '#1e40af',
        },
        standardSuccess: {
          backgroundColor: '#f0fdf4',
          borderColor: '#bbf7d0',
          color: '#166534',
        },
        standardWarning: {
          backgroundColor: '#fffbeb',
          borderColor: '#fed7aa',
          color: '#92400e',
        },
        standardError: {
          backgroundColor: '#fef2f2',
          borderColor: '#fecaca',
          color: '#991b1b',
        },
      },
    },
  },
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      style={{
        display: value === index ? 'flex' : 'none',
        flex: 1,
        minHeight: 0
      }}
      {...other}
    >
      <Box sx={{ flex: 1, minHeight: 0, width: '100%' }}>
        {children}
      </Box>
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [documentStatus, setDocumentStatus] = useState({ status: 'no_data', vector_count: 0 });
  const [extractedSections, setExtractedSections] = useState([]);
  const [finalSummary, setFinalSummary] = useState(null);
  const [documentReady, setDocumentReady] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [appSettings, setAppSettings] = useState({
    darkMode: false,
    autoSave: true,
    notifications: true,
    confidenceThreshold: 0.7,
    maxResults: 10,
    language: 'en'
  });
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'info',
      title: 'Welcome to Clinical Protocol AI',
      message: 'Your AI assistant is ready to help analyze clinical protocols.',
      timestamp: new Date(),
      read: false
    }
  ]);

  // Memoized menu items for better performance
  const menuItems = useMemo(() => [
    { text: 'Chat Assistant', icon: <Chat />, tab: 0 },
    { text: 'Document Analysis', icon: <AutoAwesome />, tab: 1 },
    { text: 'Protocol Summary', icon: <Description />, tab: 2 },
    { text: 'Upload Document', icon: <Upload />, tab: 3 },
    { text: 'Analytics Dashboard', icon: <Analytics />, tab: 4 },
  ], []);

  // Optimized status check with error handling
  const checkStatus = useCallback(async () => {
    try {
      const status = await getStatus();
      setDocumentStatus(status);
    } catch (error) {
      console.error('Failed to get status:', error);
      setSnackbar({
        open: true,
        message: 'Failed to check document status',
        severity: 'error'
      });
    }
  }, []);

  useEffect(() => {
    checkStatus();
    
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  // Optimized handlers with useCallback
  const handleTabChange = useCallback((event, newValue) => {
    setCurrentTab(newValue);
  }, []);

  const toggleDrawer = useCallback(() => {
    setDrawerOpen(!drawerOpen);
  }, [drawerOpen]);

  const handleSettingsOpen = useCallback(() => {
    setSettingsOpen(true);
  }, []);

  const handleSettingsClose = useCallback(() => {
    setSettingsOpen(false);
  }, []);

  const handleHelpOpen = useCallback(() => {
    setHelpOpen(true);
  }, []);

  const handleHelpClose = useCallback(() => {
    setHelpOpen(false);
  }, []);

  const handleNotificationsOpen = useCallback(() => {
    setNotificationsOpen(true);
    // Mark notifications as read
    setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
  }, []);

  const handleNotificationsClose = useCallback(() => {
    setNotificationsOpen(false);
  }, []);

  const handleSettingChange = useCallback((setting, value) => {
    setAppSettings(prev => ({
      ...prev,
      [setting]: value
    }));
    
    // Add notification for setting changes
    const newNotification = {
      id: Date.now(),
      type: 'success',
      title: 'Settings Updated',
      message: `${setting.charAt(0).toUpperCase() + setting.slice(1)} has been updated.`,
      timestamp: new Date(),
      read: false
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 9)]); // Keep last 10
    
    // Show snackbar confirmation
    setSnackbar({
      open: true,
      message: 'Settings updated successfully',
      severity: 'success'
    });
  }, []);

  const handleSnackbarClose = useCallback(() => {
    setSnackbar(prev => ({ ...prev, open: false }));
  }, []);

  const isDocumentReady = documentStatus.status === 'ready' && documentStatus.vector_count > 0;

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          minHeight: '100vh',
          '& *': {
            boxSizing: 'border-box' // Ensure proper box sizing
          }
        }}>
        {/* Professional App Bar */}
        <AppBar 
          position="static" 
          elevation={0}
          sx={{ 
            background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <Toolbar sx={{ py: 1.5, minHeight: { xs: 64, sm: 72 } }}>
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={toggleDrawer}
              sx={{ 
                mr: 2, 
                display: { sm: 'none' },
                bgcolor: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                '&:hover': { 
                  bgcolor: 'rgba(255,255,255,0.2)',
                  transform: 'scale(1.05)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexGrow: 1 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 2,
                bgcolor: 'rgba(255,255,255,0.1)',
                px: 3,
                py: 1.5,
                borderRadius: 3,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <Box sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}>
                  <AutoAwesome sx={{ fontSize: 24, color: '#2563eb' }} />
                </Box>
                <Box>
                  <Typography variant="h6" component="div" sx={{ 
                    fontWeight: 700, 
                    lineHeight: 1.2,
                    fontSize: '1.25rem',
                    background: 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}>
                    Clinical Protocol AI
                  </Typography>
                  <Typography variant="caption" sx={{ 
                    opacity: 0.9, 
                    fontSize: '0.75rem',
                    color: 'rgba(255,255,255,0.8)',
                    fontWeight: 500
                  }}>
                    Intelligent Document Assistant
                  </Typography>
                </Box>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              {/* Enhanced Document Status */}
              <Paper 
                sx={{ 
                  px: 3, 
                  py: 1, 
                  bgcolor: isDocumentReady ? 'rgba(5, 150, 105, 0.9)' : 'rgba(217, 119, 6, 0.9)',
                  color: 'white',
                  borderRadius: 3,
                  mr: 1,
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <CheckCircle sx={{ fontSize: 18 }} />
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.8rem', lineHeight: 1 }}>
                      {isDocumentReady ? `${documentStatus.vector_count} chunks` : 'No document'}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: '0.7rem', opacity: 0.9, lineHeight: 1 }}>
                      {isDocumentReady ? 'Ready' : 'Upload needed'}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
              
              {/* Enhanced Header Buttons */}
              <IconButton 
                color="inherit" 
                onClick={handleNotificationsOpen}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  '&:hover': { 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    transform: 'scale(1.05)'
                  }
                }}
              >
                <Badge 
                  badgeContent={notifications.filter(n => !n.read).length} 
                  color="error"
                  sx={{
                    '& .MuiBadge-badge': {
                      backgroundColor: '#ef4444',
                      color: 'white',
                      fontWeight: 600
                    }
                  }}
                >
                  <Notifications />
                </Badge>
              </IconButton>
              
              <IconButton 
                color="inherit" 
                onClick={handleSettingsOpen}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  '&:hover': { 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    transform: 'scale(1.05)'
                  }
                }}
              >
                <Settings />
              </IconButton>
              
              <IconButton 
                color="inherit" 
                onClick={handleHelpOpen}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  '&:hover': { 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    transform: 'scale(1.05)'
                  }
                }}
              >
                <Help />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Mobile Drawer */}
        <Drawer
          anchor="left"
          open={drawerOpen}
          onClose={toggleDrawer}
          sx={{ display: { sm: 'none' } }}
        >
          <Box sx={{ width: 250 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem 
                  button 
                  key={item.text}
                  onClick={() => {
                    setCurrentTab(item.tab);
                    setDrawerOpen(false);
                  }}
                  selected={currentTab === item.tab}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ 
          flex: 1, 
          py: 1, 
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0, // Important for flex child with overflow
          px: { xs: 1, sm: 2 } // Responsive padding
        }}>
          <Grid container spacing={2} sx={{ 
            flex: 1, 
            minHeight: 0, // Important for flex child with overflow
            margin: 0,
            width: '100%'
          }}>
            {/* Sidebar Navigation - Desktop */}
            <Grid item xs={12} sm={3} md={2} sx={{ 
              display: { xs: 'none', sm: 'flex' },
              flexDirection: 'column',
              minHeight: 0,
              paddingLeft: '0 !important' // Remove default grid padding
            }}>
              <Paper sx={{ 
                p: 0, 
                flex: 1,
                minHeight: 0,
                margin: 1,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: '1px solid #e2e8f0'
              }}>
                <Box sx={{ 
                  p: 3, 
                  borderBottom: '1px solid #e2e8f0',
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'
                }}>
                  <Typography variant="h6" sx={{ 
                    fontWeight: 700, 
                    color: 'text.primary',
                    fontSize: '1rem'
                  }}>
                    Navigation
                  </Typography>
                  <Typography variant="caption" sx={{ 
                    color: 'text.secondary',
                    fontSize: '0.75rem'
                  }}>
                    Choose your workspace
                  </Typography>
                </Box>
                <Box sx={{ p: 2 }}>
                  <List dense sx={{ p: 0 }}>
                    {menuItems.map((item) => (
                      <ListItem 
                        button 
                        key={item.text}
                        onClick={() => setCurrentTab(item.tab)}
                        selected={currentTab === item.tab}
                        sx={{ 
                          borderRadius: 2, 
                          mb: 1,
                          px: 2,
                          py: 1.5,
                          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&.Mui-selected': {
                            backgroundColor: '#dbeafe',
                            color: '#1d4ed8',
                            boxShadow: '0 2px 4px -1px rgb(37 99 235 / 0.2)',
                            '& .MuiListItemIcon-root': {
                              color: '#1d4ed8',
                            },
                            '&:hover': {
                              backgroundColor: '#bfdbfe',
                            },
                          },
                          '&:hover': {
                            backgroundColor: '#f1f5f9',
                            transform: 'translateX(4px)',
                          },
                        }}
                      >
                        <ListItemIcon sx={{ 
                          minWidth: 40,
                          '& .MuiSvgIcon-root': {
                            fontSize: 20
                          }
                        }}>
                          {item.icon}
                        </ListItemIcon>
                        <ListItemText 
                          primary={item.text} 
                          primaryTypographyProps={{ 
                            variant: 'body2',
                            fontWeight: currentTab === item.tab ? 600 : 500,
                            fontSize: '0.875rem'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </Paper>
            </Grid>

            {/* Main Content Area */}
            <Grid item xs={12} sm={9} md={10} sx={{ 
              display: 'flex',
              flexDirection: 'column',
              minHeight: 0,
              paddingLeft: { xs: '0 !important', sm: '8px !important' } // Responsive padding
            }}>
              <Paper sx={{ 
                flex: 1,
                borderRadius: 4, 
                display: 'flex', 
                flexDirection: 'column',
                minHeight: 0,
                margin: 1,
                background: 'linear-gradient(135deg, #ffffff 0%, #fefefe 100%)',
                border: '1px solid #e2e8f0',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
              }}>
                {/* Enhanced Tab Headers - Mobile */}
                <Box sx={{ 
                  display: { xs: 'block', sm: 'none' },
                  flexShrink: 0,
                  borderBottom: '1px solid #e2e8f0',
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'
                }}>
                  <Tabs 
                    value={currentTab} 
                    onChange={handleTabChange}
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{
                      '& .MuiTab-root': {
                        minHeight: 56,
                        fontSize: '0.8rem',
                        fontWeight: 600,
                      },
                      '& .MuiTabs-indicator': {
                        backgroundColor: '#2563eb',
                        height: 3,
                        borderRadius: '3px 3px 0 0'
                      }
                    }}
                  >
                    <Tab 
                      icon={<Chat sx={{ fontSize: 20 }} />} 
                      label="Chat" 
                      iconPosition="start"
                      sx={{ gap: 1 }}
                    />
                    <Tab 
                      icon={<AutoAwesome sx={{ fontSize: 20 }} />} 
                      label="Analysis" 
                      iconPosition="start"
                      sx={{ gap: 1 }}
                    />
                    <Tab 
                      icon={<Description sx={{ fontSize: 20 }} />} 
                      label="Summary" 
                      iconPosition="start"
                      sx={{ gap: 1 }}
                    />
                    <Tab 
                      icon={<Upload sx={{ fontSize: 20 }} />} 
                      label="Upload" 
                      iconPosition="start"
                      sx={{ gap: 1 }}
                    />
                    <Tab 
                      icon={<Analytics sx={{ fontSize: 20 }} />} 
                      label="Analytics" 
                      iconPosition="start"
                      sx={{ gap: 1 }}
                    />
                  </Tabs>
                </Box>

                {/* Tab Content */}
                <TabPanel value={currentTab} index={0}>
                  <ChatInterface documentReady={isDocumentReady} />
                </TabPanel>

                <TabPanel value={currentTab} index={1}>
                  <DocumentAnalysis 
                    documentReady={isDocumentReady}
                    onSectionsExtracted={setExtractedSections}
                    extractedSections={extractedSections}
                    onSummaryGenerated={setFinalSummary}
                  />
                </TabPanel>

                <TabPanel value={currentTab} index={2}>
                  <ProtocolSummary 
                    summary={finalSummary}
                    sections={extractedSections}
                  />
                </TabPanel>

                <TabPanel value={currentTab} index={3}>
                  <DocumentUpload 
                    onUploadComplete={() => {
                      // Refresh status after upload
                      setTimeout(async () => {
                        const status = await getStatus();
                        setDocumentStatus(status);
                      }, 2000);
                    }}
                  />
                </TabPanel>
                <TabPanel value={currentTab} index={4}>
                  <FeedbackDashboard />
                </TabPanel>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={handleSettingsClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Settings color="primary" />
              <Typography variant="h6">Application Settings</Typography>
            </Box>
            <IconButton onClick={handleSettingsClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            {/* General Settings */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Settings color="primary" />
                General Settings
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={appSettings.darkMode}
                      onChange={(e) => handleSettingChange('darkMode', e.target.checked)}
                    />
                  }
                  label="Dark Mode (Coming Soon)"
                  disabled
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={appSettings.autoSave}
                      onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                    />
                  }
                  label="Auto-save responses"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={appSettings.notifications}
                      onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                    />
                  }
                  label="Enable notifications"
                />
              </FormGroup>
            </Grid>

            {/* AI Settings */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Api color="secondary" />
                AI Configuration
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  Confidence Threshold: {Math.round(appSettings.confidenceThreshold * 100)}%
                </Typography>
                <Slider
                  value={appSettings.confidenceThreshold}
                  onChange={(e, value) => handleSettingChange('confidenceThreshold', value)}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                  marks={[
                    { value: 0.1, label: '10%' },
                    { value: 0.5, label: '50%' },
                    { value: 1.0, label: '100%' }
                  ]}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Maximum Results</InputLabel>
                  <Select
                    value={appSettings.maxResults}
                    label="Maximum Results"
                    onChange={(e) => handleSettingChange('maxResults', e.target.value)}
                  >
                    <MenuItem value={5}>5 results</MenuItem>
                    <MenuItem value={10}>10 results</MenuItem>
                    <MenuItem value={15}>15 results</MenuItem>
                    <MenuItem value={20}>20 results</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Grid>

            {/* System Info */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Info color="info" />
                System Information
              </Typography>
              <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Document Status:
                    </Typography>
                    <Chip 
                      label={isDocumentReady ? 'Ready' : 'No Document'} 
                      color={isDocumentReady ? 'success' : 'error'}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Vector Count:
                    </Typography>
                    <Typography variant="body2">
                      {documentStatus.vector_count || 0} chunks
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Version:
                    </Typography>
                    <Typography variant="body2">
                      Clinical Protocol AI v1.0
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Backend Status:
                    </Typography>
                    <Chip 
                      label="Connected" 
                      color="success"
                      size="small"
                    />
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSettingsClose}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Help Dialog */}
      <Dialog open={helpOpen} onClose={handleHelpClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Help color="primary" />
              <Typography variant="h6">Help & Support</Typography>
            </Box>
            <IconButton onClick={handleHelpClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            {/* Quick Start */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <QuestionAnswer color="primary" />
                Quick Start Guide
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon><Upload color="primary" /></ListItemIcon>
                  <ListItemText 
                    primary="1. Upload Document" 
                    secondary="Upload your clinical protocol PDF using the Upload Document tab"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Chat color="primary" /></ListItemIcon>
                  <ListItemText 
                    primary="2. Chat with AI" 
                    secondary="Ask questions about your protocol using natural language"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><AutoAwesome color="primary" /></ListItemIcon>
                  <ListItemText 
                    primary="3. Analyze Document" 
                    secondary="Extract key sections automatically and review them"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Description color="primary" /></ListItemIcon>
                  <ListItemText 
                    primary="4. Generate Summary" 
                    secondary="Create executive summaries from approved sections"
                  />
                </ListItem>
              </List>
            </Grid>

            {/* Features */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Info color="secondary" />
                Key Features
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      🤖 AI Chat Assistant
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Ask questions about your protocol and get intelligent responses with source citations.
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      📊 Document Analysis
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Automatically extract key sections like objectives, criteria, and safety measures.
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      📄 Executive Summaries
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Generate professional summaries suitable for stakeholders and regulatory review.
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      📈 Analytics Dashboard
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Track usage statistics, user satisfaction, and system performance.
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Grid>

            {/* Support */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ContactSupport color="info" />
                Support & Troubleshooting
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Common Issues:</strong>
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="• If chat responses are slow, check that Ollama is running" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="• For upload issues, ensure PDF files are text-based (not scanned images)" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="• If sections aren't extracting well, try uploading a different protocol" />
                  </ListItem>
                </List>
              </Alert>
              
              <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Technical Support
                </Typography>
                <Typography variant="body2">
                  For technical issues or questions, please check the system logs or contact your administrator.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleHelpClose}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Notifications Dialog */}
      <Dialog open={notificationsOpen} onClose={handleNotificationsClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Notifications color="primary" />
              <Typography variant="h6">Notifications</Typography>
            </Box>
            <IconButton onClick={handleNotificationsClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {notifications.length > 0 ? (
            <List>
              {notifications.map((notification) => (
                <ListItem key={notification.id} sx={{ mb: 1 }}>
                  <Paper sx={{ width: '100%', p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                      {notification.type === 'info' && <Info color="info" />}
                      {notification.type === 'success' && <CheckCircle color="success" />}
                      {notification.type === 'error' && <Error color="error" />}
                      
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          {notification.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {notification.timestamp.toLocaleString()}
                        </Typography>
                      </Box>
                      
                      {!notification.read && (
                        <Chip label="New" color="primary" size="small" />
                      )}
                    </Box>
                  </Paper>
                </ListItem>
              ))}
            </List>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Notifications sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                No notifications yet
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleNotificationsClose}>Close</Button>
        </DialogActions>
      </Dialog>
      
      {/* Global Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;