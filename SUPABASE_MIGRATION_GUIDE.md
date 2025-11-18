# 🚀 Supabase Migration Guide
## Complete Step-by-Step Guide to Migrate Student Marketplace to Supabase

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Supabase Project Setup](#step-1-supabase-project-setup)
4. [Step 2: Database Schema Migration](#step-2-database-schema-migration)
5. [Step 3: Supabase Storage Setup](#step-3-supabase-storage-setup)
6. [Step 4: Supabase Authentication Setup](#step-4-supabase-authentication-setup)
7. [Step 5: Backend Migration (FastAPI)](#step-5-backend-migration-fastapi)
8. [Step 6: Admin Panel Migration](#step-6-admin-panel-migration)
9. [Step 7: Flutter App Migration](#step-7-flutter-app-migration)
10. [Step 8: Data Migration](#step-8-data-migration)
11. [Step 9: Testing & Verification](#step-9-testing--verification)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### **What We're Migrating To:**

- **Authentication:** Supabase Auth (email/password + OAuth providers)
- **Database:** Supabase PostgreSQL (managed, with real-time subscriptions)
- **Image Storage:** Supabase Storage (public buckets, direct client uploads)
- **Backend:** FastAPI for business logic only (no file streaming)
- **Logs:** Optional logging table (disabled by default)

### **Benefits:**
- ✅ Managed PostgreSQL database (Supabase)
- ✅ Built-in authentication with OAuth (Supabase Auth)
- ✅ Direct client-to-storage uploads (no server bandwidth)
- ✅ FastAPI backend hosted on Render (easy deployment)
- ✅ Backend connects to Supabase (database + API)
- ✅ Real-time subscriptions
- ✅ Automatic backups
- ✅ Row Level Security (RLS)
- ✅ Scalable storage

---

## 📦 Prerequisites

### **Required Accounts:**
- [ ] Supabase account (free tier available)
- [ ] GitHub account (for OAuth, optional)

### **Required Tools:**
- [ ] Python 3.8+ with pip
- [ ] Node.js 18+
- [ ] Flutter SDK 3.8.1+
- [ ] PostgreSQL client (psql) - optional, for direct DB access
- [ ] Supabase CLI (optional, for local development)

### **Install Supabase CLI (Optional):**
```bash
# Windows (using Scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# macOS
brew install supabase/tap/supabase

# Or download from: https://github.com/supabase/cli/releases
```

---

## 🔧 Step 1: Supabase Project Setup

**Goal:** Create a Supabase account and set up your project with all necessary credentials.

**Time:** ~10 minutes

---

### **1.1 Create Supabase Account**

**What you're doing:** Creating a free Supabase account to host your database and services.

**Step-by-step:**

1. **Open Supabase Website:**
   - Go to [https://supabase.com](https://supabase.com) in your browser
   - You'll see the Supabase homepage

2. **Start Sign Up:**
   - Look for a button that says **"Start your project"** or **"Sign up"** (usually in the top right)
   - Click on it

3. **Choose Sign Up Method:**
   - **Option 1 (Recommended):** Sign up with **GitHub**
     - Click "Continue with GitHub"
     - Authorize Supabase to access your GitHub account
     - This is faster and more secure
   - **Option 2:** Sign up with **Email**
     - Enter your email address
     - Create a password
     - Verify your email (check your inbox)

4. **Complete Account Setup:**
   - Fill in any additional information if prompted
   - Accept terms and conditions
   - You should now be logged into your Supabase dashboard

**✅ You're done when:** You can see the Supabase dashboard (you might see "New Project" or an empty projects list).

**Next Step:** Create your first project (Step 1.2).

---

### **1.2 Create New Project**

**What you're doing:** Creating a new Supabase project that will host your database, authentication, and storage.

**Step-by-step:**

1. **Start New Project:**
   - In your Supabase dashboard, look for a button that says **"New Project"** or **"Create new project"**
   - It's usually a big green button or in the top right corner
   - Click on it

2. **Fill in Project Details:**
   - **Organization:** If this is your first project, you might need to create an organization first (just use your name or "My Projects")
   - **Name:** Type `student-marketplace` (or any name you prefer)
   - **Database Password:** 
     - ⚠️ **IMPORTANT:** Create a STRONG password (at least 12 characters, mix of letters, numbers, symbols)
     - 📝 **SAVE THIS PASSWORD!** You'll need it to connect to the database
     - Write it down in a secure place (you can't recover it easily)
   - **Region:** 
     - Choose the region closest to you or your users
     - Examples: `US East`, `EU West`, `Asia Pacific`
     - This affects latency (how fast your database responds)
   - **Pricing Plan:** 
     - Select **"Free"** (this is fine for development and testing)
     - You can upgrade later if needed

3. **Create the Project:**
   - Review all your settings
   - Click **"Create new project"** button (usually at the bottom)
   - ⏳ **Wait 2-3 minutes** - Supabase is setting up your database and services
   - You'll see a loading screen with progress

4. **Project Ready:**
   - When ready, you'll be automatically taken to your project dashboard
   - You should see your project name at the top
   - The left sidebar will show various sections (Table Editor, SQL Editor, Authentication, Storage, etc.)

**✅ You're done when:** 
- Your project is created and loaded
- You can see the project dashboard
- The left sidebar menu is visible

**⚠️ Important Reminders:**
- Save your database password somewhere secure
- Don't close this tab - you'll need it for the next steps

**Next Step:** Get your project credentials (Step 1.3).

### **1.3 Get Project Credentials**

**What you're doing:** Getting all the keys and connection strings you'll need to connect your applications to Supabase.

**Step-by-step:**

#### **Part A: Get API Keys**

1. **Navigate to API Settings:**
   - In your Supabase dashboard, look at the left sidebar
   - Click **"Settings"** (gear icon ⚙️)
   - Click **"API"** in the submenu

2. **Find and Copy Project URL:**
   - Look for **"Project URL"** section (usually at the top)
   - You'll see something like: `https://abcdefghijklmnop.supabase.co`
   - **Copy this entire URL** - you'll need it later
   - 📝 **Save it somewhere safe** (like a text file or notes app)

3. **Find and Copy anon/public key:**
   - Look for **"Project API keys"** section
   - Find the key labeled **"anon"** or **"public"**
   - It will be a long string starting with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Click the **copy icon** (📋) next to it to copy
   - ⚠️ **This key is safe to use in frontend code** (Flutter app, admin panel)
   - 📝 **Save it somewhere safe**

4. **Find and Copy service_role key:**
   - In the same **"Project API keys"** section
   - Find the key labeled **"service_role"** or **"service_role secret"**
   - It will also be a long string
   - Click the **copy icon** (📋) next to it to copy
   - ⚠️ **⚠️ KEEP THIS SECRET!** Never commit this to Git or use it in frontend code
   - ⚠️ **Only use this in your backend (FastAPI)**
   - 📝 **Save it somewhere safe and secure**

#### **Part B: Get Database Connection String**

5. **Navigate to Database Settings:**
   - Still in Settings, click **"Database"** in the submenu (or go back to Settings → Database)

6. **Find Connection String:**
   - Scroll down to find **"Connection string"** or **"Connection pooling"** section
   - You'll see different connection options (URI, JDBC, etc.)
   - Look for the tab or option that says **"URI"**

7. **Copy the Connection String:**
   - Click on the **"URI"** tab
   - You'll see a connection string like:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres
     ```
   - **⚠️ Important:** Replace `[YOUR-PASSWORD]` with your actual database password
   - Your password is the one you set when creating the project (in Step 1.2)
   - If you forgot it, you can reset it in Settings → Database → Reset database password
   - 📝 **Copy the full connection string with your password** and save it securely

**✅ Checklist - Make sure you have:**
- [ ] Project URL (e.g., `https://xxxxx.supabase.co`)
- [ ] anon/public key (long string starting with `eyJ...`)
- [ ] service_role key (long string starting with `eyJ...`)
- [ ] Database connection string with password (format: `postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres`)

**💡 Pro Tip:** Create a file called `supabase-credentials.txt` (don't commit to Git!) and save all these values there for easy reference.

**Next Step:** Continue to Step 1.4 to verify APIs are enabled.

### **1.4 Enable Required APIs**

**What you're doing:** Verifying that the necessary APIs are enabled in your Supabase project. These are usually enabled by default, but we'll check to make sure.

**Step-by-step:**

1. **Navigate to API Settings:**
   - In your Supabase dashboard (you should already be logged in)
   - Look at the left sidebar menu
   - Click on **"Settings"** (it has a gear icon ⚙️)
   - In the Settings submenu, click on **"API"**

2. **What you'll see:**
   - You'll see a page with various API settings and keys
   - At the top, you'll see sections like:
     - **Project URL**
     - **anon/public key**
     - **service_role key**
   - Scroll down to find API settings

3. **Check API Status:**
   - Look for sections or toggles related to:
     - **REST API** - Should be enabled (this is always on by default)
     - **Realtime** - Should be enabled (this is always on by default)
     - **Storage API** - Should be enabled (this is always on by default)

4. **Important Note:**
   - ⚠️ **These APIs are enabled by default** in Supabase
   - You don't need to toggle anything on/off
   - If you don't see specific toggles, that's fine - they're already enabled
   - The main purpose of this step is to familiarize yourself with where these settings are

5. **What to do if you can't find these settings:**
   - Don't worry! If you can't find specific toggles, the APIs are already enabled
   - Continue to the next step
   - The APIs will work automatically when you use them

**✅ You're done with this step when:**
- You've navigated to Settings → API
- You've seen the API keys page
- You understand that the APIs are already enabled (no action needed)

**🎉 Congratulations!** You've completed Step 1. You now have:
- ✅ Supabase account created
- ✅ Project created
- ✅ All credentials saved
- ✅ APIs verified (they're enabled by default)

**Next Step:** Move to **Step 2: Database Schema Migration** to create your database tables.

---

## 🗄️ Step 2: Database Schema Migration

### **2.1 Create Database Tables**

**What you're doing:** Running SQL commands to create all the tables (users, products, orders, etc.) in your Supabase database.

**Step-by-step:**

1. **Open SQL Editor:**
   - In your Supabase dashboard, look at the **left sidebar menu**
   - Find and click on **"SQL Editor"** (it has a database icon 📊 or looks like `</>`)
   - You'll see a new page with a code editor

2. **Create a New Query:**
   - Click the **"New query"** button (usually top right, green button)
   - Or you'll see an empty editor ready for SQL code
   - The editor should be blank/empty

3. **Copy the SQL Code:**
   - Scroll down below these instructions
   - You'll see a large SQL code block starting with:
     ```sql
     -- Enable UUID extension
     CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
     ```
   - **Select ALL the SQL code** (from `CREATE EXTENSION` to the very end - it's a long block)
   - **Copy it** (Ctrl+C on Windows, Cmd+C on Mac)

4. **Paste into SQL Editor:**
   - Go back to your Supabase SQL Editor tab
   - Click in the editor area (the big text box)
   - **Paste the SQL code** (Ctrl+V or Cmd+V)
   - You should see all the SQL code in the editor (it will be quite long - that's normal!)

5. **Run the SQL:**
   - Look for a **"Run"** button (usually at the bottom right of the editor, or press Ctrl+Enter)
   - Click **"Run"** or press **Ctrl+Enter** (Windows) or **Cmd+Enter** (Mac)
   - ⏳ Wait 10-30 seconds - Supabase is creating all your tables

6. **Check for Success:**
   - You should see a message like:
     - ✅ "Success. No rows returned"
     - ✅ "Query executed successfully"
     - ✅ Green checkmark
   - If you see errors, scroll down to see what went wrong
   - Common issues:
     - If it says "already exists" - that's okay, some tables might already exist
     - If it says "permission denied" - make sure you're using the correct project
     - If you see red error messages, read them carefully

7. **Verify Tables Were Created:**
   - In the left sidebar, click **"Table Editor"** (database icon 📊)
   - You should see a list of tables on the left side
   - Look for these tables (scroll if needed):
     - ✅ profiles
     - ✅ products
     - ✅ orders
     - ✅ order_items
     - ✅ cart_items
     - ✅ favorites
     - ✅ reviews
     - ✅ messages
     - ✅ notifications
     - ✅ roles
     - ✅ user_roles
     - ✅ revenue
     - ✅ logs
   - If you see these tables, ✅ **Success!**

**✅ You're done when:**
- SQL code ran without critical errors (warnings are okay)
- You can see all the tables listed in Table Editor
- No red error messages blocking the creation

**⚠️ Troubleshooting:**
- **"Extension already exists"** - This is fine, continue
- **"Table already exists"** - Some tables might already exist, that's okay
- **"Permission denied"** - Make sure you're in the correct project
- **Can't find SQL Editor** - Look in the left sidebar, it might be under a menu

**Next Step:** Continue to Step 2.2 to verify all tables are created correctly.

---

**Now, copy and paste this SQL code into your SQL Editor:**

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS TABLE (Supabase Auth handles auth.users)
-- ============================================
-- Note: Supabase creates auth.users automatically
-- We'll create a public.profiles table for additional user data

CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(50) UNIQUE,
    username VARCHAR(100) UNIQUE NOT NULL,
    profile_img TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_phone_verified BOOLEAN DEFAULT FALSE
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policies for profiles
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    USING (true);

-- ============================================
-- ROLES & PERMISSIONS (RBAC) - Created early for product policies
-- ============================================
CREATE TABLE public.roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.user_roles (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- Enable RLS for roles and user_roles
ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- Policies for roles (readable by everyone, modifiable by admins only)
CREATE POLICY "Roles are viewable by everyone"
    ON public.roles FOR SELECT
    USING (true);

CREATE POLICY "Only admins can manage roles"
    ON public.roles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policies for user_roles
CREATE POLICY "Users can view own roles"
    ON public.user_roles FOR SELECT
    USING (auth.uid() = user_id OR EXISTS (
        SELECT 1 FROM public.user_roles ur
        JOIN public.roles r ON ur.role_id = r.id
        WHERE ur.user_id = auth.uid() AND r.name = 'admin'
    ));

CREATE POLICY "Only admins can manage user roles"
    ON public.user_roles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Insert default roles
INSERT INTO public.roles (name, description) VALUES
    ('admin', 'Full system access'),
    ('user', 'Standard marketplace access'),
    ('seller', 'Can create and manage products');

-- ============================================
-- PRODUCTS TABLE
-- ============================================
CREATE TABLE public.products (
    id SERIAL PRIMARY KEY,
    seller_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    faculty VARCHAR(100),
    condition VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    initial_stock INTEGER DEFAULT 0,
    sold_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    is_out_of_stock BOOLEAN DEFAULT FALSE,
    approved BOOLEAN DEFAULT FALSE,
    discontinued BOOLEAN DEFAULT FALSE,
    created_via VARCHAR(50) DEFAULT 'flutter',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_stock_update TIMESTAMP WITH TIME ZONE
);

-- Product images (stored as JSON array of Supabase Storage URLs)
-- Images will be stored in Supabase Storage, URLs stored here
ALTER TABLE public.products ADD COLUMN images JSONB DEFAULT '[]'::jsonb;

-- Indexes
CREATE INDEX idx_products_seller ON public.products(seller_id);
CREATE INDEX idx_products_category ON public.products(category);
CREATE INDEX idx_products_approved ON public.products(approved);
CREATE INDEX idx_products_created_via ON public.products(created_via);

-- Enable RLS
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

-- Policies for products
CREATE POLICY "Products are viewable by everyone"
    ON public.products FOR SELECT
    USING (approved = true AND discontinued = false);

CREATE POLICY "Sellers can manage their own products"
    ON public.products FOR ALL
    USING (auth.uid() = seller_id);

CREATE POLICY "Admins can manage all products"
    ON public.products FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- ============================================
-- ORDERS TABLE
-- ============================================
CREATE TABLE public.orders (
    id SERIAL PRIMARY KEY,
    buyer_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES public.products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Enable RLS
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own orders"
    ON public.orders FOR SELECT
    USING (auth.uid() = buyer_id);

CREATE POLICY "Users can create own orders"
    ON public.orders FOR INSERT
    WITH CHECK (auth.uid() = buyer_id);

-- ============================================
-- CART TABLE
-- ============================================
CREATE TABLE public.cart_items (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Enable RLS
ALTER TABLE public.cart_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own cart"
    ON public.cart_items FOR ALL
    USING (auth.uid() = user_id);

-- ============================================
-- FAVORITES TABLE
-- ============================================
CREATE TABLE public.favorites (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Enable RLS
ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own favorites"
    ON public.favorites FOR ALL
    USING (auth.uid() = user_id);

-- ============================================
-- REVIEWS TABLE
-- ============================================
CREATE TABLE public.reviews (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Enable RLS
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Reviews are viewable by everyone"
    ON public.reviews FOR SELECT
    USING (true);

CREATE POLICY "Users can create own reviews"
    ON public.reviews FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- MESSAGES TABLE
-- ============================================
CREATE TABLE public.messages (
    id SERIAL PRIMARY KEY,
    sender_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    conversation_id VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    is_important BOOLEAN DEFAULT FALSE,
    parent_message_id INTEGER REFERENCES public.messages(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own messages"
    ON public.messages FOR SELECT
    USING (auth.uid() = sender_id OR auth.uid() = receiver_id);

CREATE POLICY "Users can send messages"
    ON public.messages FOR INSERT
    WITH CHECK (auth.uid() = sender_id);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE public.notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notifications"
    ON public.notifications FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================
-- REVENUE TABLE (Admin)
-- ============================================
CREATE TABLE public.revenue (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES public.orders(id),
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for revenue
ALTER TABLE public.revenue ENABLE ROW LEVEL SECURITY;

-- Only admins can access revenue data
CREATE POLICY "Only admins can access revenue"
    ON public.revenue FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- ============================================
-- LOGS TABLE (Optional, disabled by default)
-- ============================================
CREATE TABLE public.logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    user_id UUID REFERENCES public.profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_level ON public.logs(level);
CREATE INDEX idx_logs_created_at ON public.logs(created_at);

-- Enable RLS for logs
ALTER TABLE public.logs ENABLE ROW LEVEL SECURITY;

-- Only admins can view logs, system can write (via service role)
CREATE POLICY "Only admins can view logs"
    ON public.logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Allow inserts (for logging service - will use service role key)
-- Note: Service role key bypasses RLS, so this policy is for authenticated users
CREATE POLICY "System can write logs"
    ON public.logs FOR INSERT
    WITH CHECK (true);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to automatically create profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, username)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON public.products
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON public.orders
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON public.messages
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

---

### **2.2 Fix "Unrestricted" Warning (If You Already Ran SQL)**

**If you see "Unrestricted" warnings on `logs`, `revenue`, `roles`, or `user_roles` tables**, OR **if you get "relation already exists" errors**, run this SQL to add the missing RLS policies:

**⚠️ Important:** This SQL only adds RLS policies. It won't try to create tables that already exist, so it's safe to run even if you've already created the tables.

```sql
-- ============================================
-- ADD RLS POLICIES FOR EXISTING TABLES
-- This is safe to run even if tables already exist
-- ============================================

-- Enable RLS for roles and user_roles (if not already enabled)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'roles'
    ) THEN
        RAISE NOTICE 'Table roles does not exist, skipping...';
    ELSE
        ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS enabled for roles table';
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'user_roles'
    ) THEN
        RAISE NOTICE 'Table user_roles does not exist, skipping...';
    ELSE
        ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS enabled for user_roles table';
    END IF;
END $$;

-- Policies for roles (drop if exists, then create)
DROP POLICY IF EXISTS "Roles are viewable by everyone" ON public.roles;
CREATE POLICY "Roles are viewable by everyone"
    ON public.roles FOR SELECT
    USING (true);

DROP POLICY IF EXISTS "Only admins can manage roles" ON public.roles;
CREATE POLICY "Only admins can manage roles"
    ON public.roles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Policies for user_roles
DROP POLICY IF EXISTS "Users can view own roles" ON public.user_roles;
CREATE POLICY "Users can view own roles"
    ON public.user_roles FOR SELECT
    USING (auth.uid() = user_id OR EXISTS (
        SELECT 1 FROM public.user_roles ur
        JOIN public.roles r ON ur.role_id = r.id
        WHERE ur.user_id = auth.uid() AND r.name = 'admin'
    ));

DROP POLICY IF EXISTS "Only admins can manage user roles" ON public.user_roles;
CREATE POLICY "Only admins can manage user roles"
    ON public.user_roles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Enable RLS for revenue
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'revenue'
    ) THEN
        ALTER TABLE public.revenue ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS enabled for revenue table';
    END IF;
END $$;

DROP POLICY IF EXISTS "Only admins can access revenue" ON public.revenue;
CREATE POLICY "Only admins can access revenue"
    ON public.revenue FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Enable RLS for logs
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'logs'
    ) THEN
        ALTER TABLE public.logs ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS enabled for logs table';
    END IF;
END $$;

DROP POLICY IF EXISTS "Only admins can view logs" ON public.logs;
CREATE POLICY "Only admins can view logs"
    ON public.logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.user_roles ur
            JOIN public.roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

DROP POLICY IF EXISTS "System can write logs" ON public.logs;
CREATE POLICY "System can write logs"
    ON public.logs FOR INSERT
    WITH CHECK (true);
```

**✅ What this does:**
- Checks if tables exist before enabling RLS
- Drops existing policies if they exist (to avoid conflicts)
- Creates the RLS policies safely
- Won't error if tables don't exist

**After running this:**
- Refresh your Table Editor
- The "Unrestricted" warnings should disappear
- All tables will have proper security policies

### **2.2 Verify Tables Created**

1. Go to **Table Editor** in Supabase dashboard
2. Verify all tables are created:
   - ✅ profiles
   - ✅ products
   - ✅ orders
   - ✅ order_items
   - ✅ cart_items
   - ✅ favorites
   - ✅ reviews
   - ✅ messages
   - ✅ notifications
   - ✅ roles
   - ✅ user_roles
   - ✅ revenue
   - ✅ logs

---

## 📦 Step 3: Supabase Storage Setup

### **3.1 Create Storage Buckets**

1. Go to **Storage** in Supabase dashboard
2. Click **New bucket**

#### **Create Products Bucket:**
- **Name:** `products`
- **Public bucket:** ✅ **Enable** (check this!)
- **File size limit:** 10 MB (or as needed)
- **Allowed MIME types:** `image/jpeg,image/png,image/gif,image/webp`
- Click **Create bucket**

#### **Create Profiles Bucket:**
- **Name:** `profiles`
- **Public bucket:** ✅ **Enable** (check this!)
- **File size limit:** 5 MB
- **Allowed MIME types:** `image/jpeg,image/png,image/gif,image/webp`
- Click **Create bucket**

### **3.2 Configure Storage Policies**

**What you're doing:** Setting up security rules (policies) so users can upload, view, and manage images in your storage buckets.

**Why this is important:** Without policies, no one can upload or access images. These policies control who can do what with your storage.

**Time:** ~10 minutes

**Understanding Storage Policies:**

There are two ways to write storage policies in Supabase:

1. **Bucket-Level Policies (What we're using):**
   - Policies are written for the `storage.objects` table
   - Each policy checks which bucket it applies to using `bucket_id = 'bucket-name'`
   - ✅ **Easier to manage** - all policies in one place
   - ✅ **Recommended approach** - simpler and cleaner

2. **Storage Schema Table Policies (Advanced):**
   - Policies written directly on `storage.buckets` or `storage.objects` tables
   - More granular control but more complex
   - ⚠️ **Not needed for most use cases**

**We're using Method 1 (Bucket-Level)** because it's simpler and works perfectly for your needs.

---

#### **Method 1: Using SQL Editor (Recommended - Easier)**

This is the easiest way. We'll use the SQL Editor to create all policies at once.

**Step-by-step:**

1. **Open SQL Editor:**
   - In your Supabase dashboard, click **"SQL Editor"** in the left sidebar
   - Click **"New query"** button (top right)

2. **Copy the SQL Code:**
   - Scroll down below these instructions
   - You'll see SQL code for both buckets
   - **Select ALL the SQL code** (from the first `CREATE POLICY` to the last one)
   - **Copy it** (Ctrl+C or Cmd+C)

3. **Paste and Run:**
   - Go back to your SQL Editor
   - **Paste the SQL code** (Ctrl+V or Cmd+V)
   - Click **"Run"** button (or press Ctrl+Enter)
   - ⏳ Wait a few seconds

4. **Check for Success:**
   - You should see: ✅ "Success" or "Query executed successfully"
   - If you see errors, check that your bucket names match (`products` and `profiles`)

5. **Verify Policies Were Created:**
   - Go to **Storage** in the left sidebar
   - Click on **"Policies"** tab (at the top)
   - You should see policies listed for both buckets
   - If you see policies, ✅ **Success!**

**✅ You're done when:** You see policies listed in Storage → Policies.

---

#### **Method 2: Using Storage UI (Alternative)**

If you prefer using the UI instead of SQL:

1. **Go to Storage Policies:**
   - Click **"Storage"** in left sidebar
   - Click **"Policies"** tab at the top
   - You'll see your buckets listed

2. **For Each Bucket:**
   - Click on the bucket name (e.g., `products`)
   - Click **"New Policy"** button
   - Choose **"Create a policy from scratch"** or use a template
   - Fill in the policy details (see SQL below for what each policy should do)
   - Click **"Save"**
   - Repeat for each policy

**⚠️ Note:** Method 1 (SQL) is faster and less error-prone. Use Method 2 only if you prefer the UI.

---

#### **SQL Code for Storage Policies**

**Copy and paste this entire block into SQL Editor:**

```sql
-- ============================================
-- STORAGE POLICIES FOR PRODUCTS BUCKET
-- ============================================

-- Policy 1: Allow authenticated users to upload product images
CREATE POLICY "Authenticated users can upload products"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'products');

-- Policy 2: Allow everyone (public) to view product images
CREATE POLICY "Public can read products"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'products');

-- Policy 3: Allow users to update their own product images
-- (Users can only update files in folders named with their user ID)
CREATE POLICY "Users can update own product images"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'products' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Policy 4: Allow users to delete their own product images
-- (Users can only delete files in folders named with their user ID)
CREATE POLICY "Users can delete own product images"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'products' AND auth.uid()::text = (storage.foldername(name))[1]);

-- ============================================
-- STORAGE POLICIES FOR PROFILES BUCKET
-- ============================================

-- Policy 1: Allow authenticated users to upload profile pictures
CREATE POLICY "Authenticated users can upload profiles"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'profiles');

-- Policy 2: Allow everyone (public) to view profile pictures
CREATE POLICY "Public can read profiles"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profiles');

-- Policy 3: Allow users to update their own profile picture
-- (Users can only update files in folders named with their user ID)
CREATE POLICY "Users can update own profile picture"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'profiles' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Policy 4: Allow users to delete their own profile picture
-- (Users can only delete files in folders named with their user ID)
CREATE POLICY "Users can delete own profile picture"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'profiles' AND auth.uid()::text = (storage.foldername(name))[1]);
```

---

#### **What Each Policy Does:**

**For Products Bucket:**
- ✅ **Upload Policy:** Logged-in users can upload product images
- ✅ **Read Policy:** Anyone can view product images (public access)
- ✅ **Update Policy:** Users can only update images they uploaded (in their own folder)
- ✅ **Delete Policy:** Users can only delete images they uploaded (in their own folder)

**For Profiles Bucket:**
- ✅ **Upload Policy:** Logged-in users can upload profile pictures
- ✅ **Read Policy:** Anyone can view profile pictures (public access)
- ✅ **Update Policy:** Users can only update their own profile picture
- ✅ **Delete Policy:** Users can only delete their own profile picture

**How Folder Security Works:**
- When users upload images, they're stored in folders like: `{user_id}/filename.jpg`
- The policy checks if the folder name matches the user's ID
- This ensures users can only modify their own files

---

#### **Troubleshooting:**

**"Policy already exists" error:**
- If you see this, the policy was already created
- You can either:
  - Skip that policy (it's already there)
  - Or add `DROP POLICY IF EXISTS "Policy Name" ON storage.objects;` before creating it

**"Bucket does not exist" error:**
- Make sure you created the buckets in Step 3.1
- Check that bucket names are exactly `products` and `profiles` (lowercase, no spaces)

**Can't see policies after creating:**
- Refresh the Storage → Policies page
- Make sure you're looking at the correct bucket

**Policies not working:**
- Verify buckets are set to "Public" (Step 3.1)
- Check that you're logged in when testing uploads
- Verify bucket names match exactly in the policies

---

**✅ You're done when:**
- All 8 policies are created (4 for products, 4 for profiles)
- You can see them listed in Storage → Policies
- No error messages

**Next Step:** Continue to Step 3.3 to learn about storage URLs.

### **3.3 Get Storage URLs**

Storage URLs will be:
```
https://your-project.supabase.co/storage/v1/object/public/products/{filename}
https://your-project.supabase.co/storage/v1/object/public/profiles/{filename}
```

---

## 🔐 Step 4: Supabase Authentication Setup

### **4.1 Configure Email Auth**

1. Go to **Authentication** → **Providers**
2. Click on **Email**
3. Enable:
   - ✅ **Enable email provider**
   - ✅ **Confirm email** (recommended for production)
   - ✅ **Secure email change** (recommended)
4. Configure email templates (optional)
5. Click **Save**

### **4.2 Configure OAuth Providers (Optional)**

#### **GitHub OAuth:**
1. Go to **Authentication** → **Providers**
2. Click **GitHub**
3. Enable GitHub provider
4. Create GitHub OAuth App:
   - Go to GitHub → Settings → Developer settings → OAuth Apps
   - Click "New OAuth App"
   - **Application name:** Student Marketplace
   - **Homepage URL:** Your app URL
   - **Authorization callback URL:** `https://your-project.supabase.co/auth/v1/callback`
   - Copy **Client ID** and **Client Secret**
5. Paste into Supabase GitHub provider settings
6. Click **Save**

#### **Google OAuth (Optional):**
1. Similar process with Google Cloud Console
2. Use callback URL: `https://your-project.supabase.co/auth/v1/callback`

### **4.3 Configure Auth Settings**

1. Go to **Authentication** → **Settings**
2. Configure:
   - **Site URL:** Your frontend URL
   - **Redirect URLs:** Add your app URLs
   - **JWT expiry:** 3600 (1 hour) or as needed
   - **Refresh token expiry:** 604800 (7 days)

---

## 🐍 Step 5: Backend Migration (FastAPI)

### **5.1 Install Supabase Python Client**

```bash
cd backend
pip install supabase python-dotenv
```

### **5.2 Create Supabase Configuration**

Create `backend/supabase_config.py`:

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # anon/public key
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service_role key (server-side only)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service role client (for admin operations)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
```

### **5.3 Update Environment Variables**

Create/update `backend/.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Database (now using Supabase)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres

# JWT (Supabase handles this, but keep for compatibility)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Storage
STORAGE_BUCKET_PRODUCTS=products
STORAGE_BUCKET_PROFILES=profiles

# Logging (disabled by default)
ENABLE_LOGGING=false

# Environment
DEBUG=false
ENVIRONMENT=production
```

### **5.4 Create Supabase Auth Service**

Create `backend/services/supabase_auth.py`:

```python
from fastapi import HTTPException, Depends
from supabase import Client
from supabase_config import supabase
from typing import Optional
from datetime import datetime, timedelta

class SupabaseAuthService:
    def __init__(self):
        self.client = supabase
    
    async def sign_up(self, email: str, password: str, user_data: dict):
        """Register new user with Supabase Auth"""
        try:
            # Sign up with Supabase Auth
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": user_data.get("name"),
                        "surname": user_data.get("surname"),
                        "username": user_data.get("username"),
                        "phone": user_data.get("phone")
                    }
                }
            })
            
            if response.user:
                # Profile is automatically created by trigger
                return {
                    "user": response.user,
                    "session": response.session
                }
            else:
                raise HTTPException(status_code=400, detail="Registration failed")
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def sign_in(self, email: str, password: str):
        """Sign in user with Supabase Auth"""
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": response.user
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    async def get_user(self, token: str):
        """Get user from Supabase token"""
        try:
            # Set the session
            supabase.auth.set_session(token)
            user = supabase.auth.get_user(token)
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def sign_out(self, token: str):
        """Sign out user"""
        try:
            supabase.auth.set_session(token)
            supabase.auth.sign_out()
            return {"message": "Signed out successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# Create instance
supabase_auth = SupabaseAuthService()
```

### **5.5 Create Supabase Storage Service**

Create `backend/services/supabase_storage.py`:

```python
from supabase import Client
from supabase_config import supabase
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

class SupabaseStorageService:
    def __init__(self):
        self.client = supabase
        self.products_bucket = "products"
        self.profiles_bucket = "profiles"
    
    def generate_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """Generate signed URL for direct client upload"""
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                path=path,
                expires_in=expires_in
            )
            return response.get("signedURL")
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file (for public buckets)"""
        supabase_url = self.client.supabase_url
        return f"{supabase_url}/storage/v1/object/public/{bucket}/{path}"
    
    def generate_upload_path(self, user_id: str, filename: str, bucket_type: str = "products") -> str:
        """Generate unique upload path"""
        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{user_id}/{timestamp}_{unique_id}.{ext}"
    
    def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from storage"""
        try:
            self.client.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(self, bucket: str, folder: Optional[str] = None) -> List[str]:
        """List files in a bucket/folder"""
        try:
            if folder:
                files = self.client.storage.from_(bucket).list(folder)
            else:
                files = self.client.storage.from_(bucket).list()
            return [f["name"] for f in files]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

# Create instance
supabase_storage = SupabaseStorageService()
```

### **5.6 Update Auth Router**

Update `backend/routers/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserResponse, Token, LoginRequest
from services.supabase_auth import supabase_auth
from services.supabase_storage import supabase_storage
from supabase_config import supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user using Supabase Auth"""
    try:
        # Register with Supabase
        result = await supabase_auth.sign_up(
            email=user_data.email,
            password=user_data.password,
            user_data={
                "name": user_data.name,
                "surname": user_data.surname,
                "username": user_data.username,
                "phone": user_data.phone
            }
        )
        
        # Get profile from database
        profile = supabase.table("profiles").select("*").eq("id", result["user"].id).single().execute()
        
        return UserResponse(
            id=profile.data["id"],
            name=profile.data["name"],
            surname=profile.data["surname"],
            email=profile.data["email"],
            phone=profile.data.get("phone"),
            username=profile.data["username"],
            profile_img=profile.data.get("profile_img"),
            created_at=profile.data["created_at"],
            is_email_verified=profile.data.get("is_email_verified", False),
            is_phone_verified=profile.data.get("is_phone_verified", False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login user using Supabase Auth"""
    try:
        # Try email first
        result = await supabase_auth.sign_in(
            email=login_data.identifier,
            password=login_data.password
        )
        
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer"
        }
    except:
        # If email fails, try username/phone lookup
        # Query profile to get email
        profile = supabase.table("profiles").select("email").or_(
            f"username.eq.{login_data.identifier},phone.eq.{login_data.identifier}"
        ).single().execute()
        
        if not profile.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        result = await supabase_auth.sign_in(
            email=profile.data["email"],
            password=login_data.password
        )
        
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer"
        }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(token: str = Depends(get_supabase_user)):
    """Get current user information"""
    user = await get_supabase_user(token)
    profile = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
    
    return UserResponse(**profile.data)
```

### **5.7 Create Image Upload Endpoint (Signed URLs)**

Update `backend/routers/images.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from services.supabase_storage import supabase_storage
from services.supabase_auth import get_current_user_id
from typing import List

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload-url")
async def get_upload_url(
    bucket: str,  # "products" or "profiles"
    filename: str,
    user_id: str = Depends(get_current_user_id)
):
    """Generate signed URL for direct client upload"""
    try:
        # Generate unique path
        path = supabase_storage.generate_upload_path(user_id, filename, bucket)
        
        # Generate signed URL (valid for 1 hour)
        signed_url = supabase_storage.generate_signed_url(bucket, path, expires_in=3600)
        
        return {
            "signed_url": signed_url,
            "path": path,
            "public_url": supabase_storage.get_public_url(bucket, path),
            "expires_in": 3600
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple-urls")
async def get_multiple_upload_urls(
    bucket: str,
    filenames: List[str],
    user_id: str = Depends(get_current_user_id)
):
    """Generate multiple signed URLs for batch upload"""
    urls = []
    for filename in filenames:
        path = supabase_storage.generate_upload_path(user_id, filename, bucket)
        signed_url = supabase_storage.generate_signed_url(bucket, path, expires_in=3600)
        urls.append({
            "filename": filename,
            "signed_url": signed_url,
            "path": path,
            "public_url": supabase_storage.get_public_url(bucket, path)
        })
    return {"urls": urls}

@router.delete("/{bucket}/{path:path}")
async def delete_image(
    bucket: str,
    path: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete image from storage"""
    # Verify user owns the file (path starts with user_id)
    if not path.startswith(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = supabase_storage.delete_file(bucket, path)
    if success:
        return {"message": "Image deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete image")
```

### **5.8 Update Database Connection**

Update `backend/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from supabase_config import supabase
import os

# Use Supabase PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase():
    """Get Supabase client"""
    return supabase
```

### **5.9 Update Product Service**

Update product creation to use Supabase Storage URLs:

```python
# In backend/routers/products.py

@router.post("/")
async def create_product(
    product_data: ProductCreate,
    image_urls: List[str],  # Public URLs from Supabase Storage
    user_id: str = Depends(get_current_user_id)
):
    """Create product with Supabase Storage image URLs"""
    product = {
        "seller_id": user_id,
        "title": product_data.title,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "images": image_urls,  # Store as JSON array
        "approved": False,
        "created_via": "flutter"
    }
    
    result = supabase.table("products").insert(product).execute()
    return result.data[0]
```

### **5.10 Add Logging Service (Optional)**

Create `backend/services/logging_service.py`:

```python
from supabase_config import supabase
import os

ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "false").lower() == "true"

class LoggingService:
    def __init__(self):
        self.enabled = ENABLE_LOGGING
        self.client = supabase
    
    def log(self, level: str, message: str, metadata: dict = None, user_id: str = None):
        """Log to Supabase logs table (only if enabled)"""
        if not self.enabled:
            return
        
        try:
            log_entry = {
                "level": level,
                "message": message,
                "metadata": metadata or {},
                "user_id": user_id
            }
            self.client.table("logs").insert(log_entry).execute()
        except Exception as e:
            # Fail silently - don't break app if logging fails
            print(f"Logging error: {e}")
    
    def enable(self):
        """Enable logging"""
        self.enabled = True
    
    def disable(self):
        """Disable logging"""
        self.enabled = False

# Create instance
logging_service = LoggingService()
```

---

## ⚛️ Step 6: Admin Panel Migration

### **6.1 Install Supabase JS Client**

```bash
cd admin
npm install @supabase/supabase-js
```

### **6.2 Create Supabase Client**

Create `admin/src/services/supabase.ts`:

```typescript
import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key';

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);
```

### **6.3 Update Environment Variables**

Create `admin/.env`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
VITE_API_URL=http://localhost:8000
```

### **6.4 Update Auth Context**

Update `admin/src/contexts/AuthContext.tsx`:

```typescript
import { supabase } from '@/services/supabase';
import { User, Session } from '@supabase/supabase-js';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  };

  const logout = async () => {
    await supabase.auth.signOut();
  };

  return { user, session, loading, login, logout };
};
```

### **6.5 Update API Service**

Update `admin/src/services/api.ts` to use Supabase:

```typescript
import { supabase } from './supabase';
import axios from 'axios';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add Supabase token to requests
    this.api.interceptors.request.use(async (config) => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
      }
      return config;
    });
  }

  // Use Supabase for data fetching
  async getProducts(filters?: ProductFilters, page = 1, limit = 10) {
    const { data, error } = await supabase
      .from('products')
      .select('*, seller:profiles(*)')
      .eq('approved', true)
      .range((page - 1) * limit, page * limit - 1);
    
    if (error) throw error;
    return { data: data, total: data.length, page, limit };
  }

  // For image uploads, get signed URL from backend
  async getUploadUrl(bucket: string, filename: string) {
    const response = await this.api.post('/images/upload-url', {
      bucket,
      filename,
    });
    return response.data;
  }
}
```

### **6.6 Update Image Upload**

Update image upload to use signed URLs:

```typescript
// In admin/src/pages/ProductsPage.tsx

const uploadImage = async (file: File) => {
  // 1. Get signed URL from backend
  const { signed_url, path, public_url } = await apiService.getUploadUrl('products', file.name);
  
  // 2. Upload directly to Supabase Storage
  const { error } = await supabase.storage
    .from('products')
    .upload(path, file, {
      cacheControl: '3600',
      upsert: false
    });
  
  if (error) throw error;
  
  // 3. Return public URL
  return public_url;
};
```

---

## 📱 Step 7: Flutter App Migration

### **7.1 Install Supabase Flutter Package**

Add to `pubspec.yaml`:

```yaml
dependencies:
  supabase_flutter: ^2.0.0
```

Run:
```bash
flutter pub get
```

### **7.2 Initialize Supabase**

Update `lib/main.dart`:

```dart
import 'package:supabase_flutter/supabase_flutter.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await Supabase.initialize(
    url: 'https://your-project.supabase.co',
    anonKey: 'your-anon-key-here',
  );
  
  runApp(MyApp());
}

final supabase = Supabase.instance.client;
```

### **7.3 Create Supabase Service**

Create `lib/services/supabase_service.dart`:

```dart
import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseService {
  final SupabaseClient client = Supabase.instance.client;
  
  // Auth methods
  Future<AuthResponse> signUp({
    required String email,
    required String password,
    required Map<String, dynamic> userData,
  }) async {
    return await client.auth.signUp(
      email: email,
      password: password,
      data: userData,
    );
  }
  
  Future<AuthResponse> signIn({
    required String email,
    required String password,
  }) async {
    return await client.auth.signInWithPassword(
      email: email,
      password: password,
    );
  }
  
  Future<void> signOut() async {
    await client.auth.signOut();
  }
  
  User? get currentUser => client.auth.currentUser;
  
  Stream<AuthState> get authStateChanges => client.auth.onAuthStateChange;
  
  // Storage methods
  Future<String> uploadImage({
    required File imageFile,
    required String bucket,
    required String path,
  }) async {
    final bytes = await imageFile.readAsBytes();
    await client.storage.from(bucket).upload(path, bytes);
    
    // Get public URL
    final publicUrl = client.storage.from(bucket).getPublicUrl(path);
    return publicUrl;
  }
  
  Future<String> getSignedUploadUrl({
    required String bucket,
    required String path,
    required int expiresIn,
  }) async {
    // Call backend API to get signed URL
    final response = await http.post(
      Uri.parse('${AppConstants.apiBaseUrl}/images/upload-url'),
      headers: {
        'Authorization': 'Bearer ${client.auth.currentSession?.accessToken}',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'bucket': bucket,
        'path': path,
        'expires_in': expiresIn,
      }),
    );
    
    final data = json.decode(response.body);
    return data['signed_url'];
  }
  
  // Database methods
  Future<List<Map<String, dynamic>>> getProducts({
    int page = 1,
    int limit = 10,
    String? category,
    String? search,
  }) async {
    var query = client
        .from('products')
        .select('*, seller:profiles(*)')
        .eq('approved', true)
        .eq('discontinued', false)
        .order('created_at', ascending: false)
        .range((page - 1) * limit, page * limit - 1);
    
    if (category != null) {
      query = query.eq('category', category);
    }
    
    if (search != null) {
      query = query.or('title.ilike.%$search%,description.ilike.%$search%');
    }
    
    final response = await query;
    return List<Map<String, dynamic>>.from(response);
  }
}
```

### **7.4 Update Auth Service**

Update `lib/services/auth_service.dart`:

```dart
import '../services/supabase_service.dart';

class AuthService {
  final _supabase = SupabaseService();
  
  static Future<User> register({
    required String name,
    required String surname,
    required String email,
    required String phone,
    required String username,
    required String password,
  }) async {
    final response = await _supabase.signUp(
      email: email,
      password: password,
      userData: {
        'name': name,
        'surname': surname,
        'username': username,
        'phone': phone,
      },
    );
    
    if (response.user == null) {
      throw Exception('Registration failed');
    }
    
    // Get profile
    final profile = await _supabase.client
        .from('profiles')
        .select()
        .eq('id', response.user!.id)
        .single();
    
    return User.fromJson(profile);
  }
  
  static Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
  }) async {
    // First, try to find email by username/phone
    String? email = identifier;
    
    if (!identifier.contains('@')) {
      // Look up email from username or phone
      final profile = await _supabase.client
          .from('profiles')
          .select('email')
          .or('username.eq.$identifier,phone.eq.$identifier')
          .single();
      
      email = profile['email'];
    }
    
    final response = await _supabase.signIn(
      email: email!,
      password: password,
    );
    
    return {
      'access_token': response.session?.accessToken,
      'refresh_token': response.session?.refreshToken,
      'user': response.user,
    };
  }
}
```

### **7.5 Update Image Service**

Update `lib/services/image_service.dart`:

```dart
import '../services/supabase_service.dart';

class ImageService {
  static final _supabase = SupabaseService();
  
  /// Upload image directly to Supabase Storage
  static Future<String> uploadImage({
    required XFile imageFile,
    required String bucket,
  }) async {
    final user = _supabase.currentUser;
    if (user == null) throw Exception('Not authenticated');
    
    // Generate path
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final uuid = Uuid().v4();
    final ext = imageFile.path.split('.').last;
    final path = '${user.id}/$timestamp\_$uuid.$ext';
    
    // Upload to Supabase Storage
    final file = File(imageFile.path);
    final bytes = await file.readAsBytes();
    
    await _supabase.client.storage.from(bucket).upload(path, bytes);
    
    // Get public URL
    final publicUrl = _supabase.client.storage.from(bucket).getPublicUrl(path);
    return publicUrl;
  }
  
  /// Get signed URL for upload (if needed)
  static Future<String> getSignedUploadUrl({
    required String bucket,
    required String filename,
  }) async {
    final user = _supabase.currentUser;
    if (user == null) throw Exception('Not authenticated');
    
    final response = await http.post(
      Uri.parse('${AppConstants.apiBaseUrl}/images/upload-url'),
      headers: {
        'Authorization': 'Bearer ${_supabase.client.auth.currentSession?.accessToken}',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'bucket': bucket,
        'filename': filename,
      }),
    );
    
    final data = json.decode(response.body);
    return data['signed_url'];
  }
}
```

### **7.6 Update App Constants**

Update `lib/constants/app_constants.dart`:

```dart
class AppConstants {
  // Supabase Configuration
  static const String supabaseUrl = 'https://your-project.supabase.co';
  static const String supabaseAnonKey = 'your-anon-key-here';
  
  // Backend API (for business logic only)
  static String get apiBaseUrl {
    if (kIsWeb || Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
      return 'http://localhost:8000';
    }
    if (Platform.isAndroid) {
      return 'http://172.16.25.127:8000';
    }
    if (Platform.isIOS) {
      return 'http://172.16.25.127:8000';
    }
    return 'http://localhost:8000';
  }
}
```

---

## 📊 Step 8: Data Migration (Optional)

### **8.1 Export Current Data**

Create `backend/scripts/export_data.py`:

```python
import json
import sqlite3
from datetime import datetime

def export_users():
    """Export users from SQLite"""
    conn = sqlite3.connect('student_marketplace.db')
    cursor = conn.cursor()
    
    users = cursor.execute('SELECT * FROM users').fetchall()
    # Convert to JSON format
    return users

def export_products():
    """Export products"""
    # Similar implementation
    pass

# Run exports and save to JSON files
```

### **8.2 Import to Supabase**

Create `backend/scripts/import_to_supabase.py`:

```python
from supabase_config import supabase
import json

def import_users(users_data):
    """Import users to Supabase"""
    for user in users_data:
        # Create auth user
        supabase.auth.admin.create_user({
            "email": user["email"],
            "password": "temporary_password",  # Users will need to reset
            "email_confirm": True
        })
        
        # Update profile
        supabase.table("profiles").update({
            "name": user["name"],
            "surname": user["surname"],
            "username": user["username"],
            "phone": user.get("phone"),
        }).eq("id", user["id"]).execute()

def import_products(products_data):
    """Import products"""
    for product in products_data:
        # Migrate image URLs to Supabase Storage format
        images = product.get("images", [])
        migrated_images = []
        
        for img_url in images:
            # Download from old storage and upload to Supabase
            # Then add new URL to migrated_images
            pass
        
        supabase.table("products").insert({
            "id": product["id"],
            "seller_id": product["seller_id"],
            "title": product["title"],
            "description": product["description"],
            "price": product["price"],
            "category": product["category"],
            "images": migrated_images,
            "approved": product.get("approved", False),
        }).execute()
```

---

## 🚀 Step 9: Deploy FastAPI Backend to Render

### **9.1 Prerequisites for Render Deployment**

- [ ] Render account (sign up at [render.com](https://render.com))
- [ ] GitHub repository with your backend code
- [ ] Supabase project created and configured
- [ ] All environment variables documented

### **9.2 Prepare Backend for Render**

#### **Create `render.yaml` (Optional)**

Create `backend/render.yaml` for infrastructure as code:

```yaml
services:
  - type: web
    name: student-marketplace-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: ENABLE_LOGGING
        value: false
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
```

#### **Update `main.py` for Render**

Ensure your `backend/main.py` uses the PORT environment variable:

```python
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

# ... your routes ...

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### **Create `Procfile` (Alternative to render.yaml)**

Create `backend/Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **9.3 Deploy to Render**

#### **Step 1: Create New Web Service**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing your backend

#### **Step 2: Configure Service**

**Basic Settings:**
- **Name:** `student-marketplace-api` (or your preferred name)
- **Environment:** `Python 3`
- **Region:** Choose closest to your users
- **Branch:** `main` (or your production branch)
- **Root Directory:** `backend` (if backend is in a subdirectory)

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### **Step 3: Configure Environment Variables**

In Render dashboard, go to **Environment** tab and add:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres

# Optional: Logging
ENABLE_LOGGING=false

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS (add your frontend URLs)
CORS_ORIGINS=https://your-admin-panel.com,https://your-app.com
```

**⚠️ Important:**
- Get `DATABASE_URL` from Supabase Dashboard → Settings → Database → Connection string → URI
- Replace `[YOUR-PASSWORD]` with your actual Supabase database password
- Keep `SUPABASE_SERVICE_KEY` secret (never commit to Git)

#### **Step 4: Configure Auto-Deploy**

- **Auto-Deploy:** `Yes` (deploys on every push to main branch)
- **Pull Request Previews:** `Yes` (optional, for testing)

#### **Step 5: Deploy**

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start your FastAPI application
3. Wait for deployment to complete (2-5 minutes)
4. Your API will be available at: `https://your-service-name.onrender.com`

### **9.4 Configure Supabase Connection from Render**

#### **Database Connection**

Your FastAPI backend on Render will connect to Supabase PostgreSQL using the `DATABASE_URL`:

1. **Get Connection String from Supabase:**
   - Go to Supabase Dashboard → Settings → Database
   - Under **Connection string**, select **URI**
   - Copy the connection string
   - Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

2. **Add to Render Environment Variables:**
   - Paste the full connection string as `DATABASE_URL`
   - Render will use this to connect to Supabase database

#### **Supabase API Connection**

Your backend uses Supabase client libraries to:
- Authenticate users (Supabase Auth)
- Generate signed URLs for storage
- Access Supabase Storage
- Query database via Supabase client (optional, can use direct PostgreSQL)

**Connection is automatic** - just ensure environment variables are set correctly.

### **9.5 Update CORS Settings**

In your FastAPI `main.py`, update CORS to allow your Render domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-service-name.onrender.com",
        "https://your-admin-panel.com",
        "https://your-app.com",
        "http://localhost:3001",  # Admin panel dev
        "http://localhost:8000",  # Local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **9.6 Test Deployment**

#### **Test API Endpoints:**

```bash
# Health check
curl https://your-service-name.onrender.com/docs

# Test authentication
curl -X POST https://your-service-name.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","name":"Test","surname":"User","username":"testuser","phone":"1234567890"}'
```

#### **Verify Supabase Connection:**

1. Check Render logs for any connection errors
2. Test database queries through your API
3. Verify image upload signed URLs are generated correctly

### **9.7 Render-Specific Considerations**

#### **Free Tier Limitations:**
- **Spins down after 15 minutes of inactivity**
- **Cold starts** may take 30-60 seconds
- **Limited to 750 hours/month**

#### **Solutions:**
1. **Upgrade to Starter Plan** ($7/month) for:
   - Always-on service
   - Faster cold starts
   - Better performance

2. **Use Render Cron Jobs** to ping your service:
   - Create a cron job that hits your health endpoint every 10 minutes
   - Keeps service warm (free tier)

3. **Health Check Endpoint:**
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "service": "student-marketplace-api"}
   ```

#### **Environment Variables Best Practices:**
- Use **Render Environment Groups** for shared variables
- Mark sensitive variables as **Secret**
- Use **Sync from Environment Group** for consistency

### **9.8 Custom Domain (Optional)**

1. In Render dashboard, go to your service
2. Click **"Custom Domains"**
3. Add your domain (e.g., `api.yourdomain.com`)
4. Follow DNS configuration instructions
5. Render automatically provisions SSL certificate

### **9.9 Monitoring & Logs**

#### **View Logs:**
- Render dashboard → Your service → **Logs** tab
- Real-time logs available
- Historical logs stored

#### **Set Up Alerts:**
1. Go to **Alerts** in Render dashboard
2. Configure alerts for:
   - Deployment failures
   - High error rates
   - Service downtime

### **9.10 Update Client Applications**

After deployment, update your client apps to use the Render URL:

#### **Admin Panel (`admin/.env`):**
```env
VITE_API_URL=https://your-service-name.onrender.com
```

#### **Flutter App (`lib/constants/app_constants.dart`):**
```dart
static String get apiBaseUrl {
  if (kIsWeb || Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
    return 'https://your-service-name.onrender.com';
  }
  if (Platform.isAndroid || Platform.isIOS) {
    return 'https://your-service-name.onrender.com';
  }
  return 'https://your-service-name.onrender.com';
}
```

---

## ✅ Step 10: Testing & Verification

### **10.1 Test Authentication**

1. **Test Registration:**
   ```bash
   curl -X POST "https://your-project.supabase.co/auth/v1/signup" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123456"}'
   ```

2. **Test Login:**
   ```bash
   curl -X POST "https://your-project.supabase.co/auth/v1/token?grant_type=password" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123456"}'
   ```

### **10.2 Test Image Upload**

1. Get signed URL from backend
2. Upload image directly to Supabase Storage
3. Verify image is accessible via public URL

### **10.3 Test Database Queries**

Use Supabase dashboard SQL Editor to test queries:

```sql
-- Test product query
SELECT * FROM products WHERE approved = true LIMIT 10;

-- Test profile query
SELECT * FROM profiles LIMIT 10;
```

---

## 🆘 Troubleshooting

### **Render Deployment Issues**

**1. Build Failures:**
- Check `requirements.txt` includes all dependencies
- Verify Python version compatibility
- Check build logs for specific errors

**2. Service Won't Start:**
- Verify `startCommand` uses `$PORT` environment variable
- Check that `main:app` matches your FastAPI app instance
- Review logs for startup errors

**3. Database Connection Errors:**
- Verify `DATABASE_URL` is correctly formatted
- Check Supabase database is accessible (not paused)
- Ensure password in connection string is correct
- Check Supabase firewall settings (if applicable)

**4. Supabase API Connection Issues:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that service role key is used for admin operations
- Verify network connectivity from Render to Supabase

**5. Cold Start Timeouts:**
- Upgrade to paid plan for always-on service
- Implement health check endpoint
- Use cron job to keep service warm

### **Common Issues**

**1. RLS Policies Blocking Queries**
- Check Row Level Security policies
- Verify user has correct permissions
- Test with service role key (admin operations)

**2. Image Upload Fails**
- Verify bucket is public
- Check storage policies
- Verify signed URL hasn't expired

**3. Authentication Not Working**
- Check Supabase URL and keys
- Verify redirect URLs are configured
- Check email confirmation settings

**4. Database Connection Issues**
- Verify DATABASE_URL format
- Check connection pool settings
- Verify network access

---

## 📝 Migration Checklist

### **Pre-Migration**
- [ ] Create Supabase account and project
- [ ] Backup current database
- [ ] Document current data structure
- [ ] Test Supabase setup locally

### **Database**
- [ ] Create all tables in Supabase
- [ ] Set up RLS policies
- [ ] Create triggers and functions
- [ ] Test database queries

### **Storage**
- [ ] Create storage buckets
- [ ] Configure bucket policies
- [ ] Test image upload/download
- [ ] Verify public URLs work

### **Authentication**
- [ ] Configure email auth
- [ ] Set up OAuth providers (optional)
- [ ] Test user registration
- [ ] Test user login

### **Backend**
- [ ] Install Supabase Python client
- [ ] Update auth service
- [ ] Update storage service
- [ ] Update database connections
- [ ] Test all endpoints

### **Admin Panel**
- [ ] Install Supabase JS client
- [ ] Update auth context
- [ ] Update API service
- [ ] Test image uploads
- [ ] Verify all features work

### **Flutter App**
- [ ] Install Supabase Flutter package
- [ ] Update auth service
- [ ] Update image service
- [ ] Test on all platforms
- [ ] Verify image uploads work

### **Data Migration**
- [ ] Export current data
- [ ] Transform data format
- [ ] Import to Supabase
- [ ] Verify data integrity
- [ ] Test with migrated data

### **Deployment (Render)**
- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Configure Render web service
- [ ] Set all environment variables
- [ ] Deploy backend to Render
- [ ] Test API endpoints
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/alerts
- [ ] Update client app URLs

### **Post-Migration**
- [ ] Update all documentation
- [ ] Update environment variables
- [ ] Remove old database files
- [ ] Remove old image storage
- [ ] Update deployment configs
- [ ] Verify Render deployment is working

---

## 🎯 Next Steps After Migration

1. **Enable Real-time Subscriptions:**
   - Use Supabase real-time for live updates
   - Update Flutter app to listen to changes

2. **Optimize Performance:**
   - Add database indexes
   - Optimize RLS policies
   - Use Supabase Edge Functions for heavy operations

3. **Set Up Monitoring:**
   - Enable Supabase dashboard monitoring
   - Set up alerts
   - Monitor storage usage

4. **Enable Logging (Optional):**
   - Set `ENABLE_LOGGING=true` when needed
   - Review logs table periodically

---

---

## 📚 Additional Resources

### **Render Documentation**
- [Render Python Guide](https://render.com/docs/deploy-python)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Custom Domains](https://render.com/docs/custom-domains)

### **Supabase + Render Integration**
- [Supabase Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Supabase Environment Variables](https://supabase.com/docs/guides/getting-started/local-development#environment-variables)

---

**Last Updated:** 2025-01-16
**Migration Status:** Ready to Begin ✅
**Backend Hosting:** Render (FastAPI → Supabase)

