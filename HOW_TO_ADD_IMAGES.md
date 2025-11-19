# 📸 How to Add Images to Products

## 🎯 **Overview**

After creating products, you need to add images. Here's how to do it:

---

## 📋 **Method 1: Via Admin Panel (Recommended)**

### **Steps:**

1. **Login to Admin Panel:**
   - Go to: `http://localhost:3001` (or your admin panel URL)
   - Login with admin credentials

2. **Go to Products Page:**
   - Click on "Products" in the sidebar
   - Find the product you want to add images to
   - Click "Edit" button

3. **Upload Images:**
   - Click "Upload Images" or "Add Images" button
   - Select image files from your computer
   - Images will be uploaded to Supabase Storage automatically
   - Click "Save" to update the product

4. **Images are Now Stored:**
   - Images go to: `Supabase Storage → products bucket → {user-id}/` folder
   - URLs are saved in the product's `images` field in the database

---

## 📋 **Method 2: Via Flutter App**

### **Steps:**

1. **Login to Flutter App:**
   - Use end user credentials
   - Go to "Sell" or "My Products" section

2. **Edit Product:**
   - Find your product
   - Click edit
   - Add images using the image picker
   - Save

---

## 📋 **Method 3: Manual Image Upload (For Testing)**

### **Using Supabase Dashboard:**

1. **Prepare Images:**
   - Have image files ready on your computer
   - Supported formats: JPG, PNG, GIF, WEBP
   - Recommended size: Under 5MB each

2. **Upload to Supabase Storage:**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Select your project
   - Click **"Storage"** → **"Buckets"**
   - Click on **"products"** bucket
   - Navigate to the user's folder (or create one)
   - Click **"Upload file"**
   - Select your image
   - Copy the public URL

3. **Update Product in Database:**
   - Go to **"Table Editor"** → **"products"** table
   - Find your product
   - Edit the `images` field
   - Add the public URL (or array of URLs)
   - Save

---

## 📋 **Method 4: Using API Directly**

### **Steps:**

1. **Get Upload URL:**
   ```bash
   POST https://student-marketplace-api.onrender.com/images/upload-url
   Headers: Authorization: Bearer {your-token}
   Body: {
     "bucket": "products",
     "filename": "product-image.jpg"
   }
   ```

2. **Upload Image:**
   ```bash
   PUT {signed_url_from_step_1}
   Body: {image file bytes}
   Content-Type: image/jpeg
   ```

3. **Update Product:**
   ```bash
   PUT https://student-marketplace-api.onrender.com/admin/products/{product_id}
   Headers: Authorization: Bearer {admin-token}
   Body: {
     "images": ["https://kxqhklgknwgmehyyttzp.supabase.co/storage/v1/object/public/products/..."]
   }
   ```

---

## 🖼️ **Image Requirements**

- **Formats:** JPG, PNG, GIF, WEBP
- **Max Size:** 10MB per image
- **Recommended:** 
  - Resolution: 800x600 or higher
  - Format: JPG or PNG
  - Size: Under 2MB for faster loading

---

## 📝 **Quick Test Images**

For testing, you can use:
- Placeholder images: https://via.placeholder.com/800x600
- Free stock images: Unsplash, Pexels
- Your own product photos

**Example placeholder URL:**
```
https://via.placeholder.com/800x600/2563EB/FFFFFF?text=Product+Image
```

You can add this directly to the product's `images` array in the database for quick testing.

---

## ✅ **After Adding Images**

1. **Verify in Supabase Storage:**
   - Check that images appear in the `products` bucket
   - Verify the file paths

2. **Verify in Database:**
   - Check that product `images` field has the URLs
   - URLs should start with: `https://kxqhklgknwgmehyyttzp.supabase.co/storage/...`

3. **Test in App:**
   - View products in Flutter app
   - Images should display correctly
   - Check admin panel product list

---

**For the 5 test products, you can add images using any of these methods!** 🎯

