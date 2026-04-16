"""
Phase 2b Authentication Testing Script
Tests the complete authentication system implementation
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": f"test_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "full_name": "Authentication Test User"
}

class AuthenticationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.access_token = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_health_check(self):
        """Test that the backend is running"""
        print("🏥 Testing backend health...")
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                print("✅ Backend is healthy")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False
    
    async def test_user_registration(self):
        """Test user registration endpoint"""
        print(f"📝 Testing user registration for: {TEST_USER['email']}")
        try:
            response = await self.client.post(
                "/api/auth/register",
                json=TEST_USER
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get("success") and data.get("access_token"):
                    self.access_token = data["access_token"]
                    user = data.get("user", {})
                    print(f"✅ Registration successful!")
                    print(f"   📧 Email: {user.get('email')}")
                    print(f"   🆔 User ID: {user.get('id')}")
                    print(f"   🎫 Token received: {self.access_token[:20]}...")
                    return True
                else:
                    print(f"❌ Registration response missing required fields: {data}")
                    return False
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Registration failed ({response.status_code}): {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Registration request failed: {e}")
            return False
    
    async def test_user_login(self):
        """Test user login endpoint"""
        print(f"🔑 Testing user login for: {TEST_USER['email']}")
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = await self.client.post(
                "/api/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("access_token"):
                    self.access_token = data["access_token"]
                    user = data.get("user", {})
                    print(f"✅ Login successful!")
                    print(f"   📧 Email: {user.get('email')}")
                    print(f"   🆔 User ID: {user.get('id')}")
                    print(f"   🎫 New token: {self.access_token[:20]}...")
                    return True
                else:
                    print(f"❌ Login response missing required fields: {data}")
                    return False
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Login failed ({response.status_code}): {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False
    
    async def test_protected_route(self):
        """Test protected route access with JWT token"""
        print("🔒 Testing protected route access...")
        try:
            if not self.access_token:
                print("❌ No access token available for protected route test")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = await self.client.get(
                "/api/auth/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Protected route access successful!")
                print(f"   📧 User email: {data.get('email')}")
                print(f"   👤 Full name: {data.get('full_name')}")
                print(f"   🎯 Subscription: {data.get('subscription_tier')}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Protected route access failed ({response.status_code}): {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Protected route request failed: {e}")
            return False
    
    async def test_invalid_token(self):
        """Test rejection of invalid JWT token"""
        print("🚫 Testing invalid token rejection...")
        try:
            headers = {
                "Authorization": "Bearer invalid_token_12345"
            }
            
            response = await self.client.get(
                "/api/auth/me",
                headers=headers
            )
            
            if response.status_code == 401:
                print("✅ Invalid token correctly rejected")
                return True
            else:
                print(f"❌ Invalid token not rejected properly: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Invalid token test failed: {e}")
            return False
    
    async def test_invalid_credentials(self):
        """Test rejection of invalid login credentials"""
        print("🔐 Testing invalid credentials rejection...")
        try:
            invalid_login = {
                "email": TEST_USER["email"],
                "password": "wrong_password"
            }
            
            response = await self.client.post(
                "/api/auth/login",
                json=invalid_login
            )
            
            if response.status_code == 401:
                print("✅ Invalid credentials correctly rejected")
                return True
            else:
                print(f"❌ Invalid credentials not rejected properly: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Invalid credentials test failed: {e}")
            return False
    
    async def test_duplicate_registration(self):
        """Test rejection of duplicate email registration"""
        print("📧 Testing duplicate email rejection...")
        try:
            response = await self.client.post(
                "/api/auth/register",
                json=TEST_USER
            )
            
            if response.status_code == 400:
                error_detail = response.json().get("detail", "")
                if "already exists" in error_detail.lower():
                    print("✅ Duplicate email correctly rejected")
                    return True
                else:
                    print(f"❌ Wrong error message for duplicate: {error_detail}")
                    return False
            else:
                print(f"❌ Duplicate registration not rejected properly: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Duplicate registration test failed: {e}")
            return False
    
    async def test_token_refresh(self):
        """Test JWT token refresh endpoint"""
        print("🔄 Testing token refresh...")
        try:
            if not self.access_token:
                print("❌ No access token available for refresh test")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = await self.client.post(
                "/api/auth/refresh",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("access_token"):
                    old_token = self.access_token[:20]
                    self.access_token = data["access_token"]
                    new_token = self.access_token[:20]
                    print(f"✅ Token refresh successful!")
                    print(f"   🔄 Old token: {old_token}...")
                    print(f"   🆕 New token: {new_token}...")
                    return True
                else:
                    print(f"❌ Token refresh response missing fields: {data}")
                    return False
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Token refresh failed ({response.status_code}): {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Token refresh request failed: {e}")
            return False
    
    async def test_password_reset_request(self):
        """Test password reset request endpoint"""
        print("🔑 Testing password reset request...")
        try:
            reset_data = {
                "email": TEST_USER["email"]
            }
            
            response = await self.client.post(
                "/api/auth/password-reset-request",
                json=reset_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Password reset request successful!")
                    print(f"   📧 Message: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Password reset request failed: {data}")
                    return False
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Password reset request failed ({response.status_code}): {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Password reset request failed: {e}")
            return False
    
    async def test_logout(self):
        """Test logout endpoint"""
        print("👋 Testing logout...")
        try:
            response = await self.client.post("/api/auth/logout")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Logout successful!")
                    print(f"   📧 Message: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Logout failed: {data}")
                    return False
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"❌ Logout failed ({response.status_code}): {error_detail}")
                return False
                
        except Exception as e:
            print(f"❌ Logout request failed: {e}")
            return False

    async def run_full_test_suite(self):
        """Run the complete authentication test suite"""
        print("🚀 Starting Phase 2b Authentication Test Suite")
        print("=" * 60)
        
        tests = [
            ("Backend Health", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Protected Route Access", self.test_protected_route),
            ("Invalid Token Rejection", self.test_invalid_token),
            ("Invalid Credentials Rejection", self.test_invalid_credentials),
            ("Duplicate Email Rejection", self.test_duplicate_registration),
            ("Token Refresh", self.test_token_refresh),
            ("Password Reset Request", self.test_password_reset_request),
            ("Logout", self.test_logout),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}")
            print("-" * 40)
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results[test_name] = False
            
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 AUTHENTICATION TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status:8} {test_name}")
        
        print("-" * 60)
        print(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Phase 2b Authentication is working correctly!")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

async def main():
    """Main test runner"""
    async with AuthenticationTester() as tester:
        success = await tester.run_full_test_suite()
        return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        exit(1)
    except Exception as e:
        print(f"💥 Test suite failed with error: {e}")
        exit(1)
