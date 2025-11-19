# 🔍 Troubleshoot Login Issues

## 🎯 **Problem: "Invalid Credentials" When Logging In**

If you're getting "Invalid credentials" when trying to login, check these:

---

## ✅ **Step 1: Verify User Was Created Correctly**

### **Check in Supabase Dashboard:**

1. **Go to Authentication → Users**
   - You should see `admin@studentmarketplace.com`
   - Check that the email is correct (no typos)
   - Check that "Email Confirmed" is ✅ (green checkmark)

2. **Go to Table Editor → profiles**
   - You should see a row with the admin user's data
   - Check that:
     - `email` = `admin@studentmarketplace.com`
     - `username` = `admin`
     - `name` = `Admin`
     - `surname` = `User`

**If profile is missing:**
- The trigger didn't work
- Manually create the profile (see Step 2 below)

---

## ✅ **Step 2: Create Profile Manually (If Missing)**

If the profile wasn't created automatically:

1. **Get the User ID:**
   - Go to Authentication → Users
   - Click on `admin@studentmarketplace.com`
   - Copy the **UUID** (it's a long string like `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

2. **Create Profile:**
   - Go to Table Editor → `profiles`
   - Click "Insert" → "Insert row"
   - Fill in:
     - **id:** (Paste the UUID from step 1)
     - **email:** `admin@studentmarketplace.com`
     - **username:** `admin`
     - **name:** `Admin`
     - **surname:** `User`
     - **phone:** `+27123456789`
   - Click "Save"

---

## ✅ **Step 3: Assign Admin Role**

1. **Get Admin User ID:**
   - Go to Table Editor → `profiles`
   - Find the admin user row
   - Copy the **id** (UUID)

2. **Get Admin Role ID:**
   - Go to Table Editor → `roles`
   - Find the row where `name` = `admin`
   - Copy the **id** (should be `1`)

3. **Assign Role:**
   - Go to Table Editor → `user_roles`
   - Click "Insert" → "Insert row"
   - Fill in:
     - **user_id:** (Paste admin user UUID)
     - **role_id:** `1` (or the admin role ID from step 2)
   - Click "Save"

---

## ✅ **Step 4: Verify Login Credentials**

**For Admin Panel:**
- **Email:** `admin@studentmarketplace.com`
- **Password:** `Admin123!@#`

**Try these variations if it doesn't work:**
- Username: `admin` (instead of email)
- Phone: `+27123456789` (instead of email)

---

## ✅ **Step 5: Check Admin Panel Configuration**

1. **Check `.env` file:**
   - Open `admin/.env`
   - Verify:
     ```
     VITE_SUPABASE_URL=https://kxqhklgknwgmehyyttzp.supabase.co
     VITE_SUPABASE_ANON_KEY=your-anon-key-here
     VITE_API_URL=https://student-marketplace-api.onrender.com
     ```

2. **Restart Admin Panel:**
   ```powershell
   cd admin
   npm run dev
   ```

---

## ✅ **Step 6: Test Direct Supabase Login**

To verify the user can login to Supabase:

1. **Go to Supabase Dashboard → Authentication → Users**
2. **Click on `admin@studentmarketplace.com`**
3. **Try to reset password or verify the user is active**

---

## ✅ **Step 7: Check Browser Console**

1. **Open Admin Panel** in browser
2. **Open Developer Tools** (F12)
3. **Go to Console tab**
4. **Try to login**
5. **Check for error messages**

Common errors:
- `Invalid API key` → Check `.env` file
- `User not found` → Profile doesn't exist
- `Invalid credentials` → Wrong password or email

---

## 🔧 **Quick Fix: Reset Password**

If nothing works, try resetting the password:

1. **Go to Supabase Dashboard → Authentication → Users**
2. **Click on `admin@studentmarketplace.com`**
3. **Click "Send password reset email"** OR
4. **Manually update password:**
   - Scroll down to "Update user"
   - Change password to: `Admin123!@#`
   - Click "Update"

---

## 📝 **Common Issues:**

1. **Profile doesn't exist** → Create it manually (Step 2)
2. **Admin role not assigned** → Assign it (Step 3)
3. **Wrong credentials** → Double-check email/password
4. **User not confirmed** → Make sure "Auto Confirm User" was checked
5. **Wrong Supabase URL/Key** → Check `.env` file

---

**After fixing, try logging in again!** 🎯

