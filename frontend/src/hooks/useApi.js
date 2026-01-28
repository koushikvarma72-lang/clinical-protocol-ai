import { useState, useCallback } from 'react';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall, options = {}) => {
    const { 
      onSuccess, 
      onError, 
      showLoading = true,
      retries = 0,
      retryDelay = 1000 
    } = options;

    if (showLoading) setLoading(true);
    setError(null);

    let attempt = 0;
    
    while (attempt <= retries) {
      try {
        const result = await apiCall();
        
        if (showLoading) setLoading(false);
        
        if (onSuccess) onSuccess(result);
        return result;
        
      } catch (err) {
        attempt++;
        
        if (attempt > retries) {
          const errorMessage = err.response?.data?.message || err.message || 'An error occurred';
          setError(errorMessage);
          
          if (showLoading) setLoading(false);
          
          if (onError) {
            onError(err);
          } else {
            console.error('API Error:', err);
          }
          
          throw err;
        }
        
        // Wait before retry
        if (attempt <= retries) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
        }
      }
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return {
    loading,
    error,
    execute,
    reset
  };
};

export default useApi;