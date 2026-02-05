# api.js - Line-by-Line Explanation

**File Purpose**: Centralized API communication layer that handles all backend requests. Manages HTTP requests, error handling, caching, and interceptors for the entire frontend application.

**Complexity Level**: ⭐⭐ Intermediate (200 lines)

---

## Import Statements (Lines 1-2)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';
```
- Imports axios library for HTTP requests
- Defines backend API base URL (port 8001)

---

## Axios Instance Creation (Lines 4-10)

```javascript
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for long operations
  headers: {
    'Content-Type': 'application/json',
  },
});
```
- Creates axios instance with default configuration
- Sets 5-minute timeout for long operations (like document analysis)
- Sets JSON content type for all requests

**Real-World Analogy**: Like creating a phone with pre-configured settings - all calls use these defaults.

---

## Request Interceptor (Lines 12-22)

```javascript
api.interceptors.request.use(
  (config) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);
```
- Logs all API requests in development mode
- Shows HTTP method and URL
- Helps with debugging
- Rejects promise if request setup fails

---

## Response Interceptor (Lines 24-42)

```javascript
api.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    }
    return response;
  },
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'Network error occurred';
    
    if (process.env.NODE_ENV === 'development') {
      console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status || 'Network Error'}`, errorMessage);
    }
    
    // Transform error for better handling
    const transformedError = {
      ...error,
      message: errorMessage,
      status: error.response?.status,
      data: error.response?.data
    };
    
    return Promise.reject(transformedError);
  }
);
```
- Logs successful responses in development
- Extracts error messages from backend response
- Transforms errors into consistent format
- Includes status code and response data
- Helps with debugging and error handling

---

## Cache Implementation (Lines 44-54)

```javascript
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const getCachedData = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

const setCachedData = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() });
};
```
- Simple in-memory cache for API responses
- Caches data for 5 minutes
- `getCachedData`: Returns cached data if still valid
- `setCachedData`: Stores data with timestamp
- Reduces unnecessary API calls

**Real-World Analogy**: Like remembering information you just looked up - don't look it up again for 5 minutes.

---

## Upload PDF Function (Lines 56-75)

```javascript
export const uploadPDF = async (file) => {
  if (!file) {
    throw new Error('No file provided');
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/upload-pdf`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for upload
    });
    
    // Clear status cache after successful upload
    cache.delete('status');
    
    return response.data;
  } catch (error) {
    throw new Error(`Failed to upload PDF: ${error.message}`);
  }
};
```
- Uploads PDF file to backend
- Validates file exists
- Uses FormData for multipart upload
- 2-minute timeout for file upload
- Clears status cache after successful upload
- Throws error with descriptive message

---

## Upload PDF with Progress Function (Lines 77-105)

```javascript
export const uploadPDFWithProgress = async (file, onProgress) => {
  if (!file) {
    throw new Error('No file provided');
  }
  
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    throw new Error('Only PDF files are supported');
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/upload-pdf-with-progress`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for upload
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });
    
    // Clear status cache after successful upload
    cache.delete('status');
    
    return response.data;
  } catch (error) {
    if (error.status === 413) {
      throw new Error('File is too large. Please upload a smaller PDF file.');
    }
    throw new Error(`Failed to upload file: ${error.message}`);
  }
};
```
- Uploads PDF with progress tracking
- Validates file is PDF
- Calls `onProgress` callback with percentage
- Handles file size errors (413 status)
- Clears cache after successful upload

---

## Get Upload Progress Function (Lines 107-117)

```javascript
export const getUploadProgress = async (taskId) => {
  if (!taskId) {
    throw new Error('Task ID is required');
  }
  
  try {
    const response = await api.get(`/upload-progress/${taskId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get upload progress: ${error.message}`);
  }
};
```
- Polls backend for upload progress
- Validates task ID provided
- Returns progress data (percentage, stage, details)
- Used by DocumentUpload component

---

## Ask Question Function (Lines 119-130)

```javascript
export const askQuestion = async (question) => {
  if (!question?.trim()) {
    throw new Error('Question cannot be empty');
  }
  
  try {
    const response = await api.post('/ask', { question });
    return response.data;
  } catch (error) {
    if (error.status === 408 || error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. The AI is taking longer than expected to respond.');
    }
    throw new Error(`Failed to get answer: ${error.message}`);
  }
};
```
- Sends question to AI backend
- Validates question is not empty
- Handles timeout errors gracefully
- Returns answer, sources, evidence, confidence

---

## Extract Key Sections Function (Lines 132-147)

```javascript
export const extractKeySections = async () => {
  try {
    console.log('🔍 Starting key sections extraction...');
    const response = await api.get('/extract-key-sections', {
      timeout: 300000 // 5 minutes timeout for analysis
    });
    console.log('✅ Key sections extracted successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to extract sections:', error);
    if (error.code === 'ECONNABORTED') {
      throw new Error('Analysis timed out. The document analysis is taking longer than expected.');
    }
    throw new Error(`Failed to extract sections: ${error.message}`);
  }
};
```
- Calls backend to extract key sections
- 5-minute timeout for long analysis
- Logs detailed debug information
- Handles timeout errors

---

## Submit Review Function (Lines 149-158)

```javascript
export const submitReview = async (sections) => {
  if (!sections) {
    throw new Error('Sections data is required');
  }
  
  try {
    const response = await api.post('/review-sections', { sections });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to submit review: ${error.message}`);
  }
};
```
- Sends approved sections to backend
- Backend generates summary from sections
- Validates sections provided
- Returns generated summary

---

## Submit Feedback Function (Lines 160-170)

```javascript
export const submitFeedback = async (feedbackData) => {
  if (!feedbackData) {
    throw new Error('Feedback data is required');
  }
  
  try {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  } catch (error) {
    // Don't throw for feedback errors, just log them
    console.warn('Failed to submit feedback:', error.message);
    return null;
  }
};
```
- Records user feedback (likes, dislikes, copies, etc.)
- Silently fails if submission fails
- Doesn't interrupt user experience
- Returns null on error

---

## Get Feedback Stats Function (Lines 172-183)

```javascript
export const getFeedbackStats = async (days = 7) => {
  const cacheKey = `feedback-stats-${days}`;
  const cached = getCachedData(cacheKey);
  if (cached) return cached;
  
  try {
    const response = await api.get(`/feedback/stats?days=${days}`);
    setCachedData(cacheKey, response.data);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get feedback stats: ${error.message}`);
  }
};
```
- Gets feedback statistics for specified days
- Uses cache to avoid repeated calls
- Returns stats like satisfaction rate, reaction counts
- Used by FeedbackDashboard component

---

## Get Recent Feedback Function (Lines 185-196)

```javascript
export const getRecentFeedback = async (limit = 20) => {
  const cacheKey = `recent-feedback-${limit}`;
  const cached = getCachedData(cacheKey);
  if (cached) return cached;
  
  try {
    const response = await api.get(`/feedback/recent?limit=${limit}`);
    setCachedData(cacheKey, response.data);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get recent feedback: ${error.message}`);
  }
};
```
- Gets recent feedback entries
- Caches results for 5 minutes
- Returns array of feedback objects
- Used by FeedbackDashboard component

---

## Get Status Function (Lines 198-208)

```javascript
export const getStatus = async () => {
  const cacheKey = 'status';
  const cached = getCachedData(cacheKey);
  if (cached) return cached;
  
  try {
    const response = await api.get('/status');
    setCachedData(cacheKey, response.data);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get status: ${error.message}`);
  }
};
```
- Gets system status (document ready, vector count)
- Caches for 5 minutes
- Returns status object
- Used by App component to check if document is loaded

---

## Health Check Function (Lines 210-216)

```javascript
export const healthCheck = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.data;
  } catch (error) {
    throw new Error('Backend service is unavailable');
  }
};
```
- Checks if backend is running
- 5-second timeout
- Used to verify backend connectivity
- Throws error if backend unavailable

---

## Clear Cache Function (Lines 218-221)

```javascript
export const clearCache = () => {
  cache.clear();
};
```
- Clears all cached data
- Useful when data needs to be refreshed
- Called after uploads or major changes

---

## Export Default (Line 223)

```javascript
export default api;
```
- Exports axios instance for direct use if needed

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload-pdf` | POST | Upload PDF file |
| `/upload-pdf-with-progress` | POST | Upload with progress tracking |
| `/upload-progress/{taskId}` | GET | Get upload progress |
| `/ask` | POST | Ask question about document |
| `/extract-key-sections` | GET | Extract key sections |
| `/review-sections` | POST | Generate summary from sections |
| `/feedback` | POST | Submit user feedback |
| `/feedback/stats` | GET | Get feedback statistics |
| `/feedback/recent` | GET | Get recent feedback |
| `/status` | GET | Get system status |
| `/health` | GET | Health check |

---

## Error Handling Strategy

1. **Validation**: Check inputs before sending
2. **Timeout handling**: Specific messages for timeouts
3. **File size errors**: Specific message for 413 status
4. **Feedback errors**: Silently fail to not interrupt UX
5. **Consistent format**: Transform all errors to same format

---

## Caching Strategy

| Data | Duration | Purpose |
|------|----------|---------|
| Status | 5 min | Reduce status checks |
| Feedback stats | 5 min | Reduce dashboard queries |
| Recent feedback | 5 min | Reduce dashboard queries |

---

## Performance Optimizations

1. **Caching**: Reduces unnecessary API calls
2. **Timeouts**: Prevents hanging requests
3. **Interceptors**: Centralized logging and error handling
4. **Async/await**: Non-blocking operations
5. **Error transformation**: Consistent error handling

---

## Real-World Use Cases

1. **Upload document**: User uploads PDF for analysis
2. **Ask question**: User asks about protocol
3. **Extract sections**: AI extracts key information
4. **Generate summary**: Create executive summary
5. **Track feedback**: Record user satisfaction
6. **Monitor status**: Check if document is ready

---

## Related Files

- `ChatInterface.js` - Uses askQuestion
- `DocumentUpload.js` - Uses uploadPDFWithProgress
- `DocumentAnalysis.js` - Uses extractKeySections
- `ProtocolSummary.js` - Uses submitReview
- `FeedbackDashboard.js` - Uses feedback functions
- `App.js` - Uses getStatus
