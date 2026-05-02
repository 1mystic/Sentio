# Quick Commands Reference

## 🚀 Initial Setup Commands

Run these commands in order to set up the project:

### 1. Install Dependencies
```bash
npm install
```

### 2. Create Environment File
```bash
# Create .env file (you'll need to add your API keys)
touch .env
```

Then edit `.env` and add (use `VITE_` prefixes for client-side access):
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_COHERE_API_KEY=your_cohere_api_key
NODE_ENV=development
```

### 3. Start Development Server
```bash
npm run dev
```

Visit: `http://localhost:5173` (default Vite dev server)

---

## 📦 Development Commands

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Lint Code
```bash
npm run lint
```

### Fix Linting Issues
```bash
npm run lint:fix
```

---

## 🗄️ Database Commands

### Access Supabase SQL Editor
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Run the SQL from `SETUP.md` to create tables

---

## 🚢 Deployment Commands

### Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
```

### Connect to GitHub
```bash
git remote add origin <your-github-repo-url>
git push -u origin main
```

Then connect to Vercel (see SETUP.md for details)

---

## 🔧 Troubleshooting Commands

### Clear Node Modules and Reinstall
```bash
rm -rf node_modules package-lock.json
npm install
```

### Clear Cache / Reinstall
If you need to clear caches and reinstall dependencies:

```bash
rm -rf node_modules package-lock.json dist
npm install
npm run dev
```

### Check Node Version
```bash
node --version  # Should be >= 18.0.0
npm --version   # Should be >= 9.0.0
```

---

## 📝 Next Steps After Setup

1. ✅ Run `npm install`
2. ✅ Set up Supabase (see SETUP.md)
3. ✅ Add API keys to `.env`
4. ✅ Run database migrations in Supabase SQL Editor
5. ✅ Run `npm run dev`
6. ✅ Test signup/login flow
7. 🎉 Start building features!

---

**Need help?** Check `SETUP.md` for detailed instructions.

