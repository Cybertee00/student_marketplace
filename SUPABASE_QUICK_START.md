# ⚡ Supabase Quick Start Checklist

Use this checklist to quickly migrate to Supabase. Follow the detailed guide in `SUPABASE_MIGRATION_GUIDE.md` for complete instructions.

## 🎯 Pre-Migration (15 minutes)

- [ ] Create Supabase account at [supabase.com](https://supabase.com)
- [ ] Create new project: `student-marketplace`
- [ ] Save project credentials:
  - Project URL
  - Anon key (public)
  - Service role key (secret!)
  - Database password

## 🗄️ Database Setup (30 minutes)

- [ ] Run SQL schema from Step 2 in Supabase SQL Editor
- [ ] Verify all tables created in Table Editor
- [ ] Check RLS policies are enabled

## 📦 Storage Setup (15 minutes)

- [ ] Create `products` bucket (public)
- [ ] Create `profiles` bucket (public)
- [ ] Set up storage policies (from Step 3)
- [ ] Test bucket access

## 🔐 Authentication Setup (10 minutes)

- [ ] Enable Email provider
- [ ] Configure email settings
- [ ] (Optional) Set up OAuth providers
- [ ] Test registration/login

## 🐍 Backend Migration (45 minutes)

- [ ] Install dependencies: `pip install supabase`
- [ ] Create `backend/.env` with Supabase credentials
- [ ] Copy service files:
  - `backend/supabase_config.py`
  - `backend/services/supabase_auth.py`
  - `backend/services/supabase_storage.py`
  - `backend/services/logging_service.py`
- [ ] Update `backend/routers/auth.py` to use Supabase
- [ ] Update `backend/routers/images.py` or use `images_supabase.py`
- [ ] Test backend endpoints

## ⚛️ Admin Panel (30 minutes)

- [ ] Install: `npm install @supabase/supabase-js`
- [ ] Create `admin/.env` with Supabase keys
- [ ] Update `admin/src/services/supabase.ts`
- [ ] Update auth context
- [ ] Update image upload to use signed URLs
- [ ] Test admin panel

## 📱 Flutter App (45 minutes)

- [ ] Add to `pubspec.yaml`: `supabase_flutter: ^2.0.0`
- [ ] Run: `flutter pub get`
- [ ] Initialize Supabase in `main.dart`
- [ ] Create `lib/services/supabase_service.dart`
- [ ] Update `lib/services/auth_service.dart`
- [ ] Update `lib/services/image_service.dart`
- [ ] Test on device/emulator

## ✅ Testing (30 minutes)

- [ ] Test user registration
- [ ] Test user login
- [ ] Test image upload (get signed URL → upload → verify public URL)
- [ ] Test product creation with images
- [ ] Test profile picture upload
- [ ] Verify all features work

## 📊 Data Migration (Optional, 1-2 hours)

- [ ] Export current data from SQLite/PostgreSQL
- [ ] Transform data format
- [ ] Import to Supabase
- [ ] Verify data integrity
- [ ] Test with migrated data

## 🚀 Render Deployment

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Configure web service
- [ ] Set environment variables (Supabase + Database)
- [ ] Deploy FastAPI backend
- [ ] Test API endpoints
- [ ] Update client app URLs to Render domain

## 🎉 Post-Migration

- [ ] Update documentation
- [ ] Remove old database files
- [ ] Remove old image storage
- [ ] Update deployment configs
- [ ] Enable logging if needed: `ENABLE_LOGGING=true`
- [ ] Verify Render deployment is working

---

## 🔑 Environment Variables Checklist

### Backend `.env`
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.your-project.supabase.co:5432/postgres
ENABLE_LOGGING=false
```

### Admin Panel `.env`
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Flutter App
Update `lib/constants/app_constants.dart`:
```dart
static const String supabaseUrl = 'https://your-project.supabase.co';
static const String supabaseAnonKey = 'your-anon-key';
```

---

## 🆘 Quick Troubleshooting

**RLS blocking queries?**
- Check policies in Supabase dashboard
- Use service role key for admin operations

**Images not uploading?**
- Verify bucket is public
- Check storage policies
- Verify signed URL hasn't expired

**Auth not working?**
- Check Supabase URL and keys
- Verify redirect URLs configured
- Check email confirmation settings

---

**Need detailed instructions?** See `SUPABASE_MIGRATION_GUIDE.md`

