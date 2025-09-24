# 🚀 Quick Start Testing Guide

## ⚡ **Get the Student Marketplace Running in 5 Minutes!**

### **Step 1: Start the Backend**
```bash
cd backend
uvicorn main:app --reload
```
**Expected:** Server starts at `http://localhost:8000`
**Test:** Visit `http://localhost:8000/docs` to see the API documentation

### **Step 2: Test the Flutter App**
1. **Open Flutter app** in your emulator/device
2. **Register a new user** with your email
3. **Check backend console** for 2FA verification code
4. **Enter the code** to verify your account
5. **Login** and explore the app

### **Step 3: Test the Admin Panel**
```bash
cd admin
npm start
```
**Expected:** Admin panel opens at `http://localhost:3000`
**Login:** Use admin credentials to access the dashboard

---

## 🧪 **Quick Test Scenarios**

### **Test 1: User Registration & 2FA**
1. Open Flutter app
2. Click "Register"
3. Fill in details (use real email)
4. Check backend console for verification code
5. Enter code and verify account
6. **Result:** ✅ Account created and verified

### **Test 2: Product Browsing**
1. Login to Flutter app
2. Browse products on home screen
3. Search for specific items
4. Add items to favorites
5. **Result:** ✅ Products display correctly

### **Test 3: Shopping Cart**
1. Add products to cart
2. Modify quantities
3. Remove items
4. View cart total
5. **Result:** ✅ Cart functions properly

### **Test 4: Checkout Process**
1. Proceed to checkout
2. Select payment method
3. Complete order
4. **Result:** ✅ Order created successfully

### **Test 5: Admin Panel**
1. Login to admin panel
2. View dashboard
3. Check recent orders
4. Manage products
5. **Result:** ✅ Admin functions work

---

## 🔍 **What to Look For**

### **✅ Working Features:**
- User registration and login
- Product browsing and search
- Shopping cart functionality
- Order placement
- Admin dashboard
- User management
- Product management

### **⚠️ Expected Limitations (Development Mode):**
- 2FA codes appear in backend console (not real emails)
- Payment processing is simulated
- Database is local (PostgreSQL)

---

## 🎯 **Success Indicators**

**The app is working correctly if:**
1. ✅ Backend starts without errors
2. ✅ Flutter app connects to backend
3. ✅ User registration works
4. ✅ 2FA verification completes
5. ✅ Products display correctly
6. ✅ Cart functions properly
7. ✅ Orders can be placed
8. ✅ Admin panel loads and functions

---

## 🚨 **If Something Doesn't Work**

### **Backend Issues:**
- Check if PostgreSQL is running
- Verify database connection in `config.py`
- Check console for error messages

### **Flutter App Issues:**
- Verify API base URL in `lib/constants/app_constants.dart`
- Check if backend is running on correct port
- Look for network error messages

### **Admin Panel Issues:**
- Ensure backend is running
- Check if `npm install` was run
- Verify API endpoints in admin configuration

---

## 🎉 **Ready to Test!**

**Your Student Marketplace is ready for testing!** 

**Start with the backend, then test the Flutter app, and finally check the admin panel. Everything should work smoothly in development mode.**

**Once you're satisfied with the functionality, we can address the production deployment requirements outlined in the main summary document.**

**Happy testing! 🚀**

