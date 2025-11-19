# 🚀 Create Test Data - Quick Guide

## 📋 **What This Does**

This script will create:
- ✅ **Admin user** (with admin role assigned)
- ✅ **End user** (regular user for testing)
- ✅ **5 sample products** (ready for testing)

---

## 🎯 **Quick Start**

### **Step 1: Navigate to Backend Directory**

```powershell
cd backend
```

### **Step 2: Activate Virtual Environment**

```powershell
# If you're in the backend directory
.\.venv\Scripts\Activate.ps1
```

### **Step 3: Run the Script**

```powershell
python create_test_data.py
```

---

## ✅ **What You'll Get**

After running the script, you'll have:

### **👑 Admin User:**
- **Email:** `admin@studentmarketplace.com`
- **Password:** `Admin123!@#`
- **Username:** `admin`
- **Phone:** `+27123456789`
- **Role:** Admin (automatically assigned)

### **👤 End User:**
- **Email:** `user@studentmarketplace.com`
- **Password:** `User123!@#`
- **Username:** `johndoe`
- **Phone:** `+27987654321`
- **Role:** Regular user

### **📦 5 Products:**
1. MacBook Pro 13-inch - R8,500.00
2. Calculus Textbook - 3rd Edition - R350.00
3. Wireless Mouse - Logitech - R450.00
4. Student Desk Chair - R600.00
5. Scientific Calculator - TI-84 - R800.00

---

## 📝 **After Running the Script**

### **1. Test Admin Panel Login:**
- Go to: `http://localhost:3001` (or your admin panel URL)
- Login with admin credentials
- You should see the 5 products

### **2. Test Flutter App Login:**
- Open Flutter app
- Login with end user credentials
- You should see the 5 products in the marketplace

### **3. Add Images to Products:**
- See `HOW_TO_ADD_IMAGES.md` for detailed instructions
- You can add images via:
  - Admin panel (recommended)
  - Supabase Storage dashboard
  - Flutter app

---

## ⚠️ **Troubleshooting**

### **Error: "Module not found"**
- Make sure you're in the `backend` directory
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### **Error: "User already exists"**
- The script will detect existing users and skip creation
- This is fine - it means users were already created

### **Error: "Connection failed"**
- Check your `.env` file has correct Supabase credentials
- Verify Supabase project is active
- Check internet connection

### **Products Not Showing:**
- Make sure products were created (check script output)
- Verify in Supabase Dashboard → Table Editor → products
- Check that `approved = true` in database

---

## 🎯 **Next Steps**

1. ✅ Run the script
2. ✅ Login to admin panel
3. ✅ Verify products are visible
4. ✅ Add images to products (see `HOW_TO_ADD_IMAGES.md`)
5. ✅ Test Flutter app login
6. ✅ Test product viewing in app

---

**That's it! You're ready to test your application!** 🎉

