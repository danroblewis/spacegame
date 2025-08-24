import React from 'react';
import { render, screen, waitFor, fireEvent } from '../../test-utils';
import { setupDefaultMocks, mockAxios, mockShips } from '../../test-utils';
import Fleet from '../Fleet';

// Mock the child components that might cause issues in testing
jest.mock('../Map', () => {
  return function MockMap({ ships, selectedShip, onShipSelect }) {
    return (
      <div data-testid="mock-map">
        <div>Map Component</div>
        {ships?.map(ship => (
          <button 
            key={ship.symbol} 
            onClick={() => onShipSelect(ship)}
            data-testid={`map-ship-${ship.symbol}`}
          >
            {ship.symbol}
          </button>
        ))}
        {selectedShip && <div data-testid="selected-ship">{selectedShip.symbol}</div>}
      </div>
    );
  };
});

jest.mock('../ShipModifications', () => {
  return function MockShipModifications({ ship, onClose, onUpdate }) {
    return (
      <div data-testid="mock-ship-modifications">
        <div>Ship Modifications for {ship?.symbol}</div>
        <button onClick={onClose}>Close</button>
        <button onClick={() => onUpdate(ship)}>Update Ship</button>
      </div>
    );
  };
});

jest.mock('../ShipActionsSidebar', () => {
  return function MockShipActionsSidebar({ selectedShip, onShipUpdate }) {
    return (
      <div data-testid="mock-ship-actions-sidebar">
        <div>Ship Actions</div>
        {selectedShip && <div>Actions for {selectedShip.symbol}</div>}
        <button onClick={() => onShipUpdate(selectedShip)}>Update Ship</button>
      </div>
    );
  };
});

describe('Fleet Component', () => {
  const mockProps = {
    selectedShip: null,
    onShipSelect: jest.fn(),
    onShipUpdate: jest.fn()
  };

  beforeEach(() => {
    setupDefaultMocks();
    jest.clearAllMocks();
  });

  afterEach(() => {
    mockAxios.reset();
  });

  it('renders loading state initially', () => {
    render(<Fleet {...mockProps} />);
    expect(screen.getByText('Loading ships...')).toBeInTheDocument();
  });

  it('renders fleet with ships data', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Check if fleet section is rendered
    expect(screen.getByText('Fleet Management')).toBeInTheDocument();
    
    // Check if ships are displayed
    expect(screen.getByText(mockShips[0].symbol)).toBeInTheDocument();
    expect(screen.getByText(mockShips[1].symbol)).toBeInTheDocument();
    
    // Check if map is rendered
    expect(screen.getByTestId('mock-map')).toBeInTheDocument();
  });

  it('auto-selects first ship when none is selected', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Should call onShipSelect with first ship
    expect(mockProps.onShipSelect).toHaveBeenCalledWith(mockShips[0]);
  });

  it('does not auto-select if ship already selected', async () => {
    const propsWithSelected = {
      ...mockProps,
      selectedShip: mockShips[1]
    };

    render(<Fleet {...propsWithSelected} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Should not call onShipSelect since ship is already selected
    expect(mockProps.onShipSelect).not.toHaveBeenCalled();
  });

  it('handles ship selection from UI', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Click on a ship in the list
    const shipButton = screen.getByText(mockShips[1].symbol);
    fireEvent.click(shipButton);

    expect(mockProps.onShipSelect).toHaveBeenCalledWith(mockShips[1]);
  });

  it('displays ship status colors correctly', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Check for status indicators
    const inOrbitShip = screen.getByText('IN_ORBIT').closest('.ship-status');
    expect(inOrbitShip).toHaveClass('active');

    const inTransitShip = screen.getByText('IN_TRANSIT').closest('.ship-status');
    expect(inTransitShip).toHaveClass('active');
  });

  it('displays ship details correctly', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Check ship registration names
    expect(screen.getByText(mockShips[0].registration.name)).toBeInTheDocument();
    expect(screen.getByText(mockShips[1].registration.name)).toBeInTheDocument();

    // Check ship locations
    expect(screen.getByText(mockShips[0].nav.waypointSymbol)).toBeInTheDocument();
    expect(screen.getByText(mockShips[1].nav.waypointSymbol)).toBeInTheDocument();

    // Check cargo information
    expect(screen.getByText(`${mockShips[0].cargo.units}/${mockShips[0].cargo.capacity}`)).toBeInTheDocument();
    expect(screen.getByText(`${mockShips[1].cargo.units}/${mockShips[1].cargo.capacity}`)).toBeInTheDocument();
  });

  it('handles ship modifications toggle', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Click modify button for first ship
    const modifyButton = screen.getAllByText('Modify')[0];
    fireEvent.click(modifyButton);

    // Should show ship modifications component
    expect(screen.getByTestId('mock-ship-modifications')).toBeInTheDocument();
    expect(screen.getByText(`Ship Modifications for ${mockShips[0].symbol}`)).toBeInTheDocument();
  });

  it('closes ship modifications when requested', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Open modifications
    const modifyButton = screen.getAllByText('Modify')[0];
    fireEvent.click(modifyButton);

    expect(screen.getByTestId('mock-ship-modifications')).toBeInTheDocument();

    // Close modifications
    const closeButton = screen.getByText('Close');
    fireEvent.click(closeButton);

    expect(screen.queryByTestId('mock-ship-modifications')).not.toBeInTheDocument();
  });

  it('handles ship updates correctly', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Trigger ship update from sidebar
    const updateButton = screen.getByText('Update Ship');
    fireEvent.click(updateButton);

    expect(mockProps.onShipUpdate).toHaveBeenCalledWith(mockShips[0]);
  });

  it('fetches security status for all ships', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Wait for security status calls to be made
    await waitFor(() => {
      const securityCalls = mockAxios.history.get.filter(call => 
        call.url.includes('/security/status')
      );
      expect(securityCalls).toHaveLength(mockShips.length);
    });
  });

  it('handles API error gracefully', async () => {
    mockAxios.onGet('/api/ships').reply(500, { detail: 'Server error' });

    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Error: Server error')).toBeInTheDocument();
    });
  });

  it('handles network error gracefully', async () => {
    mockAxios.onGet('/api/ships').networkError();

    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });

  it('handles empty ships list', async () => {
    mockAxios.onGet('/api/ships').reply(200, []);

    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Should show no ships message
    expect(screen.getByText('No ships found')).toBeInTheDocument();
    expect(mockProps.onShipSelect).not.toHaveBeenCalled();
  });

  it('handles ship navigation actions', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Test dock action
    const dockButton = screen.getAllByText('Dock')[0];
    fireEvent.click(dockButton);

    await waitFor(() => {
      expect(mockAxios.history.post.some(call => 
        call.url.includes('/dock')
      )).toBe(true);
    });

    // Test orbit action
    const orbitButton = screen.getAllByText('Orbit')[0];
    fireEvent.click(orbitButton);

    await waitFor(() => {
      expect(mockAxios.history.post.some(call => 
        call.url.includes('/orbit')
      )).toBe(true);
    });
  });

  it('displays success messages for actions', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Trigger an action that should show a success message
    const dockButton = screen.getAllByText('Dock')[0];
    fireEvent.click(dockButton);

    await waitFor(() => {
      expect(screen.getByText(/successfully/i)).toBeInTheDocument();
    });
  });

  it('auto-hides messages after timeout', async () => {
    jest.useFakeTimers();
    
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Trigger an action that shows a message
    const dockButton = screen.getAllByText('Dock')[0];
    fireEvent.click(dockButton);

    await waitFor(() => {
      expect(screen.getByText(/successfully/i)).toBeInTheDocument();
    });

    // Fast-forward time
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(screen.queryByText(/successfully/i)).not.toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  it('handles ship with missing data gracefully', async () => {
    const shipsWithMissingData = [
      { ...mockShips[0], nav: null, cargo: null },
      { ...mockShips[1], registration: null }
    ];
    mockAxios.onGet('/api/ships').reply(200, shipsWithMissingData);

    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Should handle missing data gracefully
    expect(screen.getByText('Unknown')).toBeInTheDocument();
    expect(screen.getByText('N/A')).toBeInTheDocument();
  });

  it('updates ships list when ship is modified', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships...')).not.toBeInTheDocument();
    });

    // Open modifications and update ship
    const modifyButton = screen.getAllByText('Modify')[0];
    fireEvent.click(modifyButton);

    const updateButton = screen.getByText('Update Ship');
    fireEvent.click(updateButton);

    // Should update the ship in the list and call parent update
    expect(mockProps.onShipUpdate).toHaveBeenCalled();
  });

  it('integrates with map component correctly', async () => {
    render(<Fleet {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading ships..')).not.toBeInTheDocument();
    });

    // Should pass ships to map
    expect(screen.getByTestId(`map-ship-${mockShips[0].symbol}`)).toBeInTheDocument();
    expect(screen.getByTestId(`map-ship-${mockShips[1].symbol}`)).toBeInTheDocument();

    // Test ship selection from map
    const mapShipButton = screen.getByTestId(`map-ship-${mockShips[1].symbol}`);
    fireEvent.click(mapShipButton);

    expect(mockProps.onShipSelect).toHaveBeenCalledWith(mockShips[1]);
  });
});