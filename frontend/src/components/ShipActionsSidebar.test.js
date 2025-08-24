import { render, screen } from '@testing-library/react';
import ShipActionsSidebar from './ShipActionsSidebar';

// Mock the required props
const mockProps = {
  selectedShip: {
    symbol: 'TEST-SHIP-1',
    nav: {
      status: 'IN_ORBIT',
      systemSymbol: 'TEST-SYSTEM',
      waypointSymbol: 'TEST-WAYPOINT'
    },
    fuel: {
      current: 100,
      capacity: 200
    },
    frame: {
      symbol: 'FRAME_FIGHTER'
    }
  },
  onShipSelect: jest.fn(),
  onPerformAction: jest.fn()
};

describe('ShipActionsSidebar', () => {
  test('renders without crashing', () => {
    // This test will catch JSX syntax errors
    expect(() => {
      render(<ShipActionsSidebar {...mockProps} />);
    }).not.toThrow();
  });

  test('displays ship information when ship is selected', () => {
    render(<ShipActionsSidebar {...mockProps} />);
    
    // Check if ship symbol is displayed
    expect(screen.getByText(/TEST-SHIP-1/)).toBeInTheDocument();
  });

  test('renders action sections', () => {
    render(<ShipActionsSidebar {...mockProps} />);
    
    // Check for main action sections
    expect(screen.getByText(/Navigation/)).toBeInTheDocument();
    expect(screen.getByText(/Combat/)).toBeInTheDocument();
  });

  test('handles no selected ship', () => {
    render(<ShipActionsSidebar {...mockProps} selectedShip={null} />);
    
    // Should render without errors even with no ship selected
    expect(screen.getByText(/Select a ship/)).toBeInTheDocument();
  });
});