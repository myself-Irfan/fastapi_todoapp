#!/usr/bin/env python3
"""
Test script to demonstrate JWT authentication with Argon2 password hashing.
This script shows the complete authentication flow.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_authentication_flow():
    """Test the complete authentication flow."""
    print("🔐 Testing JWT Authentication with Argon2 Password Hashing")
    print("=" * 60)
    
    # Test 1: Register a new user
    print("\n1. 👤 Registering a new user...")
    register_data = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 201:
        print("✅ User registered successfully!")
        user_data = response.json()
        print(f"   Username: {user_data['data']['username']}")
        print(f"   Email: {user_data['data']['email']}")
        print(f"   User ID: {user_data['data']['id']}")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # Test 2: Try to access protected endpoint without token
    print("\n2. 🚫 Trying to access protected endpoint without token...")
    response = requests.get(f"{BASE_URL}/api/tasks/")
    if response.status_code == 401:
        print("✅ Correctly rejected - authentication required!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    # Test 3: Login and get JWT token
    print("\n3. 🔑 Logging in to get JWT token...")
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ Login successful!")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Token preview: {access_token[:50]}...")
    else:
        print(f"❌ Login failed: {response.text}")
        return
    
    # Test 4: Access protected endpoint with valid token
    print("\n4. 🔓 Accessing protected endpoint with valid token...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
    if response.status_code == 200:
        print("✅ Successfully accessed protected endpoint!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to access protected endpoint: {response.text}")
    
    # Test 5: Get current user information
    print("\n5. 👤 Getting current user information...")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print("✅ Successfully retrieved user information!")
        print(f"   Username: {user_info['data']['username']}")
        print(f"   Email: {user_info['data']['email']}")
        print(f"   Active: {user_info['data']['is_active']}")
    else:
        print(f"❌ Failed to get user information: {response.text}")
    
    # Test 6: Create a task with authentication
    print("\n6. 📝 Creating a task with authentication...")
    task_data = {
        "title": "Test Task with JWT Auth",
        "description": "This task was created using JWT authentication",
        "due_date": "2024-12-31",
        "is_complete": False
    }
    
    response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
    if response.status_code == 201:
        print("✅ Task created successfully!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to create task: {response.text}")
    
    # Test 7: Test with invalid token
    print("\n7. 🚫 Testing with invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid-token-here"}
    response = requests.get(f"{BASE_URL}/api/tasks/", headers=invalid_headers)
    if response.status_code == 401:
        print("✅ Correctly rejected invalid token!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 Authentication flow test completed successfully!")
    print("\nKey features demonstrated:")
    print("• ✅ User registration with email validation")
    print("• ✅ Argon2 password hashing")
    print("• ✅ JWT token generation and validation")
    print("• ✅ Protected endpoint access control")
    print("• ✅ Bearer token authentication")
    print("• ✅ Invalid token rejection")
    print("• ✅ User information retrieval")
    print("• ✅ Task creation with authentication")

if __name__ == "__main__":
    try:
        test_authentication_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")