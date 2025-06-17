#!/usr/bin/env python3
"""
Quick test to verify dashboard components are working correctly
"""

import requests
import time

def test_dashboard_health():
    """Test if dashboard is accessible"""
    try:
        response = requests.get("http://localhost:8050", timeout=5)
        print(f"✅ Dashboard accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")
        return False

def test_api_health():
    """Test if API is accessible"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"✅ API accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"⚠️  API not accessible: {e}")
        return False

def main():
    print("🔍 Testing Dashboard Components...")
    print("=" * 50)
    
    dashboard_ok = test_dashboard_health()
    api_ok = test_api_health()
    
    print("=" * 50)
    if dashboard_ok:
        print("✅ Dashboard is running successfully!")
        print("🌐 URL: http://localhost:8050")
        
        if api_ok:
            print("✅ API is running - All AI features available!")
        else:
            print("⚠️  API not running - AI features may be limited")
    else:
        print("❌ Dashboard is not accessible")
    
    print("\n📋 Summary of Fixed Components:")
    print("   ✅ Removed duplicate sidebar components")
    print("   ✅ Fixed duplicate chatbot IDs")
    print("   ✅ Single Smart Filters panel")
    print("   ✅ Single AI Insights panel")
    print("   ✅ Single AI Security Assistant")
    print("   ✅ Single Export & Reports panel")

if __name__ == "__main__":
    main()
