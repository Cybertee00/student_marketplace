# 🔍 Verify All Connections - Testing Guide

## 🎯 **Goal**

Verify that your server, admin panel, and Flutter app are all properly connected and working together.

---

## ✅ **Test 1: Server (Render API) is Running**

### **Check 1.1: API Health Endpoint**

1. **Open browser** and go to:
   ```
   https://student-marketplace-api.onrender.com/health
   ```

2. **Expected Result:**
   ```json
   {
     "status": "healthy"
   }
   ```

3. **If you see this:** ✅ Server is running!

4. **If you get an error:** ❌ Server might be down or URL is wrong

---

### **Check 1.2: API Documentation**

1. **Go to:**
   ```
   https://student-marketplace-api.onrender.com/docs
   ```

2. **Expected Result:**
   - You should see the FastAPI Swagger documentation
   - You can see all available endpoints

3. **If you see this:** ✅ API is accessible!

---

### **Check 1.3: Test API Endpoint**

1. **Open browser console** (F12) or use a tool like Postman
2. **Make a test request:**
   ```javascript
   fetch('https://student-marketplace-api.onrender.com/')
     .then(r => r.json())
     .then(console.log)
   ```

3. **Expected Result:**
   ```json
   {
     "message": "Welcome to Student Marketplace API",
     "version": "1.0.0",
     "docs": "/docs"
   }
   ```

---

## ✅ **Test 2: Admin Panel → Server Connection**

### **Check 2.1: Admin Panel Environment Variables**

1. **Check `admin/.env` file exists:**
   ```powershell
   cd admin
   cat .env
   ```

2. **Verify these are set:**
   ```
   VITE_SUPABASE_URL=https://kxqhklgknwgmehyyttzp.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   VITE_API_URL=https://student-marketplace-api.onrender.com
   ```

3. **If missing:** Add them and restart admin panel

---

### **Check 2.2: Admin Panel Can Reach API**

1. **Start admin panel:**
   ```powershell
   cd admin
   npm run dev
   ```

2. **Open browser:** `http://localhost:3001`

3. **Open Developer Tools (F12) → Console tab**

4. **Try to login:**
   - Email: `admin@studentmarketplace.com`
   - Password: `Admin123!@#`

5. **Watch the Console:**
   - Look for API requests to `https://student-marketplace-api.onrender.com`
   - Check for errors (red text)

6. **Check Network Tab:**
   - Go to **Network** tab in DevTools
   - Try logging in again
   - Look for requests to your API URL
   - Check if they return `200 OK` or errors

---

### **Check 2.3: Test API Call from Admin Panel**

1. **Open browser console** on admin panel (F12)
2. **Run this test:**
   ```javascript
   fetch('https://student-marketplace-api.onrender.com/health')
     .then(r => r.json())
     .then(data => console.log('API Response:', data))
     .catch(err => console.error('API Error:', err))
   ```

3. **Expected Result:**
   ```
   API Response: {status: "healthy"}
   ```

4. **If you see this:** ✅ Admin panel can reach API!

---

## ✅ **Test 3: Supabase Connection**

### **Check 3.1: Supabase Auth Works**

1. **Open browser console** on admin panel
2. **Run this test:**
   ```javascript
   // Check if Supabase is initialized
   console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL)
   ```

3. **Or test login directly:**
   - Try logging in with admin credentials
   - Check console for Supabase auth errors

---

### **Check 3.2: Supabase Database Connection**

1. **Go to Supabase Dashboard → Table Editor**
2. **Check these tables exist:**
   - ✅ `profiles`
   - ✅ `products`
   - ✅ `roles`
   - ✅ `user_roles`

3. **Verify admin user exists:**
   - Go to `profiles` table
   - You should see `admin@studentmarketplace.com`

---

## ✅ **Test 4: Flutter App → Server Connection**

### **Check 4.1: Flutter App API URL**

1. **Open:** `lib/constants/app_constants.dart`
2. **Verify:**
   ```dart
   static String get apiBaseUrl {
     return 'https://student-marketplace-api.onrender.com';
   }
   ```

---

### **Check 4.2: Test API from Flutter**

1. **Run Flutter app**
2. **Try to login:**
   - Email: `user@studentmarketplace.com` (or admin)
   - Password: `User123!@#` (or `Admin123!@#`)

3. **Check for errors:**
   - Look at console output
   - Check for network errors
   - Verify login succeeds

---

### **Check 4.3: Flutter App → Supabase**

1. **Check `lib/main.dart`:**
   - Verify Supabase is initialized with correct URL and key

2. **Test Supabase connection:**
   - Try registering a new user
   - Check if it creates profile in Supabase

---

## ✅ **Test 5: End-to-End Flow**

### **Complete Test Flow:**

1. **✅ Server is running:**
   - Visit: `https://student-marketplace-api.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. **✅ Admin Panel can login:**
   - Go to: `http://localhost:3001`
   - Login with: `admin@studentmarketplace.com` / `Admin123!@#`
   - Should redirect to dashboard

3. **✅ Admin Panel can fetch data:**
   - After login, check if you can see products/users
   - Check browser console for API calls

4. **✅ Flutter App can login:**
   - Open Flutter app
   - Login with: `user@studentmarketplace.com` / `User123!@#`
   - Should show home screen

5. **✅ Flutter App can fetch products:**
   - After login, check if products are displayed
   - Check for network errors

---

## 🔧 **Troubleshooting Common Issues**

### **Issue 1: "Network Error" or "Failed to fetch"**

**Causes:**
- API URL is wrong
- Server is down
- CORS issue

**Fix:**
- Check `VITE_API_URL` in `admin/.env`
- Verify server is running: `https://student-marketplace-api.onrender.com/health`
- Check Render dashboard to see if service is active

---

### **Issue 2: "Invalid credentials"**

**Causes:**
- Profile doesn't exist in Supabase
- Wrong password
- User not confirmed

**Fix:**
- Check `profiles` table in Supabase
- Verify user exists in Authentication → Users
- Check "Email Confirmed" is ✅

---

### **Issue 3: "CORS Error"**

**Causes:**
- Server CORS not configured
- Wrong origin

**Fix:**
- Check `CORS_ORIGINS` in Render environment variables
- Should include: `http://localhost:3001`

---

### **Issue 4: "API Timeout"**

**Causes:**
- Server is sleeping (Render free tier)
- Network issue

**Fix:**
- First request might be slow (waking up server)
- Wait 30 seconds and try again
- Check Render logs

---

## 📊 **Quick Checklist**

- [ ] Server health endpoint works: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Admin panel `.env` file configured
- [ ] Admin panel can reach API (check Network tab)
- [ ] Admin panel can login
- [ ] Supabase `profiles` table has admin user
- [ ] Flutter app API URL is correct
- [ ] Flutter app can login
- [ ] Flutter app can fetch products

---

## 🎯 **Quick Test Script**

Run this in browser console on admin panel:

```javascript
// Test 1: API Health
fetch('https://student-marketplace-api.onrender.com/health')
  .then(r => r.json())
  .then(data => {
    console.log('✅ API Health:', data);
    return fetch('https://student-marketplace-api.onrender.com/');
  })
  .then(r => r.json())
  .then(data => {
    console.log('✅ API Root:', data);
  })
  .catch(err => {
    console.error('❌ API Error:', err);
  });

// Test 2: Supabase Config
console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL);
console.log('API URL:', import.meta.env.VITE_API_URL);
```

---

**Run these tests to verify everything is connected!** 🎯

