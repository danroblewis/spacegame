#!/usr/bin/env node

/**
 * SpaceTraders GUI Test Runner
 * 
 * This script provides a comprehensive testing suite for the SpaceTraders GUI application.
 * It includes unit tests, integration tests, and browser compatibility tests.
 */

const { execSync } = require('child_process');
const path = require('path');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

// Test suites configuration
const testSuites = {
  unit: {
    name: 'Unit Tests',
    description: 'Tests individual components in isolation',
    pattern: 'src/**/*.test.js',
    files: [
      'src/components/__tests__/Dashboard.test.js',
      'src/components/__tests__/Fleet.test.js'
    ]
  },
  integration: {
    name: 'Integration Tests',
    description: 'Tests component interactions and full workflows',
    pattern: 'src/__tests__/integration.test.js',
    files: [
      'src/__tests__/integration.test.js'
    ]
  },
  app: {
    name: 'Application Tests',
    description: 'Tests main App component and routing',
    pattern: 'src/__tests__/App.test.js',
    files: [
      'src/__tests__/App.test.js'
    ]
  },
  browser: {
    name: 'Browser Compatibility Tests',
    description: 'Tests browser compatibility and edge cases',
    pattern: 'src/__tests__/browser-compatibility.test.js',
    files: [
      'src/__tests__/browser-compatibility.test.js'
    ]
  }
};

function printHeader() {
  console.log(`${colors.cyan}${colors.bright}
╔══════════════════════════════════════════════════════════════╗
║                    SpaceTraders GUI Test Suite              ║
║              Comprehensive Testing Framework                ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
}

function printTestSuiteInfo() {
  console.log(`${colors.yellow}${colors.bright}Available Test Suites:${colors.reset}\n`);
  
  Object.entries(testSuites).forEach(([key, suite]) => {
    console.log(`${colors.blue}${colors.bright}${suite.name}${colors.reset}`);
    console.log(`  Description: ${suite.description}`);
    console.log(`  Pattern: ${suite.pattern}`);
    console.log(`  Files: ${suite.files.length} test file(s)`);
    console.log('');
  });
}

function printUsage() {
  console.log(`${colors.green}${colors.bright}Usage:${colors.reset}
  
  npm test                     Run all tests
  npm run test:coverage        Run tests with coverage report
  npm run test:debug          Run tests in debug mode
  
  node src/test-runner.js [suite]   Run specific test suite:
    - unit                     Run unit tests only
    - integration             Run integration tests only
    - app                     Run app tests only
    - browser                 Run browser compatibility tests only
    - all                     Run all tests (default)
    
${colors.yellow}Examples:${colors.reset}
  node src/test-runner.js unit
  node src/test-runner.js integration
  node src/test-runner.js browser
  
${colors.magenta}Test Environment Setup:${colors.reset}
  The test environment includes:
  - JSDOM for browser simulation
  - Comprehensive API mocking with axios-mock-adapter
  - React Testing Library for component testing
  - Custom test utilities for common operations
  
${colors.cyan}Key Features:${colors.reset}
  ✓ Faux web browser environment with JSDOM
  ✓ Complete API mocking for all endpoints
  ✓ Error state and edge case testing
  ✓ Browser compatibility testing
  ✓ Integration workflow testing
  ✓ Accessibility testing
  ✓ Performance testing scenarios
`);
}

function runTestSuite(suiteName) {
  const suite = testSuites[suiteName];
  if (!suite) {
    console.error(`${colors.red}Error: Unknown test suite '${suiteName}'${colors.reset}`);
    console.log(`Available suites: ${Object.keys(testSuites).join(', ')}`);
    process.exit(1);
  }

  console.log(`${colors.green}${colors.bright}Running ${suite.name}...${colors.reset}`);
  console.log(`${suite.description}\n`);

  try {
    const testCommand = `npx react-scripts test --testPathPattern="${suite.pattern}" --watchAll=false --coverage=false --verbose`;
    console.log(`${colors.blue}Command: ${testCommand}${colors.reset}\n`);
    
    execSync(testCommand, { 
      stdio: 'inherit',
      cwd: process.cwd()
    });
    
    console.log(`${colors.green}${colors.bright}✓ ${suite.name} completed successfully!${colors.reset}\n`);
  } catch (error) {
    console.error(`${colors.red}${colors.bright}✗ ${suite.name} failed!${colors.reset}`);
    console.error(`Exit code: ${error.status}\n`);
    process.exit(error.status || 1);
  }
}

function runAllTests() {
  console.log(`${colors.green}${colors.bright}Running All Test Suites...${colors.reset}\n`);
  
  const results = {};
  
  for (const [key, suite] of Object.entries(testSuites)) {
    try {
      console.log(`${colors.cyan}Running ${suite.name}...${colors.reset}`);
      const testCommand = `npx react-scripts test --testPathPattern="${suite.pattern}" --watchAll=false --coverage=false --silent`;
      
      execSync(testCommand, { 
        stdio: 'pipe',
        cwd: process.cwd()
      });
      
      results[key] = { success: true, suite };
      console.log(`${colors.green}✓ ${suite.name} passed${colors.reset}`);
    } catch (error) {
      results[key] = { success: false, suite, error };
      console.log(`${colors.red}✗ ${suite.name} failed${colors.reset}`);
    }
  }
  
  // Print summary
  console.log(`\n${colors.cyan}${colors.bright}Test Results Summary:${colors.reset}`);
  console.log('═'.repeat(50));
  
  const passed = Object.values(results).filter(r => r.success).length;
  const failed = Object.values(results).filter(r => !r.success).length;
  
  for (const [key, result] of Object.entries(results)) {
    const status = result.success ? 
      `${colors.green}PASSED${colors.reset}` : 
      `${colors.red}FAILED${colors.reset}`;
    console.log(`${result.suite.name.padEnd(30)} ${status}`);
  }
  
  console.log('═'.repeat(50));
  console.log(`Total: ${passed + failed} | ${colors.green}Passed: ${passed}${colors.reset} | ${colors.red}Failed: ${failed}${colors.reset}`);
  
  if (failed > 0) {
    console.log(`\n${colors.red}${colors.bright}Some tests failed. Check the output above for details.${colors.reset}`);
    process.exit(1);
  } else {
    console.log(`\n${colors.green}${colors.bright}All tests passed! 🎉${colors.reset}`);
  }
}

function runCoverageReport() {
  console.log(`${colors.green}${colors.bright}Running Tests with Coverage Report...${colors.reset}\n`);
  
  try {
    const coverageCommand = 'npx react-scripts test --coverage --watchAll=false';
    console.log(`${colors.blue}Command: ${coverageCommand}${colors.reset}\n`);
    
    execSync(coverageCommand, { 
      stdio: 'inherit',
      cwd: process.cwd()
    });
    
    console.log(`\n${colors.green}${colors.bright}Coverage report generated successfully!${colors.reset}`);
    console.log(`${colors.yellow}Check the coverage/ directory for detailed HTML report.${colors.reset}`);
  } catch (error) {
    console.error(`${colors.red}Coverage report failed!${colors.reset}`);
    process.exit(error.status || 1);
  }
}

function printProblemAreas() {
  console.log(`${colors.yellow}${colors.bright}Common Issues in Web Browser Testing:${colors.reset}

${colors.red}Identified Problem Areas:${colors.reset}
  1. API Error Handling: Components don't gracefully handle API failures
  2. Loading States: Inconsistent loading state management
  3. Navigation State: Ship selection state not maintained across navigation
  4. Memory Leaks: Event listeners and timeouts not properly cleaned up
  5. Responsive Design: Components may not work well on mobile devices
  6. Accessibility: Missing ARIA labels and keyboard navigation
  7. Browser Compatibility: May not work in older browsers
  8. Network Issues: No offline handling or retry mechanisms

${colors.green}Test Coverage Areas:${colors.reset}
  ✓ Component rendering and props
  ✓ User interactions and event handling
  ✓ API mocking and error states
  ✓ Navigation and routing
  ✓ State management across components
  ✓ Browser compatibility issues
  ✓ Accessibility compliance
  ✓ Performance edge cases
  ✓ Integration workflows

${colors.cyan}Recommendations:${colors.reset}
  - Add error boundaries for better error handling
  - Implement consistent loading state patterns
  - Add proper cleanup in useEffect hooks
  - Improve responsive design with CSS Grid/Flexbox
  - Add ARIA labels and keyboard navigation support
  - Implement service worker for offline functionality
  - Add retry mechanisms for failed API calls
  - Use React.memo and useMemo for performance optimization
`);
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  printHeader();

  switch (command) {
    case 'help':
    case '--help':
    case '-h':
      printUsage();
      printTestSuiteInfo();
      break;
      
    case 'info':
      printTestSuiteInfo();
      break;
      
    case 'problems':
      printProblemAreas();
      break;
      
    case 'coverage':
      runCoverageReport();
      break;
      
    case 'all':
      runAllTests();
      break;
      
    case 'unit':
    case 'integration':
    case 'app':
    case 'browser':
      runTestSuite(command);
      break;
      
    default:
      if (testSuites[command]) {
        runTestSuite(command);
      } else {
        console.error(`${colors.red}Unknown command: ${command}${colors.reset}`);
        console.log(`Run 'node src/test-runner.js help' for usage information.`);
        process.exit(1);
      }
  }
}

// Export for use as module
module.exports = {
  testSuites,
  runTestSuite,
  runAllTests,
  runCoverageReport
};

// Run if called directly
if (require.main === module) {
  main();
}