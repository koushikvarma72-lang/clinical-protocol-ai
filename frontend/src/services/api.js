import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for long operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
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

// Response interceptor for error handling
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

// Simple cache implementation
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

// Health check function
export const healthCheck = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.data;
  } catch (error) {
    throw new Error('Backend service is unavailable');
  }
};

// Clear all cached data
export const clearCache = () => {
  cache.clear();
};

export default api;