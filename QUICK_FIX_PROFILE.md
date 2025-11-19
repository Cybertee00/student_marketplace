# ⚡ Quick Fix: Create Profile Manually

## 🎯 **If Login Says "Invalid Credentials"**

The profile probably wasn't created. Here's how to fix it:

---

## 📋 **Step-by-Step:**

### **1. Get User ID from Authentication**

1. Go to **Supabase Dashboard → Authentication → Users**
2. Click on **`admin@studentmarketplace.com`**
3. **Copy the UUID** (the long ID at the top, like `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

### **2. Create Profile Row**

1. Go to **Table Editor → `profiles`**
2. Click **"Insert"** button (top right)
3. Click **"Insert row"**
4. Fill in these fields:
   - **id:** (Paste the UUID you copied)
   - **email:** `admin@studentmarketplace.com`
   - **username:** `admin`
   - **name:** `Admin`
   - **surname:** `User`
   - **phone:** `+27123456789`
5. Click **"Save"** (or press Enter)

### **3. Assign Admin Role**

1. Go to **Table Editor → `user_roles`**
2. Click **"Insert" → "Insert row"**
3. Fill in:
   - **user_id:** (Same UUID from step 1)
   - **role_id:** `1` (This is the admin role - check `roles` table to confirm)
4. Click **"Save"**

### **4. Try Login Again**

- **Email:** `admin@studentmarketplace.com`
- **Password:** `Admin123!@#`

---

**That should fix it!** ✅

