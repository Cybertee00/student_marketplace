# 🚀 Render Deployment - Step-by-Step Guide

## ✅ Current Status
- ✅ Code pushed to GitHub
- ✅ Supabase configured
- ✅ Backend ready for deployment

---

## 📋 Step-by-Step Instructions

### **Step 1: Get Your Supabase Database Password**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings** → **Database**
4. Scroll to **Connection string** section
5. Click **URI** tab
6. Copy the connection string
7. **Extract the password** from the connection string:
   ```
   postgresql://postgres:[PASSWORD-HERE]@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres
   ```
   The password is between `postgres:` and `@`

**⚠️ Save this password - you'll need it in Step 4!**

---

### **Step 2: Create Render Account**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Sign up or log in (you can use GitHub to sign in)
3. Verify your email if required

---

### **Step 3: Create New Web Service**

1. In Render Dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub account (if not already connected)
4. Select repository: **`Cybertee00/student_marketplace`**
5. Click **"Connect"**

---

### **Step 4: Configure Service Settings**

#### **Basic Settings:**
- **Name:** `student-marketplace-api` (or your preferred name)
- **Region:** Choose closest to your users (e.g., `Oregon (US West)`)
- **Branch:** `main`
- **Root Directory:** `backend` ⚠️ **IMPORTANT: Set this to `backend`**
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### **Advanced Settings:**
- **Auto-Deploy:** `Yes` (deploys on every push to main)

---

### **Step 5: Set Environment Variables**

**📖 For detailed step-by-step instructions, see: `RENDER_ENV_VARS_QUICK_REFERENCE.md`**

#### **How to Add Variables:**

1. In the Render service setup page, scroll down to **"Environment Variables"** section
2. You'll see two input fields: **"NAME_OF_VARIABLE"** and **"value"**
3. For each variable below:
   - Click in the **"NAME_OF_VARIABLE"** field → Enter the variable name
   - Click in the **"value"** field → Enter the value
   - The variable is automatically saved when you click outside or press Enter
4. Click **"Add Environment Variable"** button to add the next one
5. Repeat until all 10 variables are added

#### **Required Variables (Add These 10):**

**1. SUPABASE_URL**
- **NAME field:** `SUPABASE_URL`
- **value field:** `https://kxqhklgknwgmehyyttzp.supabase.co`

**2. SUPABASE_KEY**
- **NAME field:** `SUPABASE_KEY`
- **value field:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjAzNDUsImV4cCI6MjA3ODk2MzQ1fQ.efpywMHQ-lb3HX27gxxkBuojDIytHrwasoJsiOB66m4`

**3. SUPABASE_SERVICE_KEY**
- **NAME field:** `SUPABASE_SERVICE_KEY`
- **value field:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzMyMDM0NSwiZXhwIjoyMDc4ODk2MzQ1fQ.Z01anPER4kcEo5jTpgYSgNeVriwk0fh5YF_fdXbpYks`

**4. DATABASE_URL** ⚠️ **IMPORTANT - You Need Your Password!**
- **NAME field:** `DATABASE_URL`
- **value field:** `postgresql://postgres:[YOUR-PASSWORD]@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres`
- **⚠️ Replace `[YOUR-PASSWORD]` with your actual Supabase database password from Step 1!**

**5. STORAGE_BUCKET_PRODUCTS**
- **NAME field:** `STORAGE_BUCKET_PRODUCTS`
- **value field:** `products`

**6. STORAGE_BUCKET_PROFILES**
- **NAME field:** `STORAGE_BUCKET_PROFILES`
- **value field:** `profiles`

**7. ENABLE_LOGGING**
- **NAME field:** `ENABLE_LOGGING`
- **value field:** `false`

**8. DEBUG**
- **NAME field:** `DEBUG`
- **value field:** `false`

**9. ENVIRONMENT**
- **NAME field:** `ENVIRONMENT`
- **value field:** `production`

**10. CORS_ORIGINS** ⚠️ **Can Update Later**
- **NAME field:** `CORS_ORIGINS`
- **value field:** `https://your-service-name.onrender.com,http://localhost:3001,http://localhost:8000`
- **⚠️ You can update this after deployment (Step 8) with your actual service URL**

#### **Visual Example:**

After adding variables, you'll see rows like:
```
NAME_OF_VARIABLE          value
─────────────────────────────────────────────────────────
SUPABASE_URL             https://kxqhklgknwgmehyyttzp.supabase.co
SUPABASE_KEY             eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL             postgresql://postgres:YOUR-PASSWORD@...
... (and 7 more)
```

**💡 Tip:** See `RENDER_ENV_VARS_QUICK_REFERENCE.md` for a complete copy-paste ready list!

---

### **Step 6: Deploy**

1. Click **"Create Web Service"**
2. Render will start building your service
3. Watch the build logs for any errors
4. First deployment takes 5-10 minutes

---

### **Step 7: Get Your Service URL**

1. After deployment succeeds, you'll see your service URL
2. It will look like: `https://student-marketplace-api.onrender.com`
3. **Copy this URL** - you'll need it!

---

### **Step 8: Update CORS_ORIGINS**

1. Go back to your Render service
2. Click **"Environment"** tab
3. Find `CORS_ORIGINS` variable
4. Click **"Edit"**
5. Update it with your actual service URL:
   ```
   https://your-actual-service-name.onrender.com,http://localhost:3001,http://localhost:8000
   ```
6. Click **"Save Changes"**
7. Service will automatically redeploy

---

### **Step 9: Test Your Deployment**

1. Visit your service URL: `https://your-service-name.onrender.com`
2. You should see: `{"message": "Welcome to Student Marketplace API", ...}`
3. Test health endpoint: `https://your-service-name.onrender.com/health`
4. Test API docs: `https://your-service-name.onrender.com/docs`

---

### **Step 10: Update Client Apps**

After deployment, update your client apps to use the new API URL:

#### **Admin Panel (`admin/.env`):**
```env
VITE_API_URL=https://your-service-name.onrender.com
```

#### **Flutter App (`lib/constants/app_constants.dart`):**
```dart
static const String apiBaseUrl = 'https://your-service-name.onrender.com';
```

---

## 🎯 Quick Checklist

- [ ] Got Supabase database password
- [ ] Created Render account
- [ ] Created new Web Service
- [ ] Set Root Directory to `backend`
- [ ] Added all environment variables
- [ ] Deployed service
- [ ] Got service URL
- [ ] Updated CORS_ORIGINS with service URL
- [ ] Tested deployment
- [ ] Updated client app URLs

---

## ⚠️ Common Issues

### **Build Fails:**
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Root Directory is set to `backend`

### **Service Won't Start:**
- Check start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Verify all environment variables are set
- Check logs for specific errors

### **Database Connection Fails:**
- Verify `DATABASE_URL` has correct password
- Check Supabase database is not paused
- Ensure IP is not blocked (Render IPs should be allowed by default)

### **CORS Errors:**
- Update `CORS_ORIGINS` with your actual frontend URLs
- Include both `http://` and `https://` if needed
- Restart service after updating CORS_ORIGINS

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Render Status: https://status.render.com
- Check build logs in Render dashboard for specific errors

---

**Ready to deploy? Start with Step 1!** 🚀

