#!/usr/bin/env python3
"""
Test script to verify that the suggestions and chatbot fixes are working
"""

import requests
import json
import time

# API base URL
API_BASE = "http://127.0.0.1:8001"
DASHBOARD_BASE = "http://127.0.0.1:8050"

def test_api_health():
    """Test API health endpoint"""
    print("🏥 Testing API health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_get_aos():
    """Test getting Application Owners"""
    print("\n👥 Testing AO list retrieval...")
    try:
        response = requests.get(f"{API_BASE}/aos")
        if response.status_code == 200:
            data = response.json()
            aos = data.get('application_owners', [])
            print(f"✅ Retrieved {len(aos)} Application Owners")
            if aos:
                print(f"   📋 Sample AOs: {aos[0]['Application_Owner_ID']} - {aos[0]['Application_Owner_Name']}")
                return aos[:3]  # Return first 3 for testing
        else:
            print(f"❌ Failed to get AOs: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting AOs: {e}")
        return []

def test_individual_suggestions(ao_id):
    """Test individual AO suggestions"""
    print(f"\n💡 Testing individual suggestions for {ao_id}...")
    try:
        response = requests.get(f"{API_BASE}/suggestions/{ao_id}")
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"✅ Got {len(suggestions)} suggestions for {ao_id}")
            if suggestions:
                print(f"   📝 Sample suggestion: {suggestions[0]['text'][:80]}...")
            return True
        else:
            print(f"❌ Failed to get suggestions for {ao_id}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting suggestions for {ao_id}: {e}")
        return False

def test_multiple_suggestions(aos):
    """Test multiple AO suggestions endpoint"""
    print(f"\n💡 Testing multiple suggestions for {len(aos)} AOs...")
    try:
        # Prepare request data
        request_data = {
            "aos": [
                {
                    "ao_id": ao["Application_Owner_ID"],
                    "ao_name": ao["Application_Owner_Name"]
                }
                for ao in aos
            ]
        }
        
        response = requests.post(
            f"{API_BASE}/suggestions",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"✅ Got {len(suggestions)} combined suggestions")
            if suggestions:
                print(f"   📝 Sample: {suggestions[0]['text'][:80]}...")
            return True
        else:
            print(f"❌ Failed to get multiple suggestions: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting multiple suggestions: {e}")
        return False

def test_chatbot(ao_id=None):
    """Test chatbot endpoint"""
    print(f"\n🤖 Testing chatbot...")
    try:
        request_data = {
            "question": "How can I improve my security posture?",
            "ao_id": ao_id
        }
        
        response = requests.post(
            f"{API_BASE}/chatbot",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            confidence = data.get('confidence', 0)
            print(f"✅ Chatbot responded with confidence {confidence:.2f}")
            print(f"   🗨️ Response: {response_text[:100]}...")
            return True
        else:
            print(f"❌ Chatbot failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        return False

def test_dashboard():
    """Test dashboard accessibility"""
    print(f"\n🖥️ Testing dashboard...")
    try:
        response = requests.get(DASHBOARD_BASE)
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running CyberSec Pro Dashboard Fix Tests")
    print("=" * 50)
    
    results = {
        "api_health": False,
        "ao_retrieval": False,
        "individual_suggestions": False,
        "multiple_suggestions": False,
        "chatbot": False,
        "dashboard": False
    }
    
    # Test API health
    results["api_health"] = test_api_health()
    
    if results["api_health"]:
        # Get AOs for testing
        aos = test_get_aos()
        results["ao_retrieval"] = len(aos) > 0
        
        if results["ao_retrieval"]:
            # Test individual suggestions
            results["individual_suggestions"] = test_individual_suggestions(aos[0]["Application_Owner_ID"])
            
            # Test multiple suggestions
            results["multiple_suggestions"] = test_multiple_suggestions(aos)
            
            # Test chatbot
            results["chatbot"] = test_chatbot(aos[0]["Application_Owner_ID"])
    
    # Test dashboard
    results["dashboard"] = test_dashboard()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The fixes are working correctly.")
        print("\n✅ Key fixes implemented:")
        print("   • Added POST /suggestions endpoint for multiple AOs")
        print("   • Fixed chatbot request format (ao_id + question)")
        print("   • Updated response models to match expected format")
        print("   • Fixed API port configuration (8001)")
        print("   • Dashboard now correctly calls both endpoints")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
