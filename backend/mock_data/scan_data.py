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