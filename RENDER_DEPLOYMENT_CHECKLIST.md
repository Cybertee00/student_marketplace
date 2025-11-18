# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. **Environment Variables Setup**

#### **Required Environment Variables for Render:**

```env
# Supabase Configuration
SUPABASE_URL=https://kxqhklgknwgmehyyttzp.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjAzNDUsImV4cCI6MjA3ODk2MzQ1fQ.efpywMHQ-lb3HX27gxxkBuojDIytHrwasoJsiOB66m4
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzMyMDM0NSwiZXhwIjoyMDc4ODk2MzQ1fQ.Z01anPER4kcEo5jTpgYSgNeVriwk0fh5YF_fdXbpYks

# Database (Supabase PostgreSQL)
# ⚠️ IMPORTANT: Replace [YOUR-PASSWORD] with your actual Supabase database password
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres

# Storage Buckets
STORAGE_BUCKET_PRODUCTS=products
STORAGE_BUCKET_PROFILES=profiles

# Logging (disabled by default)
ENABLE_LOGGING=false

# Environment
DEBUG=false
ENVIRONMENT=production

# CORS Origins (comma-separated)
# Update with your actual frontend URLs after deployment
CORS_ORIGINS=https://your-service-name.onrender.com,http://localhost:3001,http://localhost:8000
```

**⚠️ Action Required:**
- [ ] Get your Supabase database password
- [ ] Update `DATABASE_URL` in Render environment variables with actual password
- [ ] Update `CORS_ORIGINS` with your actual frontend URLs after deployment

---

### 2. **Code Updates Needed**

#### **A. Update CORS Settings in `backend/main.py`**

**Current:** Uses `allow_origins=["*"]` (allows all origins)

**Needs to be:** Use environment variable for production

**Status:** ⚠️ **NEEDS UPDATE** - See below

#### **B. Verify All Environment Variables Are Read Correctly**

**Status:** ✅ **DONE** - All services read from environment variables

---

### 3. **Deployment Files**

#### **A. `backend/render.yaml`**
- ✅ **EXISTS** - Ready to use
- ✅ **CORRECT** - Uses `$PORT` variable

#### **B. `backend/Procfile`**
- ✅ **EXISTS** - Ready to use
- ✅ **CORRECT** - Uses `$PORT` variable

#### **C. `backend/requirements.txt`**
- ✅ **EXISTS** - Includes all dependencies including `supabase>=2.0.0`

---

### 4. **Git Repository Setup**

**Before deploying to Render:**
- [ ] Ensure all code changes are committed
- [ ] Push to GitHub repository
- [ ] Verify `.env` is in `.gitignore` (should NOT be committed)
- [ ] Verify sensitive keys are NOT in code

---

### 5. **Supabase Configuration**

**Verify in Supabase Dashboard:**
- [ ] Database is accessible (not paused)
- [ ] Storage buckets (`products` and `profiles`) are created
- [ ] Storage policies are configured
- [ ] RLS policies are enabled on all tables
- [ ] Database password is known (for `DATABASE_URL`)

---

### 6. **Testing Before Deployment**

**Local Testing:**
- [ ] Test backend runs locally with `.env` file
- [ ] Test authentication endpoints
- [ ] Test image upload endpoints
- [ ] Test database queries
- [ ] Verify Supabase connection works

---

## 📋 Render Deployment Steps

### **Step 1: Create Render Account**
- [ ] Sign up at [render.com](https://render.com)
- [ ] Connect GitHub account

### **Step 2: Create Web Service**
- [ ] Click "New +" → "Web Service"
- [ ] Connect your GitHub repository
- [ ] Select repository: `student_marketplace`
- [ ] Configure:
  - **Name:** `student-marketplace-api`
  - **Environment:** `Python 3`
  - **Region:** Choose closest to users
  - **Branch:** `main` (or your production branch)
  - **Root Directory:** `backend`

### **Step 3: Configure Build & Deploy**
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] **Auto-Deploy:** `Yes`

### **Step 4: Set Environment Variables**
- [ ] Add all environment variables from section 1 above
- [ ] Mark sensitive variables as **Secret**
- [ ] ⚠️ **CRITICAL:** Update `DATABASE_URL` with actual password

### **Step 5: Deploy**
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-5 minutes)
- [ ] Check logs for any errors
- [ ] Test health endpoint: `https://your-service-name.onrender.com/health`

### **Step 6: Update CORS After Deployment**
- [ ] Get your Render service URL
- [ ] Update `CORS_ORIGINS` in Render environment variables
- [ ] Update `backend/main.py` to use environment variable (see code update below)
- [ ] Redeploy

---

## 🔧 Code Updates Required

### **Update `backend/main.py` CORS Settings**

**Current Code:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Updated Code (use this):**
```python
import os

# Get CORS origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
# Clean up any whitespace
cors_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ Post-Deployment Checklist

### **After Deployment:**
- [ ] Test API health endpoint
- [ ] Test authentication (register/login)
- [ ] Test image upload
- [ ] Test database queries
- [ ] Update admin panel `.env` with Render URL
- [ ] Update Flutter app `app_constants.dart` with Render URL
- [ ] Test end-to-end flow

### **Update Client Applications:**

#### **Admin Panel (`admin/.env`):**
```env
VITE_API_URL=https://your-service-name.onrender.com
```

#### **Flutter App (`lib/constants/app_constants.dart`):**
Update `apiBaseUrl` getter to use Render URL in production.

---

## 🆘 Troubleshooting

### **Common Issues:**

1. **Build Fails:**
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility

2. **Service Won't Start:**
   - Check logs for errors
   - Verify `startCommand` uses `$PORT`
   - Check environment variables are set

3. **Database Connection Errors:**
   - Verify `DATABASE_URL` format is correct
   - Check password is correct
   - Verify Supabase database is not paused

4. **CORS Errors:**
   - Update `CORS_ORIGINS` with actual frontend URLs
   - Redeploy after updating

---

## 📝 Summary

### **What's Ready:**
✅ Render configuration files (`render.yaml`, `Procfile`)
✅ All Supabase services integrated
✅ Environment variables structure defined
✅ Requirements.txt includes all dependencies

### **What Needs to Be Done:**
⚠️ Update CORS settings in `main.py` (code provided above)
⚠️ Get Supabase database password
⚠️ Set environment variables in Render dashboard
⚠️ Update client app URLs after deployment

### **Estimated Time:**
- Code update: 5 minutes
- Render setup: 15-20 minutes
- Testing: 10-15 minutes
- **Total: ~30-40 minutes**

---

**Ready to deploy?** Follow the steps above and you'll be live on Render! 🚀

