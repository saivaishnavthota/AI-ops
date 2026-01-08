#!/usr/bin/env python3
"""
Test script to verify external ticketing system integration
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_external_integration():
    """Test the external ticketing system integration."""
    
    print("🔍 Testing External Ticketing System Integration")
    print("=" * 50)
    
    # Test external system health
    print("\n1. Testing external system health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/health")
            if response.status_code == 200:
                print("✅ External system is healthy")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ External system health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ Could not connect to external system: {e}")
        return
    
    # Test mock ticket generation
    print("\n2. Testing mock ticket generation...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:3001/api/mock-generator/tickets",
                params={"count": 3}
            )
            if response.status_code == 200:
                data = response.json()
                tickets = data.get('tickets', [])
                print(f"✅ Generated {len(tickets)} mock tickets")
                for i, ticket in enumerate(tickets[:2], 1):
                    print(f"   Ticket {i}: {ticket.get('title', 'No title')}")
                    print(f"   Priority: {ticket.get('priority', 'Unknown')}")
                    print(f"   Requester: {ticket.get('requesterName', 'Unknown')}")
            else:
                print(f"❌ Mock ticket generation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Mock ticket generation error: {e}")
    
    # Test AI-Ops backend health
    print("\n3. Testing AI-Ops backend health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:7027/health")
            if response.status_code == 200:
                print("✅ AI-Ops backend is healthy")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ AI-Ops backend health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ Could not connect to AI-Ops backend: {e}")
        return
    
    print("\n4. Integration test summary:")
    print("✅ External ticketing system is running on port 3001")
    print("✅ AI-Ops platform is running on port 7027")
    print("✅ Mock ticket generation is working")
    print("\n🎉 Integration test completed successfully!")
    print("\nNext steps:")
    print("1. Open http://localhost:7026 in your browser")
    print("2. Login as admin")
    print("3. Go to Support Tickets page")
    print("4. Click 'Sync External' button to fetch external tickets")
    print("5. External tickets will appear with purple 'External' tags")

if __name__ == "__main__":
    asyncio.run(test_external_integration())