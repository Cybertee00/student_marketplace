# 🔧 Fix: Invalid API Key Error

## 🎯 **Problem**

Error: `AuthApiError: Invalid API key`

This happens because the `.env` file has wrong variable names. Vite requires `VITE_` prefix!

---

## ✅ **Solution**

The `.env` file in `admin/` folder needs to have variables with `VITE_` prefix.

### **Correct `.env` file:**

```env
VITE_SUPABASE_URL=https://kxqhklgknwgmehyyttzp.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjAzNDUsImV4cCI6MjA3ODk2MzQ1fQ.efpywMHQ-lb3HX27gxxkBuojDIytHrwasoJsiOB66m4
VITE_API_URL=https://student-marketplace-api.onrender.com
```

### **After Fixing:**

1. **Save the `.env` file**

2. **Restart the admin panel:**
   ```powershell
   # Stop the current server (Ctrl+C)
   # Then restart:
   cd admin
   npm run dev
   ```

3. **Try logging in again**

---

## ⚠️ **Important**

- ❌ Wrong: `SUPABASE_URL` (without VITE_)
- ✅ Correct: `VITE_SUPABASE_URL` (with VITE_)

Vite only exposes environment variables that start with `VITE_` to the frontend code!

---

**After fixing and restarting, login should work!** 🎯

