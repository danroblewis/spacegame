// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Global error handler to catch unhandled errors during tests
let consoleError = console.error;
beforeEach(() => {
  // Override console.error to catch React warnings and errors
  console.error = (...args) => {
    // Only fail tests on actual compilation errors, not deprecation warnings
    if (
      args[0] &&
      typeof args[0] === 'string' &&
      (args[0].includes('Failed to compile') ||
       args[0].includes('SyntaxError') ||
       (args[0].includes('Error:') && !args[0].includes('deprecated')))
    ) {
      throw new Error(`React Error: ${args[0]}`);
    }
    consoleError(...args);
  };
});

afterEach(() => {
  console.error = consoleError;
});

// Add custom Jest matchers for better error reporting
expect.extend({
  toRenderWithoutErrors(received) {
    try {
      received();
      return {
        message: () => `Component rendered successfully`,
        pass: true
      };
    } catch (error) {
      return {
        message: () => `Component failed to render: ${error.message}`,
        pass: false
      };
    }
  }
});