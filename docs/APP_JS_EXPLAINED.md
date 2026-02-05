# App.js - Line-by-Line Explanation

**File Purpose**: Main React application component that orchestrates the entire frontend. Manages routing, theme, layout, and global state for the Clinical Protocol AI application.

**Complexity Level**: ⭐⭐⭐ Advanced (1513 lines)

---

## Import Statements (Lines 1-50)

```javascript
import React, { useState, useEffect, useCallback, useMemo } from 'react';
```
- Imports React and essential hooks for state, effects, and optimization

```javascript
import { Box, ThemeProvider, createTheme, CssBaseline, ... } from '@mui/material';
```
- Imports Material-UI components for layout and UI elements

```javascript
import { Chat, AutoAwesome, Description, ... } from '@mui/icons-material';
```
- Imports Material-UI icons for navigation and buttons

```javascript
import ChatInterface from './components/ChatInterface';
import DocumentAnalysis from './components/DocumentAnalysis';
import ProtocolSummary from './components/ProtocolSummary';
import DocumentUpload from './components/DocumentUpload';
import FeedbackDashboard from './components/FeedbackDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { getStatus } from './services/api';
```
- Imports all child components and API functions

---

## Theme Configuration (Lines 52-350)

```javascript
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
    ...
  },
  typography: {
    fontFamily: '"Inter", "SF Pro Display", ...',
    h1: { fontSize: '2.5rem', fontWeight: 700, ... },
    h2: { fontSize: '2rem', fontWeight: 700, ... },
    ...
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: { ... },
    MuiCard: { ... },
    ...
  }
});
```
- Defines Material-UI theme with:
  - Color palette (primary blue, secondary purple)
  - Typography (fonts, sizes, weights)
  - Component overrides (custom button styles, etc.)
  - Shadows and animations

**Real-World Analogy**: Like a design system that defines how all UI elements look and feel.

---

## TabPanel Component (Lines 352-365)

```javascript
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ flex: 1 }}>{children}</Box>}
    </div>
  );
}
```
- Helper component for tab content
- Only renders children when tab is active
- Provides accessibility attributes (role, aria-labelledby)
- Hides inactive tabs with `hidden` attribute

---

## App Component Definition (Lines 367-369)

```javascript
function App() {
```
- Main application component

---

## State Management (Lines 370-410)

```javascript
const [currentTab, setCurrentTab] = useState(0);
```
- Tracks which tab is currently active (0-4)

```javascript
const [drawerOpen, setDrawerOpen] = useState(false);
```
- Tracks if mobile drawer is open

```javascript
const [documentStatus, setDocumentStatus] = useState({ 
  status: 'no_data', 
  vector_count: 0 
});
```
- Stores document status from backend
- `status`: 'no_data', 'processing', or 'ready'
- `vector_count`: Number of document chunks indexed

```javascript
const [extractedSections, setExtractedSections] = useState([]);
const [finalSummary, setFinalSummary] = useState(null);
```
- Stores extracted sections and generated summary
- Passed to child components

```javascript
const [settingsOpen, setSettingsOpen] = useState(false);
const [helpOpen, setHelpOpen] = useState(false);
const [notificationsOpen, setNotificationsOpen] = useState(false);
```
- Tracks which dialogs are open

```javascript
const [snackbar, setSnackbar] = useState({ 
  open: false, 
  message: '', 
  severity: 'info' 
});
```
- Stores snackbar notification state

```javascript
const [appSettings, setAppSettings] = useState({
  darkMode: false,
  autoSave: true,
  notifications: true,
  confidenceThreshold: 0.7,
  maxResults: 10,
  language: 'en'
});
```
- Stores user preferences

```javascript
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
```
- Stores notification history

---

## Memoized Menu Items (Lines 412-420)

```javascript
const menuItems = useMemo(() => [
  { text: 'Chat Assistant', icon: <Chat />, tab: 0 },
  { text: 'Document Analysis', icon: <AutoAwesome />, tab: 1 },
  { text: 'Protocol Summary', icon: <Description />, tab: 2 },
  { text: 'Upload Document', icon: <Upload />, tab: 3 },
  { text: 'Analytics Dashboard', icon: <Analytics />, tab: 4 },
], []);
```
- Defines navigation menu items
- Uses `useMemo` to prevent recreation on every render
- Each item has text, icon, and tab index

---

## Check Status Function (Lines 422-432)

```javascript
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
```
- Fetches document status from backend
- Updates state with status
- Shows error snackbar if fails
- Uses `useCallback` for performance

---

## Status Check Effect (Lines 434-441)

```javascript
useEffect(() => {
  checkStatus();
  
  // Check status every 30 seconds
  const interval = setInterval(checkStatus, 30000);
  return () => clearInterval(interval);
}, [checkStatus]);
```
- Checks status on component mount
- Polls status every 30 seconds
- Cleans up interval on unmount

---

## Event Handlers (Lines 443-500)

```javascript
const handleTabChange = useCallback((event, newValue) => {
  setCurrentTab(newValue);
}, []);
```
- Handles tab switching

```javascript
const toggleDrawer = useCallback(() => {
  setDrawerOpen(!drawerOpen);
}, [drawerOpen]);
```
- Toggles mobile drawer

```javascript
const handleSettingsOpen = useCallback(() => {
  setSettingsOpen(true);
}, []);

const handleSettingsClose = useCallback(() => {
  setSettingsOpen(false);
}, []);
```
- Opens/closes settings dialog

```javascript
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
  
  setNotifications(prev => [newNotification, ...prev.slice(0, 9)]);
  
  // Show snackbar confirmation
  setSnackbar({
    open: true,
    message: 'Settings updated successfully',
    severity: 'success'
  });
}, []);
```
- Updates app settings
- Creates notification
- Shows snackbar confirmation

---

## Computed Values (Lines 502-503)

```javascript
const isDocumentReady = documentStatus.status === 'ready' && documentStatus.vector_count > 0;
```
- Determines if document is ready for analysis
- Used to enable/disable features

---

## Main JSX Return (Lines 505+)

### ErrorBoundary Wrapper (Lines 505-507)
```javascript
<ErrorBoundary>
  <ThemeProvider theme={theme}>
    <CssBaseline />
```
- Wraps entire app with error boundary
- Applies theme to all components
- CssBaseline normalizes browser styles

### Main Container (Lines 508-512)
```javascript
<Box sx={{ 
  display: 'flex', 
  flexDirection: 'column', 
  minHeight: '100vh',
  '& *': {
    boxSizing: 'border-box'
  }
}}>
```
- Main flex container for full-height layout
- Ensures proper box sizing for all elements

### App Bar (Lines 514-600)
```javascript
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
    {/* Menu button for mobile */}
    <IconButton
      edge="start"
      color="inherit"
      aria-label="menu"
      onClick={toggleDrawer}
      sx={{ mr: 2, display: { sm: 'none' } }}
    >
      <MenuIcon />
    </IconButton>
    
    {/* Logo and title */}
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexGrow: 1 }}>
      <Box sx={{ ... }}>
        <Box sx={{ ... }}>
          <AutoAwesome sx={{ fontSize: 24, color: '#2563eb' }} />
        </Box>
        <Box>
          <Typography variant="h6">
            Clinical Protocol AI
          </Typography>
          <Typography variant="caption">
            Intelligent Document Assistant
          </Typography>
        </Box>
      </Box>
    </Box>
    
    {/* Document status badge */}
    <Paper sx={{ ... }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <CheckCircle sx={{ fontSize: 18 }} />
        <Box>
          <Typography variant="body2">
            {isDocumentReady ? `${documentStatus.vector_count} chunks` : 'No document'}
          </Typography>
          <Typography variant="caption">
            {isDocumentReady ? 'Ready' : 'Upload needed'}
          </Typography>
        </Box>
      </Box>
    </Paper>
    
    {/* Header buttons */}
    <IconButton onClick={handleNotificationsOpen}>
      <Badge badgeContent={notifications.filter(n => !n.read).length}>
        <Notifications />
      </Badge>
    </IconButton>
    <IconButton onClick={handleSettingsOpen}>
      <Settings />
    </IconButton>
    <IconButton onClick={handleHelpOpen}>
      <Help />
    </IconButton>
  </Toolbar>
</AppBar>
```
- Professional gradient header
- Shows app title and logo
- Displays document status
- Notification, settings, and help buttons
- Mobile menu button

### Mobile Drawer (Lines 602-620)
```javascript
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
```
- Mobile navigation drawer
- Only shows on small screens
- Closes after selecting tab

### Main Content Area (Lines 622-750)
```javascript
<Container maxWidth="xl" sx={{ 
  flex: 1, 
  py: 1, 
  display: 'flex',
  flexDirection: 'column',
  minHeight: 0,
  px: { xs: 1, sm: 2 }
}}>
  <Grid container spacing={2} sx={{ 
    flex: 1, 
    minHeight: 0,
    margin: 0,
    width: '100%'
  }}>
    {/* Sidebar Navigation - Desktop */}
    <Grid item xs={12} sm={3} md={2}>
      <Paper sx={{ ... }}>
        {/* Navigation menu */}
        <List dense>
          {menuItems.map((item) => (
            <ListItem 
              button 
              key={item.text}
              onClick={() => setCurrentTab(item.tab)}
              selected={currentTab === item.tab}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Grid>

    {/* Main Content Area */}
    <Grid item xs={12} sm={9} md={10}>
      <Paper sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Mobile Tabs */}
        <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab icon={<Chat />} label="Chat" />
            <Tab icon={<AutoAwesome />} label="Analysis" />
            <Tab icon={<Description />} label="Summary" />
            <Tab icon={<Upload />} label="Upload" />
            <Tab icon={<Analytics />} label="Analytics" />
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
```
- Responsive layout with sidebar (desktop) and tabs (mobile)
- Renders active tab content
- Passes state and callbacks to child components

### Settings Dialog (Lines 752-850)
```javascript
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
        <Typography variant="h6">General Settings</Typography>
        <FormGroup>
          <FormControlLabel
            control={<Switch checked={appSettings.autoSave} onChange={...} />}
            label="Auto-save responses"
          />
          <FormControlLabel
            control={<Switch checked={appSettings.notifications} onChange={...} />}
            label="Enable notifications"
          />
        </FormGroup>
      </Grid>

      {/* AI Configuration */}
      <Grid item xs={12}>
        <Typography variant="h6">AI Configuration</Typography>
        <Box sx={{ mb: 3 }}>
          <Typography>
            Confidence Threshold: {Math.round(appSettings.confidenceThreshold * 100)}%
          </Typography>
          <Slider
            value={appSettings.confidenceThreshold}
            onChange={(e, value) => handleSettingChange('confidenceThreshold', value)}
            min={0.1}
            max={1.0}
            step={0.1}
          />
        </Box>
        <FormControl fullWidth>
          <InputLabel>Maximum Results</InputLabel>
          <Select
            value={appSettings.maxResults}
            onChange={(e) => handleSettingChange('maxResults', e.target.value)}
          >
            <MenuItem value={5}>5 results</MenuItem>
            <MenuItem value={10}>10 results</MenuItem>
            <MenuItem value={15}>15 results</MenuItem>
            <MenuItem value={20}>20 results</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      {/* System Info */}
      <Grid item xs={12}>
        <Typography variant="h6">System Information</Typography>
        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Document Status:
              </Typography>
              <Chip 
                label={isDocumentReady ? 'Ready' : 'No Document'} 
                color={isDocumentReady ? 'success' : 'error'}
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
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  </DialogContent>
</Dialog>
```
- Settings dialog with:
  - General settings (auto-save, notifications)
  - AI configuration (confidence threshold, max results)
  - System information display

### Help Dialog (Lines 852-950)
```javascript
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
    {/* Quick Start Guide */}
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6">Quick Start Guide</Typography>
        <List>
          <ListItem>
            <ListItemIcon><Upload color="primary" /></ListItemIcon>
            <ListItemText 
              primary="1. Upload Document" 
              secondary="Upload your clinical protocol PDF"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon><Chat color="primary" /></ListItemIcon>
            <ListItemText 
              primary="2. Chat with AI" 
              secondary="Ask questions about your protocol"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon><AutoAwesome color="primary" /></ListItemIcon>
            <ListItemText 
              primary="3. Analyze Document" 
              secondary="Extract key sections automatically"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon><Description color="primary" /></ListItemIcon>
            <ListItemText 
              primary="4. Generate Summary" 
              secondary="Create executive summaries"
            />
          </ListItem>
        </List>
      </Grid>

      {/* Features */}
      <Grid item xs={12}>
        <Typography variant="h6">Key Features</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">🤖 AI Chat Assistant</Typography>
              <Typography variant="body2" color="text.secondary">
                Ask questions and get intelligent responses with citations.
              </Typography>
            </Paper>
          </Grid>
          {/* More feature cards */}
        </Grid>
      </Grid>

      {/* Support */}
      <Grid item xs={12}>
        <Typography variant="h6">Support & Troubleshooting</Typography>
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Common Issues:</strong>
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText primary="• If chat is slow, check Ollama is running" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• For upload issues, ensure PDF is text-based" />
            </ListItem>
          </List>
        </Alert>
      </Grid>
    </Grid>
  </DialogContent>
</Dialog>
```
- Help dialog with:
  - Quick start guide
  - Feature descriptions
  - Troubleshooting tips

### Notifications Dialog (Lines 952-1000)
```javascript
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
          <ListItem key={notification.id}>
            <Paper sx={{ width: '100%', p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                {notification.type === 'info' && <Info color="info" />}
                {notification.type === 'success' && <CheckCircle color="success" />}
                {notification.type === 'error' && <Error color="error" />}
                
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2">
                    {notification.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
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
</Dialog>
```
- Notifications dialog showing:
  - List of notifications
  - Notification type (info, success, error)
  - Timestamp
  - "New" badge for unread

### Global Snackbar (Lines 1002-1012)
```javascript
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
```
- Global snackbar for temporary notifications
- Auto-hides after 4 seconds
- Positioned at bottom-right

---

## Application Flow

```
App.js (Main)
├── Check document status (every 30s)
├── Render AppBar
│   ├── Logo and title
│   ├── Document status badge
│   └── Settings, Help, Notifications buttons
├── Render Navigation
│   ├── Desktop: Sidebar
│   └── Mobile: Drawer
├── Render Tab Content
│   ├── Tab 0: ChatInterface
│   ├── Tab 1: DocumentAnalysis
│   ├── Tab 2: ProtocolSummary
│   ├── Tab 3: DocumentUpload
│   └── Tab 4: FeedbackDashboard
└── Render Dialogs
    ├── Settings
    ├── Help
    ├── Notifications
    └── Snackbar
```

---

## Key Features

| Feature | Purpose |
|---------|---------|
| **Tab navigation** | Switch between features |
| **Document status** | Shows if document is ready |
| **Settings** | Configure app behavior |
| **Help** | Quick start and troubleshooting |
| **Notifications** | Track system events |
| **Responsive layout** | Works on desktop and mobile |
| **Theme** | Professional blue/purple design |
| **Error boundary** | Catches component errors |

---

## Performance Optimizations

1. **useMemo**: Memoizes menu items
2. **useCallback**: Memoizes event handlers
3. **Lazy rendering**: Only renders active tab
4. **Polling interval**: 30 seconds (not too frequent)
5. **Conditional rendering**: Only renders visible elements

---

## Real-World Use Cases

1. **First-time user**: Sees help dialog with quick start
2. **Upload document**: Status updates in header
3. **Ask questions**: Switches to chat tab
4. **Configure settings**: Adjusts confidence threshold
5. **Check notifications**: Views system events

---

## Related Files

- `ChatInterface.js` - Chat tab content
- `DocumentAnalysis.js` - Analysis tab content
- `ProtocolSummary.js` - Summary tab content
- `DocumentUpload.js` - Upload tab content
- `FeedbackDashboard.js` - Analytics tab content
- `ErrorBoundary.js` - Error handling
- `api.js` - Backend communication
