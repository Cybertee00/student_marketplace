# OAuth2 Google Drive Setup Guide

## 🚨 **Why OAuth2 Instead of Service Account?**

The previous setup failed because **Service Accounts don't have storage quota** in Google Drive. We need to use **OAuth2** instead, which allows your personal Google account to authorize the app to access your Drive.

## 📋 **Step-by-Step Setup**

### **Step 1: Create OAuth2 Credentials**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `student-marketplace-personal`
3. Go to **"APIs & Services"** → **"Credentials"**
4. Click **"Create Credentials"** → **"OAuth client ID"**
5. Choose **"Desktop application"**
6. Enter name: `Student Marketplace Desktop`
7. Click **"Create"**
8. Download the JSON file and rename it to `oauth-credentials.json`
9. Place it in your `backend` directory

### **Step 2: Test OAuth2 Setup**

Run the test script:
```bash
python test_oauth_setup.py
```

This will:
- Open your browser for Google authentication
- Ask you to log in and authorize the app
- Save the authentication token for future use

### **Step 3: Run Migration**

Once OAuth2 is set up, run the migration:
```bash
python migrate_images_oauth.py
```

## 🔑 **What Happens During OAuth2 Setup?**

1. **First Run**: Opens browser, asks you to log in and authorize
2. **Subsequent Runs**: Uses saved token automatically
3. **Token Expiry**: Automatically refreshes when needed

## 📁 **File Structure After Setup**

```
backend/
├── oauth-credentials.json    # OAuth2 credentials (from Google Cloud Console)
├── token.json               # Authentication token (auto-generated)
├── oauth_google_drive_service.py  # OAuth2 service
└── migrate_images_oauth.py  # OAuth2 migration script
```

## ✅ **Benefits of OAuth2**

- ✅ Uses your personal Google Drive storage
- ✅ No storage quota limitations
- ✅ Works with personal folders
- ✅ Automatic token refresh
- ✅ Secure authentication

## 🚀 **Ready to Proceed?**

Once you've downloaded the OAuth2 credentials file (`oauth-credentials.json`) and placed it in the backend directory, we can test the setup!
