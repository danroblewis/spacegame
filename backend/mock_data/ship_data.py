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