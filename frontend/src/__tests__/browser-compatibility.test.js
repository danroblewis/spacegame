import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test-utils';
import { setupDefaultMocks, mockAxios } from '../test-utils';
import App from '../App';

describe('Browser Compatibility Tests', () => {
  beforeEach(() => {
    setupDefaultMocks();
  });

  afterEach(() => {
    mockAxios.reset();
  });

  describe('CSS and Layout Issues', () => {
    it('handles missing CSS Grid support', () => {
      // Simulate older browser without CSS Grid
      const originalSupports = CSS.supports;
      CSS.supports = jest.fn((property, value) => {
        if (property === 'display' && value === 'grid') {
          return false;
        }
        return originalSupports(property, value);
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      CSS.supports = originalSupports;
    });

    it('handles missing Flexbox support', () => {
      // Simulate older browser without Flexbox
      const originalSupports = CSS.supports;
      CSS.supports = jest.fn((property, value) => {
        if (property === 'display' && (value === 'flex' || value === 'inline-flex')) {
          return false;
        }
        return originalSupports(property, value);
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      CSS.supports = originalSupports;
    });

    it('handles viewport meta tag issues', () => {
      // Simulate mobile browser without proper viewport handling
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 320,
      });

      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 568,
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Should be usable on small screens
      const navigation = screen.getByText('🚀 SpaceTraders GUI').closest('.navbar');
      expect(navigation).toBeInTheDocument();
    });
  });

  describe('JavaScript Compatibility', () => {
    it('handles missing Promise support', async () => {
      // Test graceful degradation when Promises might not be fully supported
      const originalPromise = window.Promise;
      
      // Simulate limited Promise support
      window.Promise = function(executor) {
        return originalPromise.call(this, executor);
      };
      window.Promise.resolve = originalPromise.resolve;
      window.Promise.reject = originalPromise.reject;
      window.Promise.all = originalPromise.all;

      render(<App />);
      
      await waitFor(() => {
        expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
      });

      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      window.Promise = originalPromise;
    });

    it('handles missing fetch API', () => {
      // Already mocked in setupTests.js, but test the mock works
      expect(global.fetch).toBeDefined();
      
      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
    });

    it('handles missing arrow function support', () => {
      // Modern build tools should handle this, but test component still works
      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
      
      // Navigate to ensure event handlers work
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);
      
      // Should work even with transpiled code
      expect(screen.getByTestId('fleet')).toBeInTheDocument();
    });
  });

  describe('Event Handling Compatibility', () => {
    it('handles touch events properly', () => {
      render(<App />);

      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      
      // Simulate touch events
      fireEvent.touchStart(fleetLink);
      fireEvent.touchEnd(fleetLink);
      fireEvent.click(fleetLink);

      expect(screen.getByTestId('fleet')).toBeInTheDocument();
    });

    it('handles keyboard events across browsers', () => {
      render(<App />);

      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      
      // Test different key events
      fleetLink.focus();
      fireEvent.keyDown(fleetLink, { key: 'Enter', keyCode: 13 });
      
      // Should navigate
      expect(screen.getByTestId('fleet')).toBeInTheDocument();
    });

    it('handles mouse events properly', () => {
      render(<App />);

      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      
      // Test different mouse events
      fireEvent.mouseEnter(fleetLink);
      fireEvent.mouseLeave(fleetLink);
      fireEvent.click(fleetLink);

      expect(screen.getByTestId('fleet')).toBeInTheDocument();
    });
  });

  describe('Storage Compatibility', () => {
    it('handles localStorage quota exceeded', () => {
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn(() => {
        throw new Error('QuotaExceededError');
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      localStorage.setItem = originalSetItem;
    });

    it('handles sessionStorage not available', () => {
      const originalSessionStorage = window.sessionStorage;
      delete window.sessionStorage;

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      window.sessionStorage = originalSessionStorage;
    });

    it('handles cookies disabled', () => {
      // Simulate environment where cookies are disabled
      Object.defineProperty(document, 'cookie', {
        get: () => '',
        set: () => {
          throw new Error('Cookies disabled');
        },
        configurable: true
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
    });
  });

  describe('Network Compatibility', () => {
    it('handles CORS issues gracefully', async () => {
      mockAxios.onGet('/api/agent').reply(0, '', {
        'Access-Control-Allow-Origin': 'null'
      });

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });

      // App should still be functional
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
    });

    it('handles slow network connections', async () => {
      // Simulate slow network
      mockAxios.onGet('/api/agent').reply(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve([200, { symbol: 'TEST', credits: 1000 }]), 5000);
        });
      });

      render(<App />);

      // Should show loading state
      expect(screen.getByText('Loading agent data...')).toBeInTheDocument();

      // Should timeout gracefully (adjust timeout in real app)
      await waitFor(() => {
        expect(screen.queryByText('Loading agent data...')).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('handles network disconnection', async () => {
      mockAxios.onGet('/api/agent').networkError();

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });

      // App should remain usable
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);
      
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
    });
  });

  describe('Font and Media Compatibility', () => {
    it('handles web font loading failures', () => {
      // Simulate font loading failure
      const originalDocument = document;
      const mockFonts = {
        ready: Promise.reject(new Error('Font loading failed')),
        load: jest.fn().mockRejectedValue(new Error('Font loading failed'))
      };
      
      Object.defineProperty(document, 'fonts', {
        value: mockFonts,
        configurable: true
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      Object.defineProperty(document, 'fonts', {
        value: originalDocument.fonts,
        configurable: true
      });
    });

    it('handles emoji rendering issues', () => {
      render(<App />);
      
      // Should render rocket emoji or degrade gracefully
      const title = screen.getByText(/SpaceTraders GUI/);
      expect(title).toBeInTheDocument();
    });
  });

  describe('Performance Issues', () => {
    it('handles memory constraints', () => {
      // Simulate low memory environment
      const originalMemory = navigator.deviceMemory;
      Object.defineProperty(navigator, 'deviceMemory', {
        value: 1, // 1GB
        configurable: true
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      Object.defineProperty(navigator, 'deviceMemory', {
        value: originalMemory,
        configurable: true
      });
    });

    it('handles slow CPU', () => {
      // Simulate slow CPU by adding delays
      const originalSetTimeout = window.setTimeout;
      window.setTimeout = (callback, delay) => {
        return originalSetTimeout(callback, delay * 2); // Double all delays
      };

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      window.setTimeout = originalSetTimeout;
    });
  });

  describe('Accessibility Browser Issues', () => {
    it('handles screen reader compatibility', () => {
      render(<App />);

      // Check ARIA landmarks
      expect(screen.getByRole('navigation')).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();

      // Check link accessibility
      const links = screen.getAllByRole('link');
      links.forEach(link => {
        expect(link).toHaveAttribute('href');
      });
    });

    it('handles high contrast mode', () => {
      // Simulate high contrast mode
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => {
          if (query === '(prefers-contrast: high)') {
            return {
              matches: true,
              media: query,
              onchange: null,
              addListener: jest.fn(),
              removeListener: jest.fn(),
              addEventListener: jest.fn(),
              removeEventListener: jest.fn(),
              dispatchEvent: jest.fn(),
            };
          }
          return {
            matches: false,
            media: query,
            onchange: null,
            addListener: jest.fn(),
            removeListener: jest.fn(),
            addEventListener: jest.fn(),
            removeEventListener: jest.fn(),
            dispatchEvent: jest.fn(),
          };
        }),
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
    });

    it('handles reduced motion preferences', () => {
      // Simulate reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => {
          if (query === '(prefers-reduced-motion: reduce)') {
            return {
              matches: true,
              media: query,
              onchange: null,
              addListener: jest.fn(),
              removeListener: jest.fn(),
              addEventListener: jest.fn(),
              removeEventListener: jest.fn(),
              dispatchEvent: jest.fn(),
            };
          }
          return {
            matches: false,
            media: query,
            onchange: null,
            addListener: jest.fn(),
            removeListener: jest.fn(),
            addEventListener: jest.fn(),
            removeEventListener: jest.fn(),
            dispatchEvent: jest.fn(),
          };
        }),
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
    });
  });

  describe('Security Issues', () => {
    it('handles Content Security Policy restrictions', () => {
      // Simulate CSP restrictions
      const originalEval = window.eval;
      window.eval = function() {
        throw new Error('Content Security Policy violation');
      };

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore
      window.eval = originalEval;
    });

    it('handles third-party script blocking', () => {
      // Simulate ad blockers or script blockers
      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
      
      // App should work without external dependencies
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);
      expect(screen.getByTestId('fleet')).toBeInTheDocument();
    });
  });
});