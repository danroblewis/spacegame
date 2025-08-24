import { render } from '@testing-library/react';

// Import all components to catch syntax errors
import Crew from './Crew';
import Dashboard from './Dashboard';
import Factions from './Factions';
import Fleet from './Fleet';
import Intelligence from './Intelligence';
import Map from './Map';
import ResourceManagement from './ResourceManagement';
import ScanResults from './ScanResults';
import ShipActionsSidebar from './ShipActionsSidebar';
import ShipModifications from './ShipModifications';
import Systems from './Systems';

describe('Component Syntax Tests', () => {
  // This test suite ensures all components can be imported without syntax errors
  
  test('all components can be imported without syntax errors', () => {
    // If any component has syntax errors, this test will fail during import
    expect(Crew).toBeDefined();
    expect(Dashboard).toBeDefined();
    expect(Factions).toBeDefined();
    expect(Fleet).toBeDefined();
    expect(Intelligence).toBeDefined();
    expect(Map).toBeDefined();
    expect(ResourceManagement).toBeDefined();
    expect(ScanResults).toBeDefined();
    expect(ShipActionsSidebar).toBeDefined();
    expect(ShipModifications).toBeDefined();
    expect(Systems).toBeDefined();
  });

  test('components with minimal props can render without crashing', () => {
    // Mock minimal props for components that require them
    const mockProps = {
      selectedShip: null,
      onShipSelect: jest.fn(),
      onPerformAction: jest.fn(),
      ships: [],
      resources: { credits: 0, fuel: 0 },
      systems: [],
      factions: [],
      crew: [],
      currentSystem: null,
      onSystemSelect: jest.fn(),
      onFactionSelect: jest.fn(),
      onCrewSelect: jest.fn(),
      selectedSystem: null,
      selectedFaction: null,
      selectedCrew: null
    };

    // Test components that can render with null/empty props
    expect(() => render(<Dashboard {...mockProps} />)).not.toThrow();
    expect(() => render(<Fleet {...mockProps} />)).not.toThrow();
    expect(() => render(<ResourceManagement {...mockProps} />)).not.toThrow();
    expect(() => render(<Systems {...mockProps} />)).not.toThrow();
    expect(() => render(<Factions {...mockProps} />)).not.toThrow();
    expect(() => render(<Crew {...mockProps} />)).not.toThrow();
    expect(() => render(<Intelligence {...mockProps} />)).not.toThrow();
    expect(() => render(<Map {...mockProps} />)).not.toThrow();
    expect(() => render(<ScanResults {...mockProps} />)).not.toThrow();
    expect(() => render(<ShipModifications {...mockProps} />)).not.toThrow();
    expect(() => render(<ShipActionsSidebar {...mockProps} />)).not.toThrow();
  });
});