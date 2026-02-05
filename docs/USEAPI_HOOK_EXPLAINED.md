# useApi.js - Line-by-Line Explanation

**File Purpose**: Custom React hook that provides a reusable interface for making API calls with built-in loading, error handling, and retry logic.

**Complexity Level**: ⭐ Beginner (50 lines)

---

## Import Statements (Lines 1-2)

```javascript
import { useState, useCallback } from 'react';
```
- Imports React hooks for state management and memoization

---

## Hook Definition (Lines 4-5)

```javascript
export const useApi = () => {
```
- Exports custom hook that can be used in any component
- Returns object with state and functions

---

## State Management (Lines 6-7)

```javascript
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```
- `loading`: Tracks if API call is in progress
- `error`: Stores error message if call fails

---

## Execute Function (Lines 9-50)

```javascript
const execute = useCallback(async (apiCall, options = {}) => {
```
- Main function that executes API calls
- Accepts `apiCall` function and optional `options`
- Uses `useCallback` for performance optimization

```javascript
  const { 
    onSuccess, 
    onError, 
    showLoading = true,
    retries = 0,
    retryDelay = 1000 
  } = options;
```
- Destructures options:
  - `onSuccess`: Callback on successful response
  - `onError`: Callback on error
  - `showLoading`: Whether to show loading state (default: true)
  - `retries`: Number of retry attempts (default: 0)
  - `retryDelay`: Delay between retries in ms (default: 1000)

```javascript
  if (showLoading) setLoading(true);
  setError(null);

  let attempt = 0;
```
- Sets loading state if requested
- Clears previous errors
- Initializes retry counter

```javascript
  while (attempt <= retries) {
    try {
      const result = await apiCall();
      
      if (showLoading) setLoading(false);
      
      if (onSuccess) onSuccess(result);
      return result;
```
- Retry loop: attempts API call up to `retries + 1` times
- On success:
  - Clears loading state
  - Calls success callback
  - Returns result

```javascript
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
```
- On error:
  - Increments attempt counter
  - If all retries exhausted:
    - Extracts error message
    - Sets error state
    - Clears loading state
    - Calls error callback or logs error
    - Throws error

```javascript
      // Wait before retry
      if (attempt <= retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
      }
```
- Waits before retrying
- Delay increases with each attempt (exponential backoff)
- Example: 1st retry waits 1s, 2nd waits 2s, 3rd waits 3s

---

## Reset Function (Lines 52-56)

```javascript
const reset = useCallback(() => {
  setLoading(false);
  setError(null);
}, []);
```
- Clears loading and error states
- Useful for resetting hook state between calls
- Uses `useCallback` for performance

---

## Return Object (Lines 58-64)

```javascript
return {
  loading,
  error,
  execute,
  reset
};
```
- Returns object with:
  - `loading`: Current loading state
  - `error`: Current error message
  - `execute`: Function to make API calls
  - `reset`: Function to clear state

---

## Usage Example

```javascript
// In a component
const { loading, error, execute } = useApi();

// Make API call
const handleClick = async () => {
  await execute(
    () => askQuestion('What is the drug?'),
    {
      onSuccess: (result) => console.log('Success:', result),
      onError: (err) => console.error('Error:', err),
      retries: 2,
      retryDelay: 1000
    }
  );
};

// In JSX
{loading && <CircularProgress />}
{error && <Alert severity="error">{error}</Alert>}
<Button onClick={handleClick}>Ask Question</Button>
```

---

## Key Features

| Feature | Purpose |
|---------|---------|
| **Loading state** | Shows spinner while loading |
| **Error handling** | Catches and displays errors |
| **Retry logic** | Automatically retries failed requests |
| **Exponential backoff** | Increases delay between retries |
| **Callbacks** | onSuccess and onError hooks |
| **Reset function** | Clear state between calls |
| **Memoization** | Performance optimization |

---

## Real-World Use Cases

1. **Simple API call**: No retries, just loading and error
```javascript
const { loading, error, execute } = useApi();
await execute(() => getStatus());
```

2. **With retries**: Retry failed requests
```javascript
await execute(() => askQuestion(q), { retries: 3 });
```

3. **With callbacks**: Handle success/error
```javascript
await execute(() => uploadFile(file), {
  onSuccess: (result) => setFile(result),
  onError: (err) => showError(err)
});
```

4. **Without loading state**: For background requests
```javascript
await execute(() => submitFeedback(data), { showLoading: false });
```

---

## Error Handling Flow

```
1. Call execute with API function
   ↓
2. Set loading = true
   ↓
3. Try to execute API call
   ↓
4a. Success:
    - Set loading = false
    - Call onSuccess callback
    - Return result
   ↓
4b. Error:
    - Increment attempt counter
    - If retries left:
      - Wait (exponential backoff)
      - Retry
    - If no retries left:
      - Set error message
      - Set loading = false
      - Call onError callback
      - Throw error
```

---

## Retry Strategy

The hook implements exponential backoff for retries:

| Attempt | Delay | Total Wait |
|---------|-------|-----------|
| 1st | 1000ms | 1s |
| 2nd | 2000ms | 3s |
| 3rd | 3000ms | 6s |

This prevents overwhelming the server with rapid retries.

---

## Performance Optimizations

1. **useCallback**: Memoizes execute and reset functions
2. **Conditional loading**: Only sets loading if requested
3. **Early return**: Returns immediately on success
4. **Efficient retries**: Exponential backoff prevents hammering

---

## Comparison with Direct API Calls

**Without hook**:
```javascript
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

const handleClick = async () => {
  setLoading(true);
  try {
    const result = await askQuestion(q);
    setLoading(false);
    // handle success
  } catch (err) {
    setError(err.message);
    setLoading(false);
  }
};
```

**With hook**:
```javascript
const { loading, error, execute } = useApi();

const handleClick = async () => {
  await execute(() => askQuestion(q), {
    onSuccess: (result) => { /* handle success */ }
  });
};
```

The hook reduces boilerplate and provides consistent error handling.

---

## Related Files

- `api.js` - API functions that work with this hook
- `ChatInterface.js` - Could use this hook
- `DocumentUpload.js` - Could use this hook
- `DocumentAnalysis.js` - Could use this hook
