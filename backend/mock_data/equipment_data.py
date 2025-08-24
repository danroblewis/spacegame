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