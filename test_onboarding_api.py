#!/usr/bin/env python3
"""
Test script for Onboarding API

Tests the API endpoints to ensure they work correctly.

Usage:
    python3 test_onboarding_api.py
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_health():
    """Test health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_create_lead():
    """Test creating a new lead."""
    print("\nTesting lead creation...")
    
    payload = {
        "name": "Jan Testovací",
        "email": "jan.test@example.com",
        "description": "Učím se JavaScript už 6 měsíců, vytvořil jsem pár vlastních projektů a chci získat první práci jako frontend developer.\n\nCíl: První práce v IT\nOblast: Frontend Development\nÚroveň: Začátečník\nČasový horizont: 6 měsíců",
        "input_transform": {
            "obor": "Frontend Development",
            "seniorita": "Začátečník",
            "hlavni_cil": "První práce v IT",
            "casovy_horizont": "6 měsíců",
            "technologie": [],
            "raw_description": "Učím se JavaScript už 6 měsíců, vytvořil jsem pár vlastních projektů a chci získat první práci jako frontend developer."
        },
        "status": "FLAGGED"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/leads",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] == True
        assert 'lead_id' in data
        
        lead_id = data['lead_id']
        print(f"✅ Lead created successfully: {lead_id}")
        
        return lead_id
        
    except AssertionError as e:
        print(f"❌ Lead creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Lead creation failed: {e}")
        return None


def test_get_lead(lead_id):
    """Test getting lead by ID."""
    print(f"\nTesting lead retrieval for {lead_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/api/leads/{lead_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['data']['id'] == lead_id
        
        print("✅ Lead retrieved successfully")
        print(f"   Name: {data['data']['name']}")
        print(f"   Email: {data['data']['email']}")
        print(f"   Status: {data['data']['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lead retrieval failed: {e}")
        return False


def test_validation():
    """Test validation errors."""
    print("\nTesting validation...")
    
    # Test missing fields
    try:
        response = requests.post(
            f"{API_BASE}/api/leads",
            json={"name": "Test"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✅ Missing fields validation passed")
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False
    
    # Test invalid email
    try:
        response = requests.post(
            f"{API_BASE}/api/leads",
            json={
                "name": "Test",
                "email": "invalid-email",
                "description": "Test description"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✅ Invalid email validation passed")
    except Exception as e:
        print(f"❌ Email validation test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("🔮 ORAKULUM ONBOARDING API TESTS")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print()
    
    # Check if API is running
    try:
        requests.get(f"{API_BASE}/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running!")
        print("   Start it with: python3 api_onboarding.py")
        return
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    time.sleep(0.5)
    
    # Test 2: Create lead
    lead_id = test_create_lead()
    results.append(("Create Lead", lead_id is not None))
    
    time.sleep(0.5)
    
    # Test 3: Get lead (if creation succeeded)
    if lead_id:
        results.append(("Get Lead", test_get_lead(lead_id)))
    
    time.sleep(0.5)
    
    # Test 4: Validation
    results.append(("Validation", test_validation()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print()
    print(f"   Total: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed")


if __name__ == "__main__":
    main()
