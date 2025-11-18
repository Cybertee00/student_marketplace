# 🔐 Where to Put Supabase Database Password

## Step 1: Get Your Database Password from Supabase

### **Option A: If you set a password when creating the project**
- Use the password you set during project creation
- If you forgot it, you'll need to reset it (see Option B)

### **Option B: Get/Reset Password from Supabase Dashboard**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `kxqhklgknwgmehyyttzp`
3. Go to **Settings** → **Database**
4. Scroll down to **Connection string** section
5. You'll see:
   - **Connection string** (URI format)
   - **Connection pooling** (Session mode)
   - **Direct connection** (Transaction mode)

6. **To get the password:**
   - If you see the connection string, it will look like:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres
     ```
   - The password is between `postgres:` and `@`
   
7. **If password is hidden or you need to reset it:**
   - Click **"Reset database password"** button
   - Set a new password (save it securely!)
   - The connection string will update with the new password

---

## Step 2: Put Password in Local `.env` File

**File Location:** `backend/.env`

**Current line (needs updating):**
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres
```

**What to do:**
1. Open `backend/.env` file
2. Find the line with `DATABASE_URL`
3. Replace `[YOUR-PASSWORD]` with your actual Supabase database password

**Example:**
```env
# If your password is "MySecurePassword123!"
DATABASE_URL=postgresql://postgres:MySecurePassword123!@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres
```

**⚠️ Important Notes:**
- If your password contains special characters, they might need URL encoding:
  - `@` becomes `%40`
  - `#` becomes `%23`
  - `$` becomes `%24`
  - `%` becomes `%25`
  - `&` becomes `%26`
  - `+` becomes `%2B`
  - `=` becomes `%3D`
  - `?` becomes `%3F`
  - ` ` (space) becomes `%20`

**Or better:** Copy the **full connection string** directly from Supabase Dashboard (it will already be URL-encoded correctly)

---

## Step 3: Put Password in Render Dashboard (When Deploying)

### **When creating the Render service:**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create a new **Web Service**
3. After configuring build settings, go to **Environment** tab
4. Add environment variable:
   - **Key:** `DATABASE_URL`
   - **Value:** The full connection string with your password

### **How to get the exact value:**

**Method 1: Copy from Supabase Dashboard**
1. Go to Supabase Dashboard → Settings → Database
2. Under **Connection string**, select **URI**
3. Copy the **entire connection string** (it includes the password)
4. Paste it as the value for `DATABASE_URL` in Render

**Method 2: Manually construct it**
```
postgresql://postgres:YOUR-PASSWORD-HERE@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres
```

Replace `YOUR-PASSWORD-HERE` with your actual password.

### **In Render Dashboard, it will look like:**

```
Environment Variables:
┌─────────────────────┬─────────────────────────────────────────────────────────────┐
│ Key                 │ Value                                                       │
├─────────────────────┼─────────────────────────────────────────────────────────────┤
│ DATABASE_URL        │ postgresql://postgres:YourPassword@db.kxqhklgknwgmehyyttzp. │
│                     │ supabase.co:5432/postgres                                   │
│ SUPABASE_URL        │ https://kxqhklgknwgmehyyttzp.supabase.co                   │
│ SUPABASE_KEY        │ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...                    │
│ SUPABASE_SERVICE_KEY│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...                    │
│ ...                 │ ...                                                         │
└─────────────────────┴─────────────────────────────────────────────────────────────┘
```

**⚠️ Security Tip:**
- Mark `DATABASE_URL` as **Secret** in Render (click the lock icon)
- This hides the password in the dashboard

---

## Quick Reference

### **Local Development (`backend/.env`):**
```env
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres
```

### **Render Dashboard (Environment Variables):**
- **Key:** `DATABASE_URL`
- **Value:** `postgresql://postgres:YOUR-PASSWORD@db.kxqhklgknwgmehyyttzp.supabase.co:5432/postgres`
- **Mark as Secret:** ✅ Yes

---

## Troubleshooting

### **"Connection refused" or "Authentication failed"**
- ✅ Check password is correct (no typos)
- ✅ Check password is URL-encoded if it has special characters
- ✅ Verify you're using the password from Supabase Dashboard (not a different password)

### **"Password contains invalid characters"**
- URL-encode special characters (see list above)
- Or copy the connection string directly from Supabase Dashboard

### **"Can't find .env file"**
- Make sure you're editing `backend/.env` (not `.env.example`)
- The file should be in the `backend` folder

---

## Summary

1. **Get password:** Supabase Dashboard → Settings → Database → Connection string
2. **Local:** Put in `backend/.env` file, replace `[YOUR-PASSWORD]` in `DATABASE_URL`
3. **Render:** Put in Render Dashboard → Environment Variables → `DATABASE_URL`

That's it! 🎉

