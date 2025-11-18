#!/usr/bin/env python3
"""
Script to register a test user for the Student Marketplace app.
Run this from the project root directory.
"""

import requests
import json
import sys

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Test user details
TEST_USER = {
    "name": "Test",
    "surname": "User",
    "email": "testuser@example.com",
    "phone": "1234567890",
    "username": "testuser",
    "password": "test123456"
}

def register_user():
    """Register a new user via the API."""
    url = f"{API_BASE_URL}/auth/register"
    
    print("Registering test user...")
    print(f"Email: {TEST_USER['email']}")
    print(f"Username: {TEST_USER['username']}")
    print(f"Phone: {TEST_USER['phone']}")
    print()
    
    try:
        response = requests.post(
            url,
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print("SUCCESS: User registered successfully!")
            print()
            print("User Details:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Name: {user_data.get('name')} {user_data.get('surname')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email Verified: {user_data.get('is_email_verified')}")
            print()
            print("Login Credentials:")
            print(f"   Username/Email/Phone: {TEST_USER['username']} (or {TEST_USER['email']} or {TEST_USER['phone']})")
            print(f"   Password: {TEST_USER['password']}")
            print()
            print("Note: Email verification may be required. Check backend console for verification token.")
            return True
        else:
            error_data = response.json()
            error_msg = error_data.get('detail', 'Unknown error')
            print(f"ERROR: Registration failed: {error_msg}")
            
            if "already exists" in error_msg.lower():
                print()
                print("The user already exists. You can:")
                print("   1. Use the existing credentials to login")
                print("   2. Change the email/username/phone in this script and try again")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the backend API.")
        print(f"   Make sure the backend is running on {API_BASE_URL}")
        print("   Start it with: cd backend && uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Student Marketplace - Test User Registration")
    print("=" * 50)
    print()
    
    success = register_user()
    
    print()
    print("=" * 50)
    
    if success:
        print("SUCCESS: Registration complete! You can now login to the app.")
    else:
        print("ERROR: Registration failed. Please check the error above.")
        sys.exit(1)

