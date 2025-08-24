import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test-utils';
import { setupDefaultMocks, mockAxios, mockShips, mockAgent } from '../test-utils';
import App from '../App';

describe('Integration Tests', () => {
  beforeEach(() => {
    setupDefaultMocks();
  });

  afterEach(() => {
    mockAxios.reset();
  });

  describe('Full Application Workflow', () => {
    it('completes a full user journey from dashboard to fleet management', async () => {
      render(<App />);

      // 1. Start at dashboard and verify it loads
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
      });

      // Should see agent information
      expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();
      expect(screen.getByText(mockAgent.credits.toLocaleString())).toBeInTheDocument();

      // 2. Navigate to Fleet
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Should see fleet data
      expect(screen.getByText('Fleet Management')).toBeInTheDocument();
      expect(screen.getByText(mockShips[0].symbol)).toBeInTheDocument();

      // 3. Select a ship
      const firstShip = screen.getByText(mockShips[0].symbol);
      fireEvent.click(firstShip);

      // Should see ship details in sidebar
      await waitFor(() => {
        expect(screen.getByText('Ship Actions')).toBeInTheDocument();
      });

      // 4. Perform ship action (dock)
      const dockButton = screen.getByText('Dock');
      fireEvent.click(dockButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/dock')
        )).toBe(true);
      });

      // 5. Navigate to different sections while maintaining ship selection
      const intelligenceLink = screen.getByRole('link', { name: 'Intelligence' });
      fireEvent.click(intelligenceLink);

      // Ship should still be selected in sidebar
      expect(screen.getByText('Ship Actions')).toBeInTheDocument();

      // 6. Return to dashboard
      const dashboardLink = screen.getByRole('link', { name: 'Dashboard' });
      fireEvent.click(dashboardLink);

      // Should still show updated data
      expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();
    });

    it('handles ship modification workflow', async () => {
      render(<App />, { route: '/fleet' });

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Select a ship
      const firstShip = screen.getByText(mockShips[0].symbol);
      fireEvent.click(firstShip);

      // Open modifications
      const modifyButton = screen.getByText('Modify');
      fireEvent.click(modifyButton);

      // Should show modifications interface
      expect(screen.getByText(`Ship Modifications for ${mockShips[0].symbol}`)).toBeInTheDocument();

      // Make modification
      const upgradeButton = screen.getByText('Upgrade Reactor');
      fireEvent.click(upgradeButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/install')
        )).toBe(true);
      });

      // Close modifications
      const closeButton = screen.getByText('Close');
      fireEvent.click(closeButton);

      // Should return to fleet view with updated ship
      expect(screen.getByText('Fleet Management')).toBeInTheDocument();
    });

    it('handles resource management workflow', async () => {
      render(<App />, { route: '/resources' });

      // Should load resource management
      expect(screen.getByText('Resource Management')).toBeInTheDocument();

      // Select a ship for resource management
      const shipSelect = screen.getByRole('combobox', { name: /select ship/i });
      fireEvent.change(shipSelect, { target: { value: mockShips[0].symbol } });

      await waitFor(() => {
        expect(mockAxios.history.get.some(call => 
          call.url.includes('/resources')
        )).toBe(true);
      });

      // Should show resource data
      expect(screen.getByText('Fuel Management')).toBeInTheDocument();
      expect(screen.getByText('Power Distribution')).toBeInTheDocument();

      // Perform resource action
      const optimizeButton = screen.getByText('Optimize Fuel');
      fireEvent.click(optimizeButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/resources/optimize-fuel')
        )).toBe(true);
      });

      // Should show success message
      expect(screen.getByText(/optimization/i)).toBeInTheDocument();
    });

    it('handles intelligence and scanning workflow', async () => {
      render(<App />, { route: '/intelligence' });

      // Should load intelligence
      expect(screen.getByText('Intelligence')).toBeInTheDocument();

      // Select a ship for scanning
      const shipSelect = screen.getByRole('combobox', { name: /select ship/i });
      fireEvent.change(shipSelect, { target: { value: mockShips[0].symbol } });

      // Perform system scan
      const scanSystemsButton = screen.getByText('Scan Systems');
      fireEvent.click(scanSystemsButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/scan/systems')
        )).toBe(true);
      });

      // Should show scan results
      expect(screen.getByText('Scan Results')).toBeInTheDocument();

      // Perform waypoint scan
      const scanWaypointsButton = screen.getByText('Scan Waypoints');
      fireEvent.click(scanWaypointsButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/scan/waypoints')
        )).toBe(true);
      });

      // Should show additional scan data
      expect(screen.getByText(/waypoint/i)).toBeInTheDocument();
    });

    it('handles crew management workflow', async () => {
      render(<App />, { route: '/crew' });

      // Should load crew management
      expect(screen.getByText('Crew Management')).toBeInTheDocument();

      // Select a ship
      const shipSelect = screen.getByRole('combobox', { name: /select ship/i });
      fireEvent.change(shipSelect, { target: { value: mockShips[0].symbol } });

      await waitFor(() => {
        expect(mockAxios.history.get.some(call => 
          call.url.includes('/crew')
        )).toBe(true);
      });

      // Should show crew data
      expect(screen.getByText('Current Crew')).toBeInTheDocument();

      // Hire new crew
      const hireButton = screen.getByText('Hire Crew');
      fireEvent.click(hireButton);

      // Should show available crew
      expect(screen.getByText('Available Crew')).toBeInTheDocument();

      // Select crew member to hire
      const crewMember = screen.getByText('Marcus Thompson');
      fireEvent.click(crewMember);

      const confirmHireButton = screen.getByText('Confirm Hire');
      fireEvent.click(confirmHireButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/crew/hire')
        )).toBe(true);
      });

      // Should show success message
      expect(screen.getByText(/hired/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling Integration', () => {
    it('handles API failures gracefully across the application', async () => {
      // Simulate API failures
      mockAxios.onGet('/api/agent').reply(500, { detail: 'Agent service down' });
      mockAxios.onGet('/api/ships').reply(500, { detail: 'Fleet service down' });

      render(<App />);

      // Should show error on dashboard
      await waitFor(() => {
        expect(screen.getByText('Error: Agent service down')).toBeInTheDocument();
      });

      // Navigate to fleet
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);

      // Should show error on fleet
      await waitFor(() => {
        expect(screen.getByText('Error: Fleet service down')).toBeInTheDocument();
      });

      // App should still be functional
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Dashboard' })).toBeInTheDocument();
    });

    it('handles network interruptions during ship actions', async () => {
      render(<App />, { route: '/fleet' });

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Select a ship
      const firstShip = screen.getByText(mockShips[0].symbol);
      fireEvent.click(firstShip);

      // Simulate network error during action
      mockAxios.onPost(/\/api\/ships\/.*\/dock/).networkError();

      const dockButton = screen.getByText('Dock');
      fireEvent.click(dockButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });

      // App should remain functional
      expect(screen.getByText('Fleet Management')).toBeInTheDocument();
    });

    it('handles partial data loading failures', async () => {
      // Agent loads successfully, ships fail
      mockAxios.onGet('/api/agent').reply(200, mockAgent);
      mockAxios.onGet('/api/ships').reply(500, { detail: 'Ships unavailable' });

      render(<App />);

      await waitFor(() => {
        expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
      });

      // Should show agent data
      expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();

      // Navigate to fleet should show error
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);

      await waitFor(() => {
        expect(screen.getByText('Error: Ships unavailable')).toBeInTheDocument();
      });
    });
  });

  describe('Performance and Loading States', () => {
    it('handles slow API responses properly', async () => {
      // Simulate slow responses
      mockAxios.onGet('/api/agent').reply(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve([200, mockAgent]), 1000);
        });
      });

      mockAxios.onGet('/api/ships').reply(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve([200, mockShips]), 1500);
        });
      });

      render(<App />);

      // Should show loading state
      expect(screen.getByText('Loading agent data...')).toBeInTheDocument();

      // Wait for agent to load
      await waitFor(() => {
        expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();
      }, { timeout: 2000 });

      // Navigate to fleet
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);

      // Should show loading for fleet
      expect(screen.getByText('Loading ships...')).toBeInTheDocument();

      // Wait for ships to load
      await waitFor(() => {
        expect(screen.getByText(mockShips[0].symbol)).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('handles concurrent API calls efficiently', async () => {
      render(<App />, { route: '/fleet' });

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Select ship (triggers multiple API calls)
      const firstShip = screen.getByText(mockShips[0].symbol);
      fireEvent.click(firstShip);

      // Should handle all concurrent calls
      await waitFor(() => {
        const apiCalls = mockAxios.history.get.length + mockAxios.history.post.length;
        expect(apiCalls).toBeGreaterThan(1);
      });

      // App should remain responsive
      expect(screen.getByText('Fleet Management')).toBeInTheDocument();
    });
  });

  describe('State Management Integration', () => {
    it('maintains state consistency across components', async () => {
      render(<App />, { route: '/fleet' });

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Select ship in fleet
      const firstShip = screen.getByText(mockShips[0].symbol);
      fireEvent.click(firstShip);

      // Ship should be reflected in sidebar
      expect(screen.getByText('Ship Actions')).toBeInTheDocument();

      // Navigate to different page
      const resourcesLink = screen.getByRole('link', { name: 'Resources' });
      fireEvent.click(resourcesLink);

      // Ship should still be selected
      expect(screen.getByText('Ship Actions')).toBeInTheDocument();

      // Update ship from resources page
      const shipSelect = screen.getByRole('combobox', { name: /select ship/i });
      fireEvent.change(shipSelect, { target: { value: mockShips[1].symbol } });

      // Should update sidebar
      // Note: This depends on implementation, adjust based on actual behavior
    });

    it('handles ship updates propagation correctly', async () => {
      render(<App />, { route: '/fleet' });

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Select ship
      const firstShip = screen.getByText(mockShips[0].symbol);
      fireEvent.click(firstShip);

      // Perform action that updates ship
      const dockButton = screen.getByText('Dock');
      fireEvent.click(dockButton);

      await waitFor(() => {
        expect(mockAxios.history.post.some(call => 
          call.url.includes('/dock')
        )).toBe(true);
      });

      // Ship status should be updated everywhere
      // This tests the state propagation mechanism
      expect(screen.getByText('DOCKED')).toBeInTheDocument();
    });
  });

  describe('Accessibility Integration', () => {
    it('maintains accessibility during navigation', async () => {
      render(<App />);

      // Check initial accessibility
      expect(screen.getByRole('navigation')).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();

      // Navigate and check accessibility is maintained
      const fleetLink = screen.getByRole('link', { name: 'Fleet' });
      fireEvent.click(fleetLink);

      await waitFor(() => {
        expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
      });

      // Should still have proper landmarks
      expect(screen.getByRole('navigation')).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();

      // Links should be accessible
      const links = screen.getAllByRole('link');
      links.forEach(link => {
        expect(link).toHaveAttribute('href');
      });
    });

    it('handles keyboard navigation properly', async () => {
      render(<App />);

      // Tab through navigation
      const firstLink = screen.getByRole('link', { name: 'Dashboard' });
      firstLink.focus();
      expect(document.activeElement).toBe(firstLink);

      // Use Enter to navigate
      fireEvent.keyPress(firstLink, { key: 'Enter', code: 'Enter' });
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    });
  });

  describe('Browser Compatibility', () => {
    it('works with different user agents', () => {
      // Simulate different browsers
      const originalUserAgent = navigator.userAgent;

      // Chrome
      Object.defineProperty(navigator, 'userAgent', {
        value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        configurable: true
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Firefox
      Object.defineProperty(navigator, 'userAgent', {
        value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        configurable: true
      });

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore original
      Object.defineProperty(navigator, 'userAgent', {
        value: originalUserAgent,
        configurable: true
      });
    });

    it('handles localStorage availability', () => {
      // Simulate localStorage unavailable
      const originalLocalStorage = window.localStorage;
      delete window.localStorage;

      render(<App />);
      expect(screen.getByText('🚀 SpaceTraders GUI')).toBeInTheDocument();

      // Restore localStorage
      window.localStorage = originalLocalStorage;
    });
  });
});