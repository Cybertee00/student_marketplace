# 👥 Create Test Users Manually in Supabase

## 🎯 **Goal**

Create admin and end user accounts so you can login to both the admin panel and Flutter app.

---

## 📋 **Step-by-Step: Create Users in Supabase Dashboard**

### **Step 1: Create Admin User**

1. **Go to Supabase Dashboard:**
   - Open: https://supabase.com/dashboard
   - Select your project

2. **Navigate to Authentication:**
   - Click **"Authentication"** in the left sidebar
   - Click **"Users"** tab

3. **Add New User:**
   - Click **"Add User"** button (top right)
   - Click **"Create new user"**

4. **Fill in Admin User Details:**
   - **Email:** `admin@studentmarketplace.com`
   - **Password:** `Admin123!@#`
   - **Auto Confirm User:** ✅ (check this box - IMPORTANT!)
   - **User Metadata (JSON):** Click to expand, then paste:
     ```json
     {
       "name": "Admin",
       "surname": "User",
       "username": "admin",
       "phone": "+27123456789"
     }
     ```

5. **Click "Create User"**

6. **Verify Profile Created:**
   - Go to **"Table Editor"** → **"profiles"** table
   - You should see a new row with the admin user's data
   - If not, the trigger might need fixing (see below)

---

### **Step 2: Create End User**

1. **Still in Authentication → Users:**
   - Click **"Add User"** again
   - Click **"Create new user"**

2. **Fill in End User Details:**
   - **Email:** `user@studentmarketplace.com`
   - **Password:** `User123!@#`
   - **Auto Confirm User:** ✅ (check this box - IMPORTANT!)
   - **User Metadata (JSON):** Click to expand the field, then paste this EXACT text (copy everything between the curly braces):
     ```json
     {
       "name": "John",
       "surname": "Doe",
       "username": "johndoe",
       "phone": "+27987654321"
     }
     ```
   
   **💡 Tip:** In Supabase Dashboard, the User Metadata field might look like a text box. Just paste the JSON directly (you can include or exclude the ```json markers - both work).

3. **Click "Create User"**

4. **Verify Profile Created:**
   - Check **"Table Editor"** → **"profiles"** table
   - You should see both users now

---

### **Step 3: Fix Profile if Missing**

**If the profile wasn't created automatically:**

1. **Go to Table Editor → profiles**
2. **Click "Insert" → "Insert row"**
3. **Fill in:**
   - **id:** (Copy the UUID from Authentication → Users)
   - **email:** `admin@studentmarketplace.com` (or `user@studentmarketplace.com`)
   - **username:** `admin` (or `johndoe`)
   - **name:** `Admin` (or `John`)
   - **surname:** `User` (or `Doe`)
   - **phone:** `+27123456789` (or `+27987654321`)

4. **Click "Save"**

---

### **Step 4: Assign Admin Role**

1. **Go to Table Editor → user_roles**
2. **Click "Insert" → "Insert row"**
3. **Fill in:**
   - **user_id:** (Copy the UUID of admin user from profiles table)
   - **role_id:** `1` (This should be the admin role - check roles table to confirm)

4. **Click "Save"**

---

### **Step 5: Test Login**

**Admin Panel:**
- Go to: `http://localhost:3001` (or your admin panel URL)
- Login with:
  - Email: `admin@studentmarketplace.com`
  - Password: `Admin123!@#`

**Flutter App:**
- Open the app
- Login with:
  - Email: `user@studentmarketplace.com`
  - Password: `User123!@#`

---

## 🔧 **If Profile Trigger Still Not Working**

Run the SQL fix:

1. **Go to SQL Editor**
2. **Copy and paste the contents of `backend/fix_profile_trigger.sql`**
3. **Click "Run"**

This will update the trigger to handle all metadata fields properly.

---

## ✅ **After Creating Users**

Once users are created, you can:

1. **Run the test data script** to create products:
   ```powershell
   cd D:\PJs\student_marketplace\backend
   .\.venv\Scripts\python.exe create_test_data.py
   ```
   The script will detect existing users and create 5 products.

2. **Test everything:**
   - Login to admin panel
   - Login to Flutter app
   - View products
   - Add images to products

---

**That's it! You'll have working login credentials for both admin and end user.** 🎉

