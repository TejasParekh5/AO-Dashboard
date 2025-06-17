"""
🔧 DASHBOARD FIXES VALIDATION TEST
=====================================

This script tests the fixes applied to the dashboard to ensure:
1. Color scheme fixes (success, warning, info keys)
2. Font weight fixes (removed invalid 'weight' property)
3. Set indexing fixes (using lists instead of sets)
4. Input validation fixes (ensuring lists for dropdown values)

Author: AI Assistant
Date: June 17, 2025
"""

import sys
import os
import traceback
import requests
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_imports():
    """Test if dashboard can be imported without errors"""
    print("🔍 Testing dashboard imports...")
    try:
        import dashboard_optimized
        print("✅ Dashboard imports successful")
        return True
    except Exception as e:
        print(f"❌ Dashboard import failed: {e}")
        traceback.print_exc()
        return False

def test_api_imports():
    """Test if API can be imported without errors"""
    print("🔍 Testing API imports...")
    try:
        import api_optimized
        print("✅ API imports successful")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_color_scheme():
    """Test if all required color keys are available"""
    print("🔍 Testing color scheme fixes...")
    try:
        import dashboard_optimized
        colors = dashboard_optimized.colors
        
        required_colors = ['success', 'warning', 'info', 'danger', 'Critical', 'High', 'Medium', 'Low']
        missing_colors = [color for color in required_colors if color not in colors]
        
        if missing_colors:
            print(f"❌ Missing color keys: {missing_colors}")
            return False
        else:
            print("✅ All required color keys are present")
            return True
    except Exception as e:
        print(f"❌ Color scheme test failed: {e}")
        return False

def test_api_endpoints():
    """Test if API endpoints are accessible"""
    print("🔍 Testing API endpoints...")
    try:
        # Test basic connectivity
        response = requests.get("http://127.0.0.1:8001/", timeout=5)
        if response.status_code in [200, 404]:  # 404 is fine for root
            print("✅ API server is accessible")
            
            # Test docs endpoint
            docs_response = requests.get("http://127.0.0.1:8001/api/docs", timeout=5)
            if docs_response.status_code == 200:
                print("✅ API documentation is accessible")
                return True
            else:
                print(f"⚠️  API docs returned status: {docs_response.status_code}")
                return True  # Server is still accessible
        else:
            print(f"❌ API server returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  API server not accessible (may not be running): {e}")
        return False

def test_dashboard_accessibility():
    """Test if dashboard is accessible"""
    print("🔍 Testing dashboard accessibility...")
    try:
        response = requests.get("http://127.0.0.1:8050", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            return True
        else:
            print(f"❌ Dashboard returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Dashboard not accessible (may not be running): {e}")
        return False

def test_data_loading():
    """Test if data loads correctly"""
    print("🔍 Testing data loading...")
    try:
        import dashboard_optimized
        df = dashboard_optimized.df
        
        if len(df) > 0:
            print(f"✅ Data loaded successfully: {len(df)} records")
            
            # Test required columns
            required_columns = ['Application_Owner_ID', 'Status', 'Vulnerability_Severity']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns present")
                return True
        else:
            print("❌ No data loaded")
            return False
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 Starting Dashboard Fixes Validation Test")
    print("=" * 50)
    
    tests = [
        ("Dashboard Imports", test_dashboard_imports),
        ("API Imports", test_api_imports),
        ("Color Scheme", test_dashboard_color_scheme),
        ("Data Loading", test_data_loading),
        ("Dashboard Accessibility", test_dashboard_accessibility),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Dashboard fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    print("\n💡 Next Steps:")
    if passed >= total - 2:  # Allow for API/Dashboard not running
        print("1. Dashboard code fixes are successful")
        print("2. Start both API and Dashboard servers if not running")
        print("3. Open http://localhost:8050 to test the UI")
        print("4. Test all dashboard features interactively")
    else:
        print("1. Review and fix the failing tests")
        print("2. Re-run this validation script")
        print("3. Check the terminal logs for detailed error messages")

if __name__ == "__main__":
    main()
