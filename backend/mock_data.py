# Mock data for testing

MOCK_AVAILABLE_CREW = [
    {
        "id": "hire_001",
        "name": "Marcus Thompson",
        "role": "GUNNER",
        "level": 2,
        "skills": {"combat": 70, "weapons": 75, "tactics": 60},
        "salary": 100
    },
    {
        "id": "hire_002",
        "name": "Dr. Elena Vasquez",
        "role": "MEDIC",
        "level": 3,
        "skills": {"medicine": 85, "surgery": 80, "biology": 70},
        "salary": 130
    },
    {
        "id": "hire_003",
        "name": "Jake Morrison",
        "role": "MINER",
        "level": 3,
        "skills": {"mining": 80, "geology": 75, "equipment": 70},
        "salary": 110
    },
    {
        "id": "hire_004",
        "name": "Security Chief Rivera",
        "role": "SECURITY",
        "level": 4,
        "skills": {"security": 90, "combat": 85, "investigation": 75},
        "salary": 140
    }
]

MOCK_AGENT = {
    "symbol": "DEMO_AGENT",
    "headquarters": "X1-DF55-20250X",
    "credits": 1000000,
    "startingFaction": "COSMIC"
}

MOCK_SHIPS = [
    {
        "symbol": "DEMO_SHIP_1",
        "registration": {"name": "Explorer One", "role": "EXPLORER"},
        "nav": {
            "status": "IN_ORBIT", 
            "waypointSymbol": "X1-DF55-20250X",
            "systemSymbol": "X1-DF55",
            "route": {
                "destination": {
                    "symbol": "X1-DF55-20250X",
                    "type": "PLANET",
                    "systemSymbol": "X1-DF55",
                    "x": -42,
                    "y": -26
                },
                "origin": {
                    "symbol": "X1-DF55-20250X",
                    "type": "PLANET",
                    "systemSymbol": "X1-DF55",
                    "x": -42,
                    "y": -26
                },
                "departureTime": "2023-11-01T00:00:00.000Z",
                "arrival": "2023-11-01T00:00:00.000Z"
            }
        },
        "crew": {"current": 2, "capacity": 4},
        "frame": {"name": "Explorer Frame", "symbol": "FRAME_EXPLORER"},
        "reactor": {"name": "Basic Reactor", "symbol": "REACTOR_FUSION_I", "powerOutput": 15},
        "engine": {"name": "Basic Engine", "symbol": "ENGINE_ION_DRIVE_I", "speed": 25},
        "modules": [
            {"name": "Shield Generator I", "symbol": "MODULE_SHIELD_GENERATOR_I", "description": "Basic shield generator"},
            {"name": "Cargo Hold I", "symbol": "MODULE_CARGO_HOLD_I", "description": "Basic cargo storage"}
        ],
        "mounts": [
            {"name": "Laser Cannon I", "symbol": "MOUNT_LASER_CANNON_I", "description": "Basic laser cannon"},
            {"name": "Missile Launcher I", "symbol": "MOUNT_MISSILE_LAUNCHER_I", "description": "Basic missile launcher"}
        ],
        "cargo": {"units": 50, "capacity": 100, "inventory": [{"symbol": "FUEL", "units": 50}]}
    }
]

MOCK_SYSTEMS = [
    {
        "symbol": "X1-DF55",
        "sectorSymbol": "X1",
        "type": "NEUTRON_STAR",
        "x": 0,
        "y": 0,
        "waypoints": [
            {"symbol": "X1-DF55-20250X", "type": "PLANET", "x": -42, "y": -26},
            {"symbol": "X1-DF55-20250Y", "type": "ASTEROID_FIELD", "x": 18, "y": -175},
            {"symbol": "X1-DF55-20250Z", "type": "JUMP_GATE", "x": 48, "y": 12},
            {"symbol": "X1-DF55-20250A", "type": "GAS_GIANT", "x": -85, "y": 92},
            {"symbol": "X1-DF55-20250B", "type": "MOON", "x": -38, "y": -15}
        ],
        "factions": [{"symbol": "COSMIC"}]
    }
]

MOCK_WAYPOINTS = [
    {
        "symbol": "X1-DF55-20250X",
        "type": "PLANET",
        "systemSymbol": "X1-DF55",
        "x": -42,
        "y": -26,
        "orbitals": [{"symbol": "X1-DF55-20250B"}],
        "traits": [
            {"symbol": "MARKETPLACE", "name": "Marketplace", "description": "A thriving marketplace where goods and services are traded."},
            {"symbol": "SHIPYARD", "name": "Shipyard", "description": "A facility where ships are constructed, repaired, and outfitted."}
        ],
        "faction": {"symbol": "COSMIC"}
    },
    {
        "symbol": "X1-DF55-20250Y",
        "type": "ASTEROID_FIELD",
        "systemSymbol": "X1-DF55",
        "x": 18,
        "y": -175,
        "orbitals": [],
        "traits": [
            {"symbol": "COMMON_METAL_DEPOSITS", "name": "Common Metal Deposits", "description": "Large deposits of common metals."},
            {"symbol": "RARE_METAL_DEPOSITS", "name": "Rare Metal Deposits", "description": "Rare metal deposits."}
        ]
    },
    {
        "symbol": "X1-DF55-20250Z",
        "type": "JUMP_GATE",
        "systemSymbol": "X1-DF55",
        "x": 48,
        "y": 12,
        "orbitals": [],
        "traits": [
            {"symbol": "UNCHARTED", "name": "Uncharted", "description": "An uncharted waypoint."}
        ]
    },
    {
        "symbol": "X1-DF55-20250A",
        "type": "GAS_GIANT",
        "systemSymbol": "X1-DF55",
        "x": -85,
        "y": 92,
        "orbitals": [],
        "traits": [
            {"symbol": "FROZEN", "name": "Frozen", "description": "A cold, frozen world."}
        ]
    },
    {
        "symbol": "X1-DF55-20250B",
        "type": "MOON",
        "systemSymbol": "X1-DF55",
        "x": -38,
        "y": -15,
        "orbitals": [],
        "traits": [
            {"symbol": "MINERAL_DEPOSITS", "name": "Mineral Deposits", "description": "Natural mineral deposits."}
        ]
    }
]

MOCK_FACTIONS = [
    {
        "symbol": "COSMIC",
        "name": "Cosmic Coalition",
        "description": "A powerful coalition of space-faring civilizations",
        "headquarters": "X1-DF55-20250X",
        "isRecruiting": True,
        "traits": [
            {"name": "Bureaucratic", "description": "Highly organized and bureaucratic"},
            {"name": "Secretive", "description": "Keeps information close to the chest"}
        ]
    }
]

# Mock equipment data for ship modifications
MOCK_EQUIPMENT = {
    "modules": [
        {
            "symbol": "MODULE_CARGO_HOLD_I",
            "name": "Cargo Hold I",
            "description": "Expand your ship's cargo capacity",
            "capacity": 30,
            "requirements": {"power": 1, "crew": 0, "slots": 1},
            "price": 5000
        },
        {
            "symbol": "MODULE_CARGO_HOLD_II", 
            "name": "Cargo Hold II",
            "description": "Advanced cargo storage system",
            "capacity": 50,
            "requirements": {"power": 2, "crew": 0, "slots": 2},
            "price": 12000
        },
        {
            "symbol": "MODULE_MINERAL_PROCESSOR_I",
            "name": "Mineral Processor I",
            "description": "Process raw minerals into refined goods",
            "requirements": {"power": 3, "crew": 1, "slots": 2},
            "price": 15000
        },
        {
            "symbol": "MODULE_FUEL_REFINERY_I",
            "name": "Fuel Refinery I", 
            "description": "Refine fuel from raw materials",
            "requirements": {"power": 4, "crew": 2, "slots": 3},
            "price": 25000
        },
        {
            "symbol": "MODULE_JUMP_DRIVE_I",
            "name": "Jump Drive I",
            "description": "Enable instant travel between systems",
            "range": 2000,
            "requirements": {"power": 8, "crew": 1, "slots": 4},
            "price": 50000
        },
        {
            "symbol": "MODULE_SHIELD_GENERATOR_I",
            "name": "Shield Generator I",
            "description": "Basic shield protection",
            "requirements": {"power": 5, "crew": 0, "slots": 2},
            "price": 18000
        }
    ],
    "mounts": [
        {
            "symbol": "MOUNT_MINING_LASER_I",
            "name": "Mining Laser I",
            "description": "Basic mining laser for extracting resources",
            "strength": 10,
            "deposits": ["IRON", "COPPER", "ALUMINUM"],
            "requirements": {"power": 2, "crew": 0, "slots": 1},
            "price": 8000
        },
        {
            "symbol": "MOUNT_MINING_LASER_II", 
            "name": "Mining Laser II",
            "description": "Advanced mining laser with higher yield",
            "strength": 25,
            "deposits": ["IRON", "COPPER", "ALUMINUM", "GOLD", "PLATINUM"],
            "requirements": {"power": 4, "crew": 0, "slots": 2},
            "price": 20000
        },
        {
            "symbol": "MOUNT_SURVEYOR_I",
            "name": "Surveyor I",
            "description": "Survey waypoints for valuable resources",
            "strength": 5,
            "requirements": {"power": 2, "crew": 1, "slots": 1},
            "price": 10000
        },
        {
            "symbol": "MOUNT_SENSOR_ARRAY_I",
            "name": "Sensor Array I", 
            "description": "Advanced sensors for detecting ships and hazards",
            "requirements": {"power": 3, "crew": 0, "slots": 1},
            "price": 12000
        },
        {
            "symbol": "MOUNT_GAS_SIPHON_I",
            "name": "Gas Siphon I",
            "description": "Extract gases from gas giants",
            "strength": 8,
            "deposits": ["HYDROCARBON"],
            "requirements": {"power": 3, "crew": 1, "slots": 2},
            "price": 15000
        },
        {
            "symbol": "MOUNT_LASER_CANNON_I",
            "name": "Laser Cannon I",
            "description": "Basic weapon system for ship defense",
            "strength": 15,
            "requirements": {"power": 5, "crew": 0, "slots": 1},
            "price": 22000
        }
    ],
    "reactors": [
        {
            "symbol": "REACTOR_FUSION_I",
            "name": "Fusion Reactor I",
            "description": "Advanced fusion reactor with higher power output",
            "powerOutput": 15,
            "requirements": {"power": 0, "crew": 2, "slots": 0},
            "price": 35000
        },
        {
            "symbol": "REACTOR_ANTIMATTER_I",
            "name": "Antimatter Reactor I", 
            "description": "Cutting-edge antimatter reactor",
            "powerOutput": 25,
            "requirements": {"power": 0, "crew": 3, "slots": 0},
            "price": 75000
        }
    ],
    "engines": [
        {
            "symbol": "ENGINE_ION_DRIVE_I",
            "name": "Ion Drive I",
            "description": "Efficient ion propulsion system",
            "speed": 25,
            "requirements": {"power": 4, "crew": 0, "slots": 0},
            "price": 28000
        },
        {
            "symbol": "ENGINE_HYPER_DRIVE_I", 
            "name": "Hyper Drive I",
            "description": "Ultra-fast hyperdrive engine",
            "speed": 40,
            "requirements": {"power": 8, "crew": 1, "slots": 0},
            "price": 60000
        }
    ]
}

# Mock scanning data
MOCK_SCAN_RESULTS = {
    "systems": [
        {
            "symbol": "X1-DF56",
            "sectorSymbol": "X1",
            "type": "RED_STAR",
            "x": 100,
            "y": -50,
            "distance": 150.2
        },
        {
            "symbol": "X1-DF57", 
            "sectorSymbol": "X1",
            "type": "NEUTRON_STAR",
            "x": -75,
            "y": 120,
            "distance": 95.8
        }
    ],
    "waypoints": [
        {
            "symbol": "X1-DF55-20250C",
            "type": "PLANET",
            "systemSymbol": "X1-DF55",
            "x": 45,
            "y": -80,
            "traits": [
                {"symbol": "VOLCANIC", "name": "Volcanic", "description": "Volcanic activity detected"},
                {"symbol": "RARE_METAL_DEPOSITS", "name": "Rare Metal Deposits", "description": "Contains valuable minerals"}
            ]
        },
        {
            "symbol": "X1-DF55-20250D",
            "type": "ASTEROID_FIELD",
            "systemSymbol": "X1-DF55", 
            "x": -120,
            "y": 60,
            "traits": [
                {"symbol": "COMMON_METAL_DEPOSITS", "name": "Common Metal Deposits", "description": "Standard mining resources"},
                {"symbol": "PRECIOUS_METAL_DEPOSITS", "name": "Precious Metal Deposits", "description": "Valuable precious metals detected"}
            ]
        }
    ],
    "ships": [
        {
            "symbol": "MERCHANT_VESSEL_001",
            "registration": {"factionSymbol": "COSMIC", "role": "TRADER"},
            "nav": {"waypointSymbol": "X1-DF55-20250Y", "status": "IN_ORBIT"},
            "frame": {"symbol": "FRAME_LIGHT_FREIGHTER"},
            "cargo": {"units": 75, "capacity": 100},
            "threat_level": "LOW",
            "distance": 25.5
        },
        {
            "symbol": "PATROL_SHIP_ALPHA",
            "registration": {"factionSymbol": "GALACTIC_EMPIRE", "role": "PATROL"}, 
            "nav": {"waypointSymbol": "X1-DF55-20250Z", "status": "IN_TRANSIT"},
            "frame": {"symbol": "FRAME_INTERCEPTOR"},
            "cargo": {"units": 10, "capacity": 20},
            "threat_level": "MEDIUM",
            "distance": 45.2
        }
    ]
}

# Mock survey data for intelligence/scanning features
MOCK_SURVEYS = [
    {
        "signature": "survey_001",
        "symbol": "X1-DF55-20250Y",
        "deposits": [
            {"symbol": "IRON_ORE", "name": "Iron Ore"},
            {"symbol": "COPPER_ORE", "name": "Copper Ore"},
            {"symbol": "ALUMINUM_ORE", "name": "Aluminum Ore"}
        ],
        "expiration": "2023-11-01T01:00:00.000Z",
        "size": "LARGE"
    },
    {
        "signature": "survey_002", 
        "symbol": "X1-DF55-20250B",
        "deposits": [
            {"symbol": "PRECIOUS_STONES", "name": "Precious Stones"},
            {"symbol": "RARE_EARTH_ELEMENTS", "name": "Rare Earth Elements"}
        ],
        "expiration": "2023-11-01T02:00:00.000Z",
        "size": "SMALL"
    }
]

# Mock resource data generator
def generate_mock_resource_data(ship_symbol: str):
    import random
    return {
        "fuel": {
            "current": random.randint(70, 100),
            "capacity": 100,
            "efficiency": random.randint(85, 98),
            "consumption_rate": round(random.uniform(0.8, 1.5), 1)
        },
        "power": {
            "current": random.randint(75, 95),
            "capacity": 100,
            "distribution": {
                "engines": random.randint(30, 40),
                "life_support": random.randint(20, 30),
                "systems": random.randint(15, 25),
                "shields": random.randint(10, 20)
            }
        },
        "heat": {
            "current": random.randint(30, 60),
            "max_safe": 80,
            "dissipation_rate": round(random.uniform(1.8, 2.5), 1),
            "thermal_vents": random.randint(3, 6)
        },
        "life_support": {
            "oxygen": random.randint(90, 100),
            "temperature": random.randint(20, 24),
            "humidity": random.randint(40, 55),
            "crew_comfort": random.randint(75, 95),
            "air_quality": random.randint(85, 100)
        },
        "waste": {
            "organic": random.randint(5, 15),
            "recyclable": random.randint(3, 12),
            "hazardous": random.randint(1, 5),
            "recycling_efficiency": random.randint(70, 85),
            "storage_capacity": 50
        },
        "emergency": {
            "medical": random.randint(80, 100),
            "rations": random.randint(70, 95),
            "oxygen_backup": random.randint(85, 100),
            "repair_kits": random.randint(2, 5),
            "emergency_beacon": True
        }
    }