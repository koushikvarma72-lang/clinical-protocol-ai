// Performance monitoring utilities
export class PerformanceMonitor {
  static timers = new Map();
  
  static startTimer(name) {
    this.timers.set(name, performance.now());
  }
  
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
}

// Debounce utility for performance optimization
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

// Throttle utility for performance optimization
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

// Memory usage monitoring
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

// Bundle size analyzer (development only)
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