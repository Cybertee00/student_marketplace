# 🚀 Simple Google Drive Setup

## 🤔 Why Do I Need Google Cloud Project?

You already have Google Drive storage, but your **app needs permission** to access it automatically.

### **What You Have:** ✅
- Google Drive account
- Folders for products and profile pictures
- Manual upload capability

### **What You Need:** ❌
- Google Cloud Project (free)
- API credentials (free)
- Service account (free)

## 📝 **Quick 5-Step Setup** (10 minutes)

### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name: `student-marketplace`
4. Click "Create"

### Step 2: Enable Google Drive API
1. In your project, go to "APIs & Services" → "Library"
2. Search "Google Drive API"
3. Click "Enable"

### Step 3: Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: `marketplace-bot`
4. Click "Create and Continue" → "Done"

### Step 4: Download Credentials
1. Click on your service account email
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key" → "JSON"
4. Download the file
5. Rename it to `google-credentials.json`
6. Put it in your `backend/` folder

### Step 5: Share Your Folders
1. Open your Google Drive folders
2. Click "Share" on each folder
3. Add the service account email (from the JSON file)
4. Set permission to "Editor"

## ✅ **That's It!**

Once you do this, your app can automatically:
- Upload images to Google Drive
- Access your existing images
- Manage files programmatically

## 🆓 **Cost:** 
- Google Cloud Project: FREE
- Google Drive API: FREE (up to 1 billion requests/day)
- Your existing Google Drive storage: Same as before

## 🚨 **Important:**
You're not creating new storage - you're just giving your app permission to use your existing Google Drive!
