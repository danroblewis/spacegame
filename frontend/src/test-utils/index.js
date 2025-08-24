import React from 'react';
import { render as rtlRender } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Create mock adapter for axios
export const mockAxios = new MockAdapter(axios);

// Custom render function that includes Router
function render(ui, { route = '/', ...options } = {}) {
  window.history.pushState({}, 'Test page', route);

  function Wrapper({ children }) {
    return <BrowserRouter>{children}</BrowserRouter>;
  }

  return rtlRender(ui, { wrapper: Wrapper, ...options });
}

// Mock data for testing
export const mockAgent = {
  symbol: "DEMO_AGENT",
  headquarters: "X1-DF55-20250X",
  credits: 1000000,
  startingFaction: "COSMIC"
};

export const mockShips = [
  {
    symbol: "DEMO_SHIP_1",
    registration: { name: "Explorer One", role: "EXPLORER" },
    nav: {
      status: "IN_ORBIT",
      waypointSymbol: "X1-DF55-20250X",
      systemSymbol: "X1-DF55",
      route: {
        destination: {
          symbol: "X1-DF55-20250X",
          type: "PLANET",
          systemSymbol: "X1-DF55",
          x: -42,
          y: -26
        },
        origin: {
          symbol: "X1-DF55-20250X",
          type: "PLANET",
          systemSymbol: "X1-DF55",
          x: -42,
          y: -26
        },
        departureTime: "2023-11-01T00:00:00.000Z",
        arrival: "2023-11-01T00:00:00.000Z"
      }
    },
    crew: { current: 2, capacity: 4 },
    frame: { name: "Explorer Frame", symbol: "FRAME_EXPLORER" },
    reactor: { name: "Basic Reactor", symbol: "REACTOR_FUSION_I", powerOutput: 15 },
    engine: { name: "Basic Engine", symbol: "ENGINE_ION_DRIVE_I", speed: 25 },
    modules: [
      { name: "Shield Generator I", symbol: "MODULE_SHIELD_GENERATOR_I", description: "Basic shield generator" },
      { name: "Cargo Hold I", symbol: "MODULE_CARGO_HOLD_I", description: "Basic cargo storage" }
    ],
    mounts: [
      { name: "Laser Cannon I", symbol: "MOUNT_LASER_CANNON_I", description: "Basic laser cannon" },
      { name: "Missile Launcher I", symbol: "MOUNT_MISSILE_LAUNCHER_I", description: "Basic missile launcher" }
    ],
    cargo: { units: 50, capacity: 100, inventory: [{ symbol: "FUEL", units: 50 }] }
  },
  {
    symbol: "DEMO_SHIP_2",
    registration: { name: "Cargo Runner", role: "HAULER" },
    nav: {
      status: "IN_TRANSIT",
      waypointSymbol: "X1-DF55-20250Y",
      systemSymbol: "X1-DF55",
      route: {
        destination: {
          symbol: "X1-DF55-20250Y",
          type: "ASTEROID_FIELD",
          systemSymbol: "X1-DF55",
          x: 18,
          y: -175
        }
      }
    },
    crew: { current: 1, capacity: 2 },
    frame: { name: "Hauler Frame", symbol: "FRAME_HAULER" },
    reactor: { name: "Basic Reactor", symbol: "REACTOR_FUSION_I", powerOutput: 15 },
    engine: { name: "Basic Engine", symbol: "ENGINE_ION_DRIVE_I", speed: 20 },
    modules: [
      { name: "Cargo Hold II", symbol: "MODULE_CARGO_HOLD_II", description: "Advanced cargo storage" }
    ],
    mounts: [],
    cargo: { units: 80, capacity: 200, inventory: [{ symbol: "IRON_ORE", units: 80 }] }
  }
];

export const mockSystems = [
  {
    symbol: "X1-DF55",
    sectorSymbol: "X1",
    type: "NEUTRON_STAR",
    x: 0,
    y: 0,
    waypoints: [
      { symbol: "X1-DF55-20250X", type: "PLANET", x: -42, y: -26 },
      { symbol: "X1-DF55-20250Y", type: "ASTEROID_FIELD", x: 18, y: -175 }
    ],
    factions: [{ symbol: "COSMIC" }]
  }
];

export const mockFactions = [
  {
    symbol: "COSMIC",
    name: "Cosmic Coalition",
    description: "A powerful coalition of space-faring civilizations",
    headquarters: "X1-DF55-20250X",
    isRecruiting: true,
    traits: [
      { name: "Bureaucratic", description: "Highly organized and bureaucratic" },
      { name: "Secretive", description: "Keeps information close to the chest" }
    ]
  }
];

export const mockWaypoints = [
  {
    symbol: "X1-DF55-20250X",
    type: "PLANET",
    systemSymbol: "X1-DF55",
    x: -42,
    y: -26,
    orbitals: [{ symbol: "X1-DF55-20250B" }],
    traits: [
      { symbol: "MARKETPLACE", name: "Marketplace", description: "A thriving marketplace where goods and services are traded." },
      { symbol: "SHIPYARD", name: "Shipyard", description: "A facility where ships are constructed, repaired, and outfitted." }
    ],
    faction: { symbol: "COSMIC" }
  }
];

// Setup default API mocks
export const setupDefaultMocks = () => {
  mockAxios.reset();
  
  // Mock agent endpoint
  mockAxios.onGet('/api/agent').reply(200, mockAgent);
  
  // Mock ships endpoint
  mockAxios.onGet('/api/ships').reply(200, mockShips);
  
  // Mock systems endpoint
  mockAxios.onGet('/api/systems').reply(200, mockSystems);
  
  // Mock factions endpoint
  mockAxios.onGet('/api/factions').reply(200, mockFactions);
  
  // Mock waypoints endpoint
  mockAxios.onGet(/\/api\/systems\/.*\/waypoints/).reply(200, mockWaypoints);
  
  // Mock ship actions
  mockAxios.onPost(/\/api\/ships\/.*\/navigate/).reply(200, {
    data: {
      fuel: { current: 48, capacity: 100, consumed: { amount: 2, timestamp: "2023-11-01T00:00:00.000Z" } },
      nav: mockShips[0].nav
    }
  });
  
  mockAxios.onPost(/\/api\/ships\/.*\/dock/).reply(200, {
    data: { nav: { ...mockShips[0].nav, status: "DOCKED" } }
  });
  
  mockAxios.onPost(/\/api\/ships\/.*\/orbit/).reply(200, {
    data: { nav: { ...mockShips[0].nav, status: "IN_ORBIT" } }
  });
  
  // Mock security endpoints
  mockAxios.onGet(/\/api\/ships\/.*\/security\/status/).reply(200, {
    cloakingActive: false,
    stealthModeActive: false,
    signalJammingActive: false,
    electronicWarfareActive: false,
    countermeasuresActive: false,
    encryptionActive: false,
    energyConsumption: 0
  });
  
  // Mock resource endpoints
  mockAxios.onGet(/\/api\/ships\/.*\/resources/).reply(200, {
    fuel: { current: 80, capacity: 100, efficiency: 90, consumption_rate: 1.2 },
    power: { current: 85, capacity: 100, distribution: { engines: 35, life_support: 25, systems: 20, shields: 15 } },
    heat: { current: 45, max_safe: 80, dissipation_rate: 2.1, thermal_vents: 4 },
    life_support: { oxygen: 95, temperature: 22, humidity: 48, crew_comfort: 85, air_quality: 92 },
    waste: { organic: 8, recyclable: 6, hazardous: 2, recycling_efficiency: 78, storage_capacity: 50 },
    emergency: { medical: 90, rations: 85, oxygen_backup: 95, repair_kits: 3, emergency_beacon: true }
  });
  
  // Mock crew endpoints
  mockAxios.onGet(/\/api\/ships\/.*\/crew/).reply(200, {
    data: [
      {
        symbol: "CREW_001",
        name: "Captain Rodriguez",
        role: "PILOT",
        level: 5,
        experience: 850,
        health: 100,
        morale: 85,
        skills: { piloting: 95, navigation: 90, leadership: 80 },
        salary: 200
      }
    ]
  });
  
  // Mock scan endpoints
  mockAxios.onPost(/\/api\/ships\/.*\/scan\/systems/).reply(201, {
    data: {
      cooldown: { shipSymbol: "DEMO_SHIP_1", totalSeconds: 70, remainingSeconds: 70 },
      systems: [
        { symbol: "X1-DF56", sectorSymbol: "X1", type: "RED_STAR", x: 100, y: -50, distance: 150.2 }
      ]
    }
  });
  
  mockAxios.onPost(/\/api\/ships\/.*\/scan\/waypoints/).reply(201, {
    data: {
      cooldown: { shipSymbol: "DEMO_SHIP_1", totalSeconds: 60, remainingSeconds: 60 },
      waypoints: [
        {
          symbol: "X1-DF55-20250C",
          type: "PLANET",
          systemSymbol: "X1-DF55",
          x: 45,
          y: -80,
          traits: [
            { symbol: "VOLCANIC", name: "Volcanic", description: "Volcanic activity detected" }
          ]
        }
      ]
    }
  });
  
  mockAxios.onPost(/\/api\/ships\/.*\/scan\/ships/).reply(201, {
    data: {
      cooldown: { shipSymbol: "DEMO_SHIP_1", totalSeconds: 10, remainingSeconds: 10 },
      ships: [
        {
          symbol: "MERCHANT_VESSEL_001",
          registration: { factionSymbol: "COSMIC", role: "TRADER" },
          nav: { waypointSymbol: "X1-DF55-20250Y", status: "IN_ORBIT" },
          frame: { symbol: "FRAME_LIGHT_FREIGHTER" },
          cargo: { units: 75, capacity: 100 },
          threat_level: "LOW",
          distance: 25.5
        }
      ]
    }
  });
  
  // Mock equipment endpoints
  mockAxios.onGet('/api/equipment').reply(200, {
    data: {
      modules: [
        {
          symbol: "MODULE_CARGO_HOLD_I",
          name: "Cargo Hold I",
          description: "Expand your ship's cargo capacity",
          capacity: 30,
          requirements: { power: 1, crew: 0, slots: 1 },
          price: 5000
        }
      ],
      mounts: [
        {
          symbol: "MOUNT_MINING_LASER_I",
          name: "Mining Laser I",
          description: "Basic mining laser for extracting resources",
          strength: 10,
          deposits: ["IRON", "COPPER", "ALUMINUM"],
          requirements: { power: 2, crew: 0, slots: 1 },
          price: 8000
        }
      ]
    }
  });
};

// Utility to wait for async operations
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

// Clean up function for tests
export const cleanup = () => {
  mockAxios.reset();
};

// Re-export everything from RTL
export * from '@testing-library/react';
export { render };
export { default as userEvent } from '@testing-library/user-event';