#!/usr/bin/env python3

import os
import sys
import asyncio
import httpx

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the main app and endpoints
from main import app, navigate_ship, create_survey, HAS_VALID_TOKEN, SPACETRADERS_TOKEN
from main import NavigateRequest, MOCK_SHIPS

async def test_navigate_endpoint():
    """Test the navigate endpoint with mock data"""
    print("\n=== Testing Navigate Endpoint ===")
    print(f"Has valid token: {HAS_VALID_TOKEN}")
    print(f"Token: {SPACETRADERS_TOKEN}")
    
    # Create a mock request
    request = NavigateRequest(waypointSymbol="X1-DF55-20250Y")
    
    try:
        async with httpx.AsyncClient() as client:
            result = await navigate_ship("DEMO_SHIP_1", request, client)
            print("Navigate endpoint SUCCESS:")
            print(f"Result: {result}")
            return True
    except Exception as e:
        print(f"Navigate endpoint FAILED: {e}")
        return False

async def test_survey_endpoint():
    """Test the survey endpoint with mock data"""
    print("\n=== Testing Survey Endpoint ===")
    
    try:
        async with httpx.AsyncClient() as client:
            result = await create_survey("DEMO_SHIP_1", client)
            print("Survey endpoint SUCCESS:")
            print(f"Result: {result}")
            return True
    except Exception as e:
        print(f"Survey endpoint FAILED: {e}")
        return False

async def main():
    print("Testing SpaceTraders Endpoints")
    print("=" * 40)
    
    # Test navigate endpoint
    nav_success = await test_navigate_endpoint()
    
    # Test survey endpoint  
    survey_success = await test_survey_endpoint()
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print(f"Navigate endpoint: {'✅ PASS' if nav_success else '❌ FAIL'}")
    print(f"Survey endpoint: {'✅ PASS' if survey_success else '❌ FAIL'}")
    
    if nav_success and survey_success:
        print("\n🎉 All endpoints are working correctly!")
        return 0
    else:
        print("\n⚠️  Some endpoints have issues that need to be fixed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)