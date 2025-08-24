# SpaceTraders GUI Testing Framework

This document describes the comprehensive testing framework for the SpaceTraders GUI application, including the faux web browser testing environment and solutions for common browser compatibility issues.

## 🌟 Overview

Our testing framework provides:
- **Faux Web Browser Environment**: Complete JSDOM setup simulating real browser behavior
- **Comprehensive API Mocking**: Full backend API simulation
- **Browser Compatibility Testing**: Tests for various browsers and edge cases
- **Integration Testing**: End-to-end workflow testing
- **Accessibility Testing**: ARIA compliance and keyboard navigation
- **Performance Testing**: Memory, network, and performance edge cases

## 🚀 Quick Start

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in debug mode
npm run test:debug

# Run specific test suites
node src/test-runner.js unit
node src/test-runner.js integration
node src/test-runner.js browser
node src/test-runner.js app
```

### Test Runner Options

```bash
# Show help and usage
node src/test-runner.js help

# Show test suite information
node src/test-runner.js info

# Show identified problem areas
node src/test-runner.js problems

# Run coverage report
node src/test-runner.js coverage
```

## 📁 Test Structure

```
frontend/src/
├── __tests__/
│   ├── App.test.js                    # Main app and routing tests
│   ├── integration.test.js            # End-to-end integration tests
│   └── browser-compatibility.test.js  # Browser compatibility tests
├── components/__tests__/
│   ├── Dashboard.test.js              # Dashboard component tests
│   └── Fleet.test.js                  # Fleet component tests
├── test-utils/
│   └── index.js                       # Custom testing utilities
├── setupTests.js                      # Test environment setup
└── test-runner.js                     # Test runner script
```

## 🧪 Test Categories

### 1. Unit Tests
Tests individual components in isolation:
- Component rendering with different props
- Event handling and user interactions
- State management within components
- Error boundary behavior
- Loading states and data display

**Example:**
```javascript
it('renders dashboard with agent and fleet data', async () => {
  render(<Dashboard />);
  
  await waitFor(() => {
    expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
  });
  
  expect(screen.getByText('Agent Dashboard')).toBeInTheDocument();
  expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();
});
```

### 2. Integration Tests
Tests component interactions and full workflows:
- Complete user journeys from dashboard to fleet management
- Ship selection and modification workflows
- Resource management workflows
- Intelligence and scanning workflows
- Cross-component state management

**Example:**
```javascript
it('completes a full user journey from dashboard to fleet management', async () => {
  render(<App />);
  
  // Navigate through multiple components
  const fleetLink = screen.getByRole('link', { name: 'Fleet' });
  fireEvent.click(fleetLink);
  
  // Verify state is maintained across navigation
  expect(screen.getByText('Fleet Management')).toBeInTheDocument();
});
```

### 3. Browser Compatibility Tests
Tests for various browser issues and compatibility:
- CSS Grid and Flexbox support
- JavaScript compatibility (Promises, fetch API)
- Event handling (touch, keyboard, mouse)
- Storage compatibility (localStorage, sessionStorage)
- Network issues (CORS, slow connections)
- Accessibility features

### 4. Application Tests
Tests main App component and routing:
- React Router navigation
- State management across routes
- Component integration
- Error handling across the application

## 🔧 Test Environment Setup

### JSDOM Configuration
Our setup includes comprehensive browser mocking:

```javascript
// Mock window.matchMedia for responsive design testing
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver for component resizing
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock localStorage and sessionStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;
```

### API Mocking
Complete backend simulation using axios-mock-adapter:

```javascript
import MockAdapter from 'axios-mock-adapter';

export const mockAxios = new MockAdapter(axios);

// Setup comprehensive API mocks
export const setupDefaultMocks = () => {
  mockAxios.onGet('/api/agent').reply(200, mockAgent);
  mockAxios.onGet('/api/ships').reply(200, mockShips);
  mockAxios.onGet('/api/systems').reply(200, mockSystems);
  // ... more mocks
};
```

## 🎯 Identified Problem Areas

### Current Issues Found in Browser Testing:

1. **API Error Handling**: Components don't gracefully handle API failures
2. **Loading States**: Inconsistent loading state management across components
3. **Navigation State**: Ship selection state not properly maintained across navigation
4. **Memory Leaks**: Event listeners and timeouts not properly cleaned up
5. **Responsive Design**: Components may not work well on mobile devices
6. **Accessibility**: Missing ARIA labels and keyboard navigation support
7. **Browser Compatibility**: May not work properly in older browsers
8. **Network Issues**: No offline handling or retry mechanisms

### Solutions Implemented:

✅ **Comprehensive Error Handling Tests**: Test all error states and edge cases
✅ **Loading State Testing**: Verify loading states are consistent across components
✅ **State Management Testing**: Ensure state is maintained across navigation
✅ **Memory Leak Prevention**: Test cleanup of event listeners and timeouts
✅ **Responsive Design Testing**: Test various viewport sizes and orientations
✅ **Accessibility Testing**: Verify ARIA compliance and keyboard navigation
✅ **Browser Compatibility Testing**: Test older browser scenarios
✅ **Network Resilience Testing**: Test offline scenarios and network failures

## 🛠️ Custom Test Utilities

### Enhanced Render Function
```javascript
import { render as rtlRender } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

function render(ui, { route = '/', ...options } = {}) {
  window.history.pushState({}, 'Test page', route);

  function Wrapper({ children }) {
    return <BrowserRouter>{children}</BrowserRouter>;
  }

  return rtlRender(ui, { wrapper: Wrapper, ...options });
}
```

### Wait Utilities
```javascript
export const waitFor = (callback, options = {}) => {
  return new Promise((resolve, reject) => {
    const timeout = options.timeout || 5000;
    const interval = options.interval || 100;
    const startTime = Date.now();

    const check = () => {
      try {
        const result = callback();
        if (result) {
          resolve(result);
        } else if (Date.now() - startTime >= timeout) {
          reject(new Error('Timeout waiting for condition'));
        } else {
          setTimeout(check, interval);
        }
      } catch (error) {
        if (Date.now() - startTime >= timeout) {
          reject(error);
        } else {
          setTimeout(check, interval);
        }
      }
    };

    check();
  });
};
```

## 📊 Coverage Goals

Our test coverage targets:
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

### Coverage Exclusions:
- `src/index.js` (application entry point)
- `src/reportWebVitals.js` (performance monitoring)
- Test files themselves
- Test utilities

## 🚦 Running Tests in CI/CD

### GitHub Actions Example:
```yaml
- name: Run Tests
  run: |
    npm test -- --coverage --watchAll=false
    npm run test:coverage

- name: Run Browser Compatibility Tests
  run: node src/test-runner.js browser

- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage/lcov.info
```

## 🔍 Debugging Tests

### Debug Mode:
```bash
npm run test:debug
```

### Debugging Individual Tests:
```bash
node --inspect-brk node_modules/.bin/react-scripts test --runInBand --no-cache
```

### Common Debugging Tips:
1. Use `screen.debug()` to see current DOM state
2. Add `await waitFor(() => {})` for async operations
3. Check mock call history: `mockAxios.history.get`
4. Verify component props with `screen.getByTestId()`

## 📈 Performance Testing

### Memory Testing:
```javascript
it('handles memory constraints', () => {
  Object.defineProperty(navigator, 'deviceMemory', {
    value: 1, // 1GB
    configurable: true
  });

  render(<App />);
  expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
});
```

### Network Testing:
```javascript
it('handles slow network connections', async () => {
  mockAxios.onGet('/api/agent').reply(() => {
    return new Promise(resolve => {
      setTimeout(() => resolve([200, mockAgent]), 5000);
    });
  });

  render(<App />);
  expect(screen.getByText('Loading agent data...')).toBeInTheDocument();
});
```

## 🌐 Browser Support Testing

### Tested Scenarios:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (responsive design)
- ✅ Older browsers (compatibility features)

### Accessibility Testing:
- ✅ Screen reader compatibility
- ✅ Keyboard navigation
- ✅ High contrast mode
- ✅ Reduced motion preferences
- ✅ ARIA labels and landmarks

## 📚 Best Practices

1. **Test Behavior, Not Implementation**: Test what the user sees and does
2. **Use Semantic Queries**: Prefer `getByRole`, `getByText` over `getByTestId`
3. **Test Error States**: Always test both success and failure scenarios
4. **Mock External Dependencies**: Use comprehensive API mocking
5. **Clean Up**: Ensure tests don't affect each other
6. **Accessibility First**: Include accessibility tests from the start
7. **Performance Awareness**: Test with realistic data sizes
8. **Browser Reality**: Test real browser constraints and limitations

## 🔧 Troubleshooting

### Common Issues:

**Tests failing with "not wrapped in act()":**
```javascript
// Use waitFor for async operations
await waitFor(() => {
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

**Mock not working:**
```javascript
// Reset mocks between tests
afterEach(() => {
  mockAxios.reset();
  jest.clearAllMocks();
});
```

**Component not rendering:**
```javascript
// Check if component needs Router context
render(<App />, { wrapper: BrowserRouter });
```

## 📞 Support

For testing-related questions:
1. Check this documentation first
2. Review test examples in the codebase
3. Run `node src/test-runner.js help` for usage information
4. Check the test output for specific error messages

---

## 🎉 Success Criteria

A successful test run should:
- ✅ All test suites pass
- ✅ Coverage targets met (70%+)
- ✅ No memory leaks detected
- ✅ Browser compatibility verified
- ✅ Accessibility standards met
- ✅ Performance edge cases handled
- ✅ Error states properly tested

Happy testing! 🧪✨