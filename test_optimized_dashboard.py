#!/usr/bin/env python3
"""
CYBERSEC PRO DASHBOARD - COMPREHENSIVE TEST SUITE
=================================================
This script tests all optimized dashboard functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

class DashboardTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.dashboard_url = "http://localhost:8050"
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" ({details})"
            
        self.test_results.append(result)
        print(result)
        
    def test_api_health(self):
        """Test API server health"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=5)
            success = response.status_code == 200
            data = response.json() if success else {}
            details = f"Status: {response.status_code}, Message: {data.get('message', 'No message')}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test("API Health Check", success, details)
        return success
        
    def test_dashboard_health(self):
        """Test dashboard server health"""
        try:
            response = requests.get(f"{self.dashboard_url}/", timeout=10)
            success = response.status_code == 200 and "html" in response.headers.get('content-type', '')
            details = f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'Unknown')}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test("Dashboard Health Check", success, details)
        return success
        
    def test_get_aos(self):
        """Test getting Application Owners list"""
        try:
            response = requests.get(f"{self.api_url}/aos", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                ao_count = len(data.get('application_owners', []))
                details = f"Found {ao_count} Application Owners"
            else:
                details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test("Get Application Owners", success, details)
        return success, data if success else None
        
    def test_suggestions(self, ao_id):
        """Test suggestions for a specific AO"""
        try:
            response = requests.get(f"{self.api_url}/suggestions/{ao_id}", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                suggestion_count = len(data.get('suggestions', []))
                details = f"Generated {suggestion_count} suggestions for {ao_id}"
            else:
                details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test(f"Generate Suggestions for {ao_id}", success, details)
        return success
        
    def test_chatbot(self):
        """Test chatbot functionality"""
        try:
            payload = {"question": "What are the main cybersecurity risks?"}
            response = requests.post(f"{self.api_url}/chatbot", 
                                   json=payload, timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                answer_length = len(data.get('answer', ''))
                confidence = data.get('relevance_score', 0)
                details = f"Answer: {answer_length} chars, Confidence: {confidence:.2f}"
            else:
                details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test("Chatbot Query", success, details)
        return success
        
    def test_departments(self):
        """Test getting departments list"""
        try:
            response = requests.get(f"{self.api_url}/departments", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                dept_count = len(data.get('departments', []))
                details = f"Found {dept_count} departments"
            else:
                details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test("Get Departments", success, details)
        return success
        
    def test_applications(self):
        """Test getting applications list"""
        try:
            response = requests.get(f"{self.api_url}/applications", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                app_count = len(data.get('applications', []))
                details = f"Found {app_count} applications"
            else:
                details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = str(e)
            
        self.log_test("Get Applications", success, details)
        return success
        
    def test_performance(self):
        """Test API response times"""
        endpoints = [
            f"{self.api_url}/",
            f"{self.api_url}/aos",
            f"{self.api_url}/departments"
        ]
        
        total_time = 0
        successful_requests = 0
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(endpoint, timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    total_time += response_time
                    successful_requests += 1
                    
            except Exception:
                pass
                
        if successful_requests > 0:
            avg_response_time = total_time / successful_requests
            success = avg_response_time < 1000  # Less than 1 second
            details = f"Average response time: {avg_response_time:.0f}ms"
        else:
            success = False
            details = "No successful requests"
            
        self.log_test("API Performance", success, details)
        return success
        
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🧪 CYBERSEC PRO DASHBOARD - COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # Test API health first
        if not self.test_api_health():
            print("❌ API server not responding. Please start the API server first.")
            return False
            
        # Test dashboard health
        if not self.test_dashboard_health():
            print("❌ Dashboard server not responding. Please start the dashboard first.")
            return False
            
        print("")
        print("🔍 Testing API Endpoints...")
        print("-" * 40)
        
        # Test all API endpoints
        aos_success, aos_data = self.test_get_aos()
        self.test_departments()
        self.test_applications()
        
        # Test suggestions with real AO data
        if aos_success and aos_data:
            application_owners = aos_data.get('application_owners', [])
            if application_owners:
                # Test with first few AOs
                for ao in application_owners[:3]:
                    ao_id = ao.get('Application_Owner_ID')
                    if ao_id:
                        self.test_suggestions(ao_id)
        
        # Test chatbot
        self.test_chatbot()
        
        print("")
        print("⚡ Testing Performance...")
        print("-" * 40)
        self.test_performance()
        
        # Print summary
        print("")
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(result)
            
        print("")
        print(f"📈 Results: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED! Dashboard is fully functional.")
            return True
        else:
            failed_tests = self.total_tests - self.passed_tests
            print(f"⚠️  {failed_tests} test(s) failed. Check the details above.")
            return False
            
    def generate_report(self):
        """Generate detailed test report"""
        report = f"""
# 🧪 CYBERSEC PRO DASHBOARD - TEST REPORT

**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dashboard Version**: 2.0 Enhanced
**Test Suite**: Comprehensive Functionality Tests

## 📊 Test Results Summary

- **Total Tests**: {self.total_tests}
- **Passed**: {self.passed_tests}
- **Failed**: {self.total_tests - self.passed_tests}
- **Success Rate**: {(self.passed_tests/self.total_tests*100):.1f}%

## 📝 Detailed Results

"""
        for result in self.test_results:
            report += f"- {result}\n"
            
        report += f"""
## 🎯 Overall Status

{"✅ **ALL SYSTEMS OPERATIONAL** - Dashboard is ready for production use!" if self.passed_tests == self.total_tests else "⚠️ **ISSUES DETECTED** - Some tests failed, review details above."}

## 🌐 Access URLs

- **Dashboard**: http://localhost:8050
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (if available)

---
*Generated by CyberSec Pro Dashboard Test Suite v2.0*
"""
        
        with open('CURRENT_TEST_RESULTS.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"\n📋 Detailed test report saved to: CURRENT_TEST_RESULTS.md")

if __name__ == "__main__":
    tester = DashboardTester()
    success = tester.run_all_tests()
    tester.generate_report()
    
    sys.exit(0 if success else 1)
