# 🔧 Admin Panel Environment Setup

## 📝 **Create `.env` File**

Create a file named `.env` in the `admin` folder with:

```env
VITE_SUPABASE_URL=https://kxqhklgknwgmehyyttzp.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjAzNDUsImV4cCI6MjA3ODk2MzQ1fQ.efpywMHQ-lb3HX27gxxkBuojDIytHrwasoJsiOB66m4
VITE_API_URL=https://student-marketplace-api.onrender.com
```

## 🚀 **After Creating `.env`**

1. **Restart the dev server:**
   ```bash
   cd admin
   npm run dev
   ```

2. **The admin panel will now use your Render API!**

---

**Note:** The `.env` file is in `.gitignore` so it won't be committed to Git (which is correct for security).

