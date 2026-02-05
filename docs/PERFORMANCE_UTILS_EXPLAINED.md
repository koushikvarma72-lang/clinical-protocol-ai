# performance.js - Line-by-Line Explanation

**File Purpose**: Utility functions for performance monitoring, optimization, and debugging. Includes timing measurements, debouncing, throttling, and memory analysis.

**Complexity Level**: ⭐ Beginner (80 lines)

---

## PerformanceMonitor Class (Lines 1-30)

### Class Definition
```javascript
export class PerformanceMonitor {
  static timers = new Map();
```
- Static class for performance monitoring
- `timers` Map stores start times for named operations

### Start Timer Method
```javascript
static startTimer(name) {
  this.timers.set(name, performance.now());
}
```
- Records current time for a named operation
- Uses `performance.now()` for high-resolution timing
- Stores in Map with operation name as key

**Real-World Analogy**: Like pressing start on a stopwatch.

### End Timer Method
```javascript
static endTimer(name) {
  const startTime = this.timers.get(name);
  if (startTime) {
    const duration = performance.now() - startTime;
    this.timers.delete(name);
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
    }
    
    return duration;
  }
  return null;
}
```
- Calculates elapsed time since startTimer was called
- Logs duration in development mode
- Removes timer from Map
- Returns duration in milliseconds
- Returns null if timer not found

**Real-World Analogy**: Like pressing stop on a stopwatch and reading the time.

### Measure Component Method
```javascript
static measureComponent(WrappedComponent, componentName) {
  return function MeasuredComponent(props) {
    React.useEffect(() => {
      PerformanceMonitor.startTimer(`${componentName} render`);
      return () => {
        PerformanceMonitor.endTimer(`${componentName} render`);
      };
    });
    
    return React.createElement(WrappedComponent, props);
  };
}
```
- Higher-order component that measures render time
- Starts timer when component mounts
- Ends timer when component unmounts
- Logs render duration
- Useful for identifying slow components

**Usage Example**:
```javascript
const MeasuredChatInterface = PerformanceMonitor.measureComponent(
  ChatInterface, 
  'ChatInterface'
);
```

---

## Debounce Function (Lines 32-45)

```javascript
export const debounce = (func, wait, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
};
```
- Delays function execution until after specified wait time
- Resets timer if called again before wait completes
- `immediate`: If true, calls function immediately, then waits

**Real-World Analogy**: Like a doorbell that waits for you to stop ringing before playing the sound.

**Use Cases**:
- Search input: Wait for user to stop typing before searching
- Window resize: Wait for resize to complete before recalculating
- Auto-save: Wait for user to stop editing before saving

**Example**:
```javascript
const debouncedSearch = debounce((query) => {
  searchDocuments(query);
}, 500);

// Call many times, but only searches after 500ms of inactivity
input.addEventListener('input', (e) => debouncedSearch(e.target.value));
```

---

## Throttle Function (Lines 47-54)

```javascript
export const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
```
- Limits function execution to once per specified time interval
- Ignores calls that happen too frequently
- Resets throttle after interval

**Real-World Analogy**: Like a water fountain that only dispenses water once per second, no matter how many times you press the button.

**Use Cases**:
- Scroll events: Limit scroll handler to once per 100ms
- Mouse move: Limit tracking to once per 50ms
- Button clicks: Prevent double-clicks

**Example**:
```javascript
const throttledScroll = throttle(() => {
  updateScrollPosition();
}, 100);

window.addEventListener('scroll', throttledScroll);
```

---

## Get Memory Usage Function (Lines 56-66)

```javascript
export const getMemoryUsage = () => {
  if (performance.memory) {
    return {
      used: Math.round(performance.memory.usedJSHeapSize / 1048576),
      total: Math.round(performance.memory.totalJSHeapSize / 1048576),
      limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576)
    };
  }
  return null;
};
```
- Returns current memory usage in MB
- `used`: JavaScript heap currently in use
- `total`: Total allocated heap
- `limit`: Maximum heap size
- Returns null if not supported (not all browsers)

**Real-World Analogy**: Like checking how much RAM your app is using.

**Example**:
```javascript
const memory = getMemoryUsage();
console.log(`Using ${memory.used}MB of ${memory.limit}MB`);
```

---

## Analyze Bundle Size Function (Lines 68-80)

```javascript
export const analyzeBundleSize = () => {
  if (process.env.NODE_ENV === 'development') {
    const scripts = Array.from(document.querySelectorAll('script[src]'));
    const totalSize = scripts.reduce((total, script) => {
      return total + (script.src.length || 0);
    }, 0);
    
    console.log('📦 Estimated bundle size:', Math.round(totalSize / 1024), 'KB');
    return totalSize;
  }
  return null;
};
```
- Estimates total bundle size by summing script URLs
- Only runs in development mode
- Logs result to console
- Returns total size in bytes

**Note**: This is a rough estimate based on URL lengths, not actual file sizes.

**Real-World Analogy**: Like checking the total size of all JavaScript files loaded.

---

## Performance Optimization Strategies

### 1. Debouncing
```javascript
// Bad: Searches on every keystroke
input.addEventListener('input', (e) => search(e.target.value));

// Good: Searches after user stops typing
const debouncedSearch = debounce((query) => search(query), 300);
input.addEventListener('input', (e) => debouncedSearch(e.target.value));
```

### 2. Throttling
```javascript
// Bad: Runs on every scroll event (60+ times per second)
window.addEventListener('scroll', updateScrollPosition);

// Good: Runs at most once per 100ms
const throttledScroll = throttle(updateScrollPosition, 100);
window.addEventListener('scroll', throttledScroll);
```

### 3. Component Measurement
```javascript
// Measure render time of slow component
const MeasuredComponent = PerformanceMonitor.measureComponent(
  SlowComponent,
  'SlowComponent'
);
```

---

## Performance Metrics

| Metric | Purpose | Normal Range |
|--------|---------|--------------|
| **Render time** | How long component takes to render | <16ms (60fps) |
| **Memory usage** | How much RAM app uses | <50MB |
| **Bundle size** | Total JavaScript size | <500KB |
| **API response** | How long API calls take | <1000ms |

---

## Real-World Use Cases

### 1. Search Input Optimization
```javascript
const debouncedSearch = debounce((query) => {
  askQuestion(query);
}, 500);

<TextField onChange={(e) => debouncedSearch(e.target.value)} />
```

### 2. Window Resize Handling
```javascript
const throttledResize = throttle(() => {
  recalculateLayout();
}, 250);

window.addEventListener('resize', throttledResize);
```

### 3. Performance Monitoring
```javascript
PerformanceMonitor.startTimer('document-analysis');
// ... do analysis ...
PerformanceMonitor.endTimer('document-analysis');
// Logs: ⏱️ document-analysis: 1234.56ms
```

### 4. Memory Monitoring
```javascript
const memory = getMemoryUsage();
if (memory.used > memory.limit * 0.9) {
  console.warn('Memory usage critical!');
}
```

---

## Debounce vs Throttle

| Feature | Debounce | Throttle |
|---------|----------|----------|
| **Timing** | Waits for inactivity | Limits frequency |
| **Use case** | Search, auto-save | Scroll, resize |
| **Calls** | One after wait | Multiple, spaced out |
| **Example** | Type 5 chars, search once | Scroll 100 times, handle 10 times |

---

## Browser Compatibility

| Function | Chrome | Firefox | Safari | Edge |
|----------|--------|---------|--------|------|
| `performance.now()` | ✅ | ✅ | ✅ | ✅ |
| `performance.memory` | ✅ | ❌ | ❌ | ✅ |
| `document.querySelectorAll` | ✅ | ✅ | ✅ | ✅ |

---

## Performance Tips

1. **Use debounce for**: Search, auto-save, form validation
2. **Use throttle for**: Scroll, resize, mouse move
3. **Monitor memory**: Check for memory leaks
4. **Measure components**: Identify slow renders
5. **Analyze bundle**: Keep JavaScript size small

---

## Related Files

- `ChatInterface.js` - Could use debounce for search
- `DocumentUpload.js` - Could use throttle for progress updates
- `App.js` - Could use performance monitoring
- `api.js` - Could measure API response times
