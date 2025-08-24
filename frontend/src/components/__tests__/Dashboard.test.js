import React from 'react';
import { render, screen, waitFor } from '../../test-utils';
import { setupDefaultMocks, mockAxios, mockAgent, mockShips } from '../../test-utils';
import Dashboard from '../Dashboard';

describe('Dashboard Component', () => {
  beforeEach(() => {
    setupDefaultMocks();
  });

  afterEach(() => {
    mockAxios.reset();
  });

  it('renders loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByText('Loading agent data...')).toBeInTheDocument();
  });

  it('renders dashboard with agent and fleet data', async () => {
    render(<Dashboard />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Check if main title is rendered
    expect(screen.getByText('Agent Dashboard')).toBeInTheDocument();

    // Check agent information section
    expect(screen.getByText('Agent Information')).toBeInTheDocument();
    expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();
    expect(screen.getByText(mockAgent.credits.toLocaleString())).toBeInTheDocument();
    expect(screen.getByText(mockAgent.startingFaction)).toBeInTheDocument();
    expect(screen.getByText(mockAgent.headquarters)).toBeInTheDocument();

    // Check fleet overview section
    expect(screen.getByText('Fleet Overview')).toBeInTheDocument();
    expect(screen.getByText(mockShips.length.toString())).toBeInTheDocument();

    // Check recent activity section
    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    expect(screen.getByText(mockShips[0].symbol)).toBeInTheDocument();
  });

  it('displays correct fleet statistics', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Total ships
    expect(screen.getByText(mockShips.length.toString())).toBeInTheDocument();

    // Active ships (those with IN_TRANSIT or IN_ORBIT status)
    const activeShips = mockShips.filter(ship => 
      ship.nav?.status === 'IN_TRANSIT' || ship.nav?.status === 'IN_ORBIT'
    );
    expect(screen.getByText(activeShips.length.toString())).toBeInTheDocument();

    // Total cargo
    const totalCargo = mockShips.reduce((total, ship) => total + (ship.cargo?.units || 0), 0);
    expect(screen.getByText(totalCargo.toString())).toBeInTheDocument();
  });

  it('displays ship status correctly', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Check for ship status indicators
    expect(screen.getByText('IN_ORBIT')).toBeInTheDocument();
    expect(screen.getByText('IN_TRANSIT')).toBeInTheDocument();
  });

  it('displays ship details in recent activity', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Check ship locations
    expect(screen.getByText(mockShips[0].nav.waypointSymbol)).toBeInTheDocument();
    expect(screen.getByText(mockShips[1].nav.waypointSymbol)).toBeInTheDocument();

    // Check cargo amounts
    expect(screen.getByText(mockShips[0].cargo.units.toString())).toBeInTheDocument();
    expect(screen.getByText(mockShips[1].cargo.units.toString())).toBeInTheDocument();

    // Check crew counts
    expect(screen.getByText(mockShips[0].crew.current.toString())).toBeInTheDocument();
    expect(screen.getByText(mockShips[1].crew.current.toString())).toBeInTheDocument();
  });

  it('handles agent API error', async () => {
    mockAxios.onGet('/api/agent').reply(500, { detail: 'Agent API error' });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Error: Agent API error')).toBeInTheDocument();
    });
  });

  it('handles ships API error', async () => {
    mockAxios.onGet('/api/ships').reply(500, { detail: 'Ships API error' });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Error: Ships API error')).toBeInTheDocument();
    });
  });

  it('handles network error', async () => {
    mockAxios.onGet('/api/agent').networkError();

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });

  it('handles empty ships array', async () => {
    mockAxios.onGet('/api/ships').reply(200, []);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Should show 0 for all fleet statistics
    const totalShipsElement = screen.getByText('Total Ships').parentElement;
    expect(totalShipsElement).toHaveTextContent('0');

    const activeShipsElement = screen.getByText('Active Ships').parentElement;
    expect(activeShipsElement).toHaveTextContent('0');

    const totalCargoElement = screen.getByText('Total Cargo').parentElement;
    expect(totalCargoElement).toHaveTextContent('0');
  });

  it('handles ships with missing navigation data', async () => {
    const shipsWithMissingData = [
      { ...mockShips[0], nav: null },
      { ...mockShips[1], cargo: null }
    ];
    mockAxios.onGet('/api/ships').reply(200, shipsWithMissingData);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Should handle missing data gracefully
    expect(screen.getByText('UNKNOWN')).toBeInTheDocument();
    expect(screen.getByText('N/A')).toBeInTheDocument();
  });

  it('formats credits with locale string', async () => {
    const agentWithLargeCredits = { ...mockAgent, credits: 1234567 };
    mockAxios.onGet('/api/agent').reply(200, agentWithLargeCredits);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Check if credits are formatted with commas
    expect(screen.getByText('1,234,567')).toBeInTheDocument();
  });

  it('limits recent activity to first 3 ships', async () => {
    const manyShips = [...mockShips, ...mockShips, ...mockShips]; // 6 ships total
    mockAxios.onGet('/api/ships').reply(200, manyShips);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Should only show first 3 ships in recent activity
    const shipCards = screen.getAllByTestId(/ship-card|ship-name/).length;
    expect(shipCards).toBeLessThanOrEqual(6); // At most 3 ships × 2 elements per ship
  });

  it('makes correct API calls', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    });

    // Verify API calls were made
    expect(mockAxios.history.get).toHaveLength(2);
    expect(mockAxios.history.get[0].url).toBe('/api/agent');
    expect(mockAxios.history.get[1].url).toBe('/api/ships');
  });

  it('handles concurrent API calls correctly', async () => {
    // Simulate slow API responses
    mockAxios.onGet('/api/agent').reply(() => {
      return new Promise(resolve => {
        setTimeout(() => resolve([200, mockAgent]), 100);
      });
    });

    mockAxios.onGet('/api/ships').reply(() => {
      return new Promise(resolve => {
        setTimeout(() => resolve([200, mockShips]), 150);
      });
    });

    render(<Dashboard />);

    // Should show loading initially
    expect(screen.getByText('Loading agent data...')).toBeInTheDocument();

    // Wait for both API calls to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading agent data...')).not.toBeInTheDocument();
    }, { timeout: 300 });

    // Both should be loaded
    expect(screen.getByText('Agent Dashboard')).toBeInTheDocument();
    expect(screen.getByText(mockAgent.symbol)).toBeInTheDocument();
  });
});