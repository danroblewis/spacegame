import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SPACETRADERS_TOKEN = os.getenv("SPACETRADERS_TOKEN")
SPACETRADERS_CALLSIGN = os.getenv("SPACETRADERS_CALLSIGN")
SPACETRADERS_API_URL = os.getenv("SPACETRADERS_API_URL", "https://api.spacetraders.io/v2")

# Check if we have a valid token
HAS_VALID_TOKEN = SPACETRADERS_TOKEN and SPACETRADERS_TOKEN != "demo_token_for_testing"

# Available ship customizations
SHIP_COLORS = ["red", "blue", "green", "gold", "silver", "black", "white", "purple"]
SHIP_DECALS = ["flames", "stars", "stripes", "dragon", "eagle", "skull", "lightning", "geometric"]

# CORS configuration
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]