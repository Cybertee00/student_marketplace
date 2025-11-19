# 🔧 Fix Profile Creation Trigger

## 🎯 **Problem**

The database trigger that automatically creates profiles when users are created in `auth.users` is not working correctly. It only handles `id`, `email`, and `username`, but doesn't handle `name`, `surname`, and `phone` from user metadata.

## ✅ **Solution**

Run the SQL script to update the trigger function.

---

## 📋 **Step-by-Step Instructions**

### **Step 1: Open Supabase SQL Editor**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Click **"SQL Editor"** in the left sidebar

### **Step 2: Run the Fix SQL**

1. Click **"New query"** button
2. Copy the contents of `backend/fix_profile_trigger.sql`
3. Paste it into the SQL editor
4. Click **"Run"** (or press Ctrl+Enter)

### **Step 3: Verify**

You should see:
- ✅ "Success. No rows returned" or similar success message
- ✅ A query result showing the trigger details

### **Step 4: Test User Creation**

After fixing the trigger, try running the test data script again:

```powershell
cd D:\PJs\student_marketplace\backend
.\.venv\Scripts\python.exe create_test_data.py
```

---

## 🔍 **What This Does**

1. **Drops** the old trigger and function
2. **Creates** a new function that handles:
   - `id` (from auth.users)
   - `email` (from auth.users)
   - `username` (from metadata or email)
   - `name` (from metadata)
   - `surname` (from metadata)
   - `phone` (from metadata)
3. **Recreates** the trigger on `auth.users`
4. **Adds** `ON CONFLICT DO NOTHING` to prevent errors if profile already exists

---

## ⚠️ **If You Still Get Errors**

If user creation still fails after fixing the trigger:

1. **Check the trigger exists:**
   ```sql
   SELECT * FROM information_schema.triggers 
   WHERE trigger_name = 'on_auth_user_created';
   ```

2. **Check the function exists:**
   ```sql
   SELECT * FROM pg_proc 
   WHERE proname = 'handle_new_user';
   ```

3. **Manually create users via Supabase Dashboard:**
   - Go to Authentication → Users → Add User
   - Create users manually
   - Then run the script again (it will detect existing users)

---

**After fixing the trigger, user creation should work!** 🎉

