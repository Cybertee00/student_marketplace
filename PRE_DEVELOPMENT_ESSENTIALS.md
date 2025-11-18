# 📋 Pre-Development Essentials Guide
## Student Marketplace - Complete Project Setup & Architecture

---

## 🎯 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Image Storage Architecture](#image-storage-architecture)
4. [Environment Setup](#environment-setup)
5. [Database Configuration](#database-configuration)
6. [Authentication & Security](#authentication--security)
7. [Third-Party Services](#third-party-services)
8. [Development Workflow](#development-workflow)
9. [Deployment Checklist](#deployment-checklist)
10. [Critical Configuration Files](#critical-configuration-files)

---

## 🏗️ Project Overview

### **Project Structure**
```
student_marketplace/
├── backend/          # FastAPI Python backend
├── admin/            # React TypeScript admin panel
├── lib/              # Flutter mobile app
├── android/          # Android native code
├── ios/              # iOS native code
└── web/              # Web build configuration
```

### **Current Status**
- ✅ Backend API (FastAPI) - Fully functional
- ✅ Admin Panel (React/TypeScript) - Fully functional
- ✅ Mobile App (Flutter) - Fully functional
- ✅ Database (PostgreSQL) - Configured
- ✅ Authentication (JWT) - Implemented
- ✅ Image Storage - Hybrid (Local + Google Drive ready)
- ✅ WebSocket - Real-time messaging
- ✅ Role-Based Access Control (RBAC) - Implemented

---

## 🖼️ Image Storage Architecture

### **Where Images Are Saved**

#### **1. Development Mode (Current Setup)**
Images are stored **locally** in the backend directory:

```
backend/
├── products_images/      # Product images stored here
│   ├── 20250916_022320_abc123.jpg
│   ├── 20250916_022321_def456.png
│   └── ...
└── profile_pictures/     # User profile pictures stored here
    ├── 20250916_022320_xyz789.jpg
    └── ...
```

**File Naming Convention:**
- Format: `{timestamp}_{uuid}.{extension}`
- Example: `20250916_022320_e5bb234e-dc9f-4267-a9a4-9b371e5333d5.jpg`
- Ensures uniqueness and prevents conflicts

#### **2. Production Mode (Google Drive Integration)**
When Google Drive is enabled, images are stored in:

**Google Drive Folders:**
- **Products Folder ID:** `156ZsoOjj9nUICNjGdS8_kAnzQc1569JC`
- **Profile Pictures Folder ID:** `1jknOL8yP2fDxLi9r_6mz8OK4fy54FdUM`

**Storage Service:** `HybridStorageService`
- Automatically switches between local and Google Drive
- Currently: `USE_GOOGLE_DRIVE = False` (local storage)
- Can be enabled: `hybrid_storage.enable_google_drive()`

#### **3. Image URL Structure**

**Development (Local):**
```
http://localhost:8000/images/{filename}              # Product images
http://localhost:8000/images/profile/{filename}      # Profile pictures
```

**Production (Google Drive):**
```
https://drive.google.com/uc?id={file_id}            # Direct download URL
https://drive.google.com/file/d/{file_id}/view       # View URL
```

**Admin Panel (Vite Proxy):**
```
/images/{filename}                                   # Relative path (proxied to backend)
```

**Mobile App:**
```
http://172.16.25.127:8000/images/{filename}         # Full URL (Android device)
http://10.0.2.2:8000/images/{filename}              # Full URL (Android emulator)
http://localhost:8000/images/{filename}             # Full URL (iOS simulator/Web)
```

### **Image Storage Service**

**File:** `backend/hybrid_storage_service.py`

**Key Methods:**
- `save_image_locally()` - Saves images to local folders
- `get_image_url()` - Returns appropriate URL based on storage mode
- `delete_image()` - Removes images from storage
- `list_images()` - Lists all images in a folder

**Configuration:**
```python
self.PRODUCTS_FOLDER = "products_images"
self.PROFILE_FOLDER = "profile_pictures"
self.USE_GOOGLE_DRIVE = False  # Toggle for production
```

---

## 🛠️ Architecture & Technology Stack

### **Backend (FastAPI)**
- **Framework:** FastAPI (Python 3.8+)
- **Database:** SQLite (dev) / PostgreSQL (production)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** JWT (JSON Web Tokens)
- **File Storage:** Hybrid (Local + Google Drive)
- **Real-time:** WebSocket (Socket.IO)
- **API Documentation:** Swagger/OpenAPI (`/docs`)

### **Admin Panel (React)**
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State Management:** React Query (TanStack Query)
- **HTTP Client:** Axios
- **Routing:** React Router DOM
- **Charts:** Recharts
- **Port:** 3001

### **Mobile App (Flutter)**
- **Framework:** Flutter 3.8.1+
- **Language:** Dart
- **State Management:** Provider
- **Navigation:** GoRouter
- **HTTP Client:** http package
- **Local Storage:** SharedPreferences
- **Image Caching:** cached_network_image

---

## ⚙️ Environment Setup

### **1. Backend Setup**

**Prerequisites:**
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL (for production) or SQLite (for development)

**Installation:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `alembic` - Database migrations
- `python-jose` - JWT tokens
- `passlib` - Password hashing
- `python-multipart` - File uploads
- `google-api-python-client` - Google Drive integration

**Start Backend:**
```bash
cd backend
uvicorn main:app --reload
# Or use: python start.py
```

**Backend runs on:** `http://localhost:8000`

### **2. Admin Panel Setup**

**Prerequisites:**
- Node.js 18 or higher
- npm or yarn

**Installation:**
```bash
cd admin
npm install
```

**Start Admin Panel:**
```bash
npm run dev
```

**Admin Panel runs on:** `http://localhost:3001`

**Login Credentials:**
- Email: `admin@university.edu`
- Password: `admin123`

### **3. Mobile App Setup**

**Prerequisites:**
- Flutter SDK 3.8.1 or higher
- Dart SDK
- Android Studio / Xcode (for mobile development)
- VS Code or Android Studio IDE

**Installation:**
```bash
flutter pub get
```

**Run App:**
```bash
flutter run
```

**Platform-Specific API URLs:**
- **Android Emulator:** `http://10.0.2.2:8000`
- **Physical Android Device:** `http://172.16.25.127:8000` (your computer's IP)
- **iOS Simulator:** `http://localhost:8000`
- **Web/Desktop:** `http://localhost:8000`

---

## 🗄️ Database Configuration

### **Development (SQLite)**
```python
DATABASE_URL = "sqlite:///./student_marketplace.db"
```
- Database file: `backend/student_marketplace.db`
- No setup required - created automatically

### **Production (PostgreSQL)**
```python
DATABASE_URL = "postgresql://user:password@host:port/database_name"
```

**Setup PostgreSQL:**
1. Install PostgreSQL
2. Create database: `CREATE DATABASE student_marketplace;`
3. Update `backend/config.py` with connection string
4. Run migrations: `alembic upgrade head`

### **Database Migrations**

**Create Migration:**
```bash
cd backend
alembic revision --autogenerate -m "description"
```

**Apply Migrations:**
```bash
alembic upgrade head
```

**Rollback Migration:**
```bash
alembic downgrade -1
```

---

## 🔐 Authentication & Security

### **JWT Configuration**

**File:** `backend/config.py`

```python
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

**⚠️ CRITICAL:** Change `SECRET_KEY` in production!

### **Password Hashing**
- **Algorithm:** bcrypt
- **Library:** passlib
- **Auto-hashing:** All passwords are hashed before storage

### **User Roles & Permissions**

**Role-Based Access Control (RBAC):**
- **Admin:** Full system access
- **User:** Standard marketplace access
- **Seller:** Can create and manage products

**File:** `backend/rbac.py`

### **Email Verification**
- **2FA System:** Email verification for new users
- **Token Expiry:** 10 minutes
- **OTP Length:** 6 digits
- **Development Mode:** OTP printed to console

---

## 🌐 Third-Party Services

### **1. Google Drive (Image Storage)**

**Purpose:** Store product images and profile pictures in production

**Setup Required:**
1. Create Google Cloud Project
2. Enable Google Drive API
3. Create Service Account or OAuth2 credentials
4. Download credentials JSON file
5. Place in `backend/google-credentials.json` or `backend/oauth-credentials.json`

**Configuration Files:**
- `backend/google_drive_service.py` - Service account method
- `backend/oauth_google_drive_service.py` - OAuth2 method
- `backend/hybrid_storage_service.py` - Hybrid storage wrapper

**Folder IDs:**
- Products: `156ZsoOjj9nUICNjGdS8_kAnzQc1569JC`
- Profiles: `1jknOL8yP2fDxLi9r_6mz8OK4fy54FdUM`

**Enable Google Drive:**
```python
# In hybrid_storage_service.py
hybrid_storage.enable_google_drive()
```

### **2. Email Service (SMTP)**

**Purpose:** Send verification emails, notifications

**Configuration:** `backend/config.py`

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
```

**Options:**
- Gmail (with App Password)
- SendGrid
- AWS SES
- Mailgun

### **3. Payment Gateway**

**Current:** Demo/PayGate integration
- **Demo ID:** `10011072100`
- **Merchant ID:** `10000100`

**⚠️ CRITICAL:** Replace with production credentials before launch!

---

## 📁 Critical Configuration Files

### **Backend Configuration**

**1. `backend/config.py`**
- Database URL
- JWT secret key
- SMTP settings
- CORS origins
- Environment variables

**2. `backend/database.py`**
- Database connection
- Session management

**3. `backend/auth.py`**
- JWT token creation/verification
- Password hashing
- User authentication

**4. `backend/models.py`**
- Database models (User, Product, Order, etc.)
- Relationships and constraints

**5. `backend/schemas.py`**
- Pydantic models for request/response validation
- Image URL transformation

### **Admin Panel Configuration**

**1. `admin/vite.config.ts`**
- API proxy configuration
- Port settings
- Build configuration

**2. `admin/src/services/api.ts`**
- API base URL
- Request interceptors
- Error handling

### **Mobile App Configuration**

**1. `lib/constants/app_constants.dart`**
- API base URL (platform-specific)
- App constants
- Color scheme

**2. `lib/services/api_service.dart`**
- API endpoints
- Request/response handling

---

## 🔄 Development Workflow

### **1. Starting the Development Environment**

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Admin Panel:**
```bash
cd admin
npm run dev
```

**Terminal 3 - Mobile App:**
```bash
flutter run
```

### **2. Database Changes**

1. Modify models in `backend/models.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review migration file in `backend/alembic/versions/`
4. Apply: `alembic upgrade head`

### **3. API Testing**

**Swagger UI:** `http://localhost:8000/docs`
- Interactive API documentation
- Test endpoints directly
- View request/response schemas

**Alternative:** Use Postman or curl

### **4. Image Upload Testing**

**Test Image Upload:**
```bash
curl -X POST "http://localhost:8000/images/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg"
```

---

## 🚀 Deployment Checklist

### **Pre-Deployment Requirements**

#### **1. Security**
- [ ] Change JWT `SECRET_KEY` to strong random string
- [ ] Update database password
- [ ] Configure CORS origins (remove `*`)
- [ ] Enable HTTPS/SSL
- [ ] Set `DEBUG = False`
- [ ] Review and secure API endpoints

#### **2. Database**
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Backup existing database
- [ ] Run all migrations: `alembic upgrade head`
- [ ] Test database connection
- [ ] Set up database backups

#### **3. Image Storage**
- [ ] Set up Google Drive credentials
- [ ] Create Google Drive folders
- [ ] Update folder IDs in code
- [ ] Enable Google Drive: `hybrid_storage.enable_google_drive()`
- [ ] Migrate existing images (if any)
- [ ] Test image upload/download

#### **4. Email Service**
- [ ] Configure production SMTP server
- [ ] Test email sending
- [ ] Set up email templates
- [ ] Verify email delivery

#### **5. Payment Gateway**
- [ ] Replace demo credentials with production
- [ ] Test payment flow
- [ ] Set up webhook endpoints
- [ ] Configure payment notifications

#### **6. Environment Variables**
- [ ] Create `.env` file (don't commit!)
- [ ] Set all required environment variables
- [ ] Document all environment variables
- [ ] Set up environment-specific configs

#### **7. API Configuration**
- [ ] Update API base URLs for production
- [ ] Configure CORS for production domains
- [ ] Set up rate limiting
- [ ] Enable request logging
- [ ] Set up monitoring/analytics

#### **8. Mobile App**
- [ ] Update API base URL to production
- [ ] Configure app signing (Android/iOS)
- [ ] Update app version
- [ ] Test on physical devices
- [ ] Prepare for app store submission

#### **9. Admin Panel**
- [ ] Build production bundle: `npm run build`
- [ ] Configure reverse proxy
- [ ] Set up SSL certificate
- [ ] Test all admin functions
- [ ] Verify image loading

#### **10. Testing**
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Load testing
- [ ] Security testing
- [ ] User acceptance testing

---

## 📝 Essential Environment Variables

### **Backend (.env)**
```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your-super-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Google Drive (Optional)
GOOGLE_CREDENTIALS_PATH=google-credentials.json
GOOGLE_DRIVE_ENABLED=false

# Environment
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### **Admin Panel (.env)**
```env
VITE_API_URL=http://localhost:8000
```

### **Mobile App**
Configured in `lib/constants/app_constants.dart`:
```dart
static String get apiBaseUrl {
  // Platform-specific configuration
  if (Platform.isAndroid) {
    return 'http://172.16.25.127:8000'; // Your server IP
  }
  return 'http://localhost:8000';
}
```

---

## 🔧 Image Storage Decision Matrix

### **When to Use Local Storage**
- ✅ Development/Testing
- ✅ Small-scale deployment
- ✅ Limited storage needs
- ✅ No cloud service setup

### **When to Use Google Drive**
- ✅ Production deployment
- ✅ Scalable storage needs
- ✅ CDN-like performance
- ✅ Backup and redundancy

### **Hybrid Approach (Current)**
- ✅ Start with local storage
- ✅ Switch to Google Drive when ready
- ✅ No code changes needed
- ✅ Seamless migration

---

## 📊 Current Project Status

### **✅ Completed Features**

**Backend:**
- User authentication (JWT)
- User registration with email verification
- Product CRUD operations
- Order management
- Shopping cart
- Image upload/download
- Real-time messaging (WebSocket)
- Role-based access control
- Admin dashboard API
- Review system
- Notification system

**Admin Panel:**
- Dashboard with analytics
- Product management
- Order management
- User management
- Revenue reports
- Messaging system
- Inventory management

**Mobile App:**
- User registration/login
- Product browsing
- Search and filters
- Shopping cart
- Order placement
- Profile management
- Product selling
- Favorites
- Reviews

### **🚧 In Progress / Needs Attention**

- [ ] Production image storage setup (Google Drive)
- [ ] Production email service configuration
- [ ] Payment gateway production credentials
- [ ] Database migration to PostgreSQL
- [ ] Production deployment
- [ ] SSL/HTTPS setup
- [ ] Performance optimization
- [ ] Comprehensive testing

---

## 🎓 Learning Resources

### **FastAPI**
- Official Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### **Flutter**
- Official Docs: https://flutter.dev/docs
- Cookbook: https://flutter.dev/docs/cookbook

### **React/TypeScript**
- React Docs: https://react.dev
- TypeScript Docs: https://www.typescriptlang.org/docs

### **Google Drive API**
- API Docs: https://developers.google.com/drive/api
- Python Client: https://github.com/googleapis/google-api-python-client

---

## 🆘 Troubleshooting

### **Common Issues**

**1. Images Not Loading**
- Check API base URL configuration
- Verify image folder exists
- Check file permissions
- Review CORS settings

**2. Database Connection Errors**
- Verify DATABASE_URL
- Check database is running
- Review connection credentials
- Check firewall settings

**3. Authentication Issues**
- Verify JWT secret key
- Check token expiration
- Review CORS origins
- Verify user exists in database

**4. Google Drive Not Working**
- Check credentials file exists
- Verify API is enabled
- Review folder permissions
- Check service account setup

---

## 📞 Support & Documentation

### **Project Documentation Files**
- `README.md` - Main project documentation
- `backend/README.md` - Backend-specific docs
- `admin/README.md` - Admin panel docs
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `GOOGLE_DRIVE_SETUP_GUIDE.md` - Google Drive setup
- `OAUTH_SETUP_GUIDE.md` - OAuth2 setup

### **Quick Reference**

**Backend API:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs`
**Admin Panel:** `http://localhost:3001`

**Default Admin Login:**
- Email: `admin@university.edu`
- Password: `admin123`

---

## ✅ Pre-Development Checklist

Before starting development, ensure:

- [ ] All prerequisites installed (Python, Node.js, Flutter)
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Admin panel dependencies installed (`npm install`)
- [ ] Flutter dependencies installed (`flutter pub get`)
- [ ] Database configured and migrations run
- [ ] Environment variables set up
- [ ] Image storage folders created
- [ ] API base URLs configured correctly
- [ ] All services can start successfully
- [ ] Test user can be created and login works
- [ ] Image upload/download works
- [ ] Admin panel can connect to backend
- [ ] Mobile app can connect to backend

---

**Last Updated:** 2025-01-16
**Project Version:** 1.0.0
**Status:** Development Ready ✅

