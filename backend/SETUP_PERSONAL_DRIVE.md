# 🏠 Setting Up Personal Google Drive for Student Marketplace

## 🎯 **Why Use Personal Drive Instead of Company Drive?**

### **Problems with Company Drive:**
- ❌ IT policies may block API access
- ❌ Company owns your data
- ❌ Can revoke access anytime
- ❌ May violate company policies
- ❌ Limited control over permissions

### **Benefits of Personal Drive:**
- ✅ Full control over your data
- ✅ No company restrictions
- ✅ You own the storage
- ✅ Complete API access
- ✅ No compliance issues

## 🚀 **Quick Setup with Personal Google Account**

### **Step 1: Create Personal Google Account**
1. Go to https://accounts.google.com/signup
2. Create account: `yourname.studentmarketplace@gmail.com`
3. Verify email and set up 2FA

### **Step 2: Create Project Folders**
1. Go to https://drive.google.com/
2. Create folder: **"Student Marketplace - Products"**
3. Create folder: **"Student Marketplace - Profiles"**
4. Note the folder IDs from the URLs

### **Step 3: Update Folder IDs**
Update these in `google_drive_service.py`:
```python
# Replace with your new folder IDs
PRODUCTS_FOLDER_ID = "your_new_products_folder_id"
PROFILE_PICTURES_FOLDER_ID = "your_new_profiles_folder_id"
```

### **Step 4: Continue with Google Cloud Setup**
- Use the same personal Google account
- Create Google Cloud Project
- Enable Google Drive API
- Create service account
- Share folders with service account

## 💰 **Cost Consideration**
- **Personal Google Drive**: 15GB free (plenty for images)
- **Google Cloud Project**: Free
- **Google Drive API**: Free (1 billion requests/day)

## 🔒 **Security Benefits**
- Your data stays private
- No company oversight
- Full control over access
- Can backup/export anytime
