# 🚀 Deployment Guide

## Quick Deploy Options

### Option 1: Frontend Only (Vercel) - 5 minutes ⚡

**Deploy Frontend to Vercel (Free):**

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy from root directory:**
   ```bash
   cd frontend
   vercel
   ```

3. **Follow prompts:**
   - Link to existing project? No
   - Project name: policysentinel
   - Directory: ./
   - Override settings? No

4. **Your frontend will be live at:**
   ```
   https://policysentinel.vercel.app
   ```

**Note:** Frontend will work for UI demo, but API calls will fail until backend is deployed.

---

### Option 2: Full Stack (Railway) - 10 minutes 🚂

**Deploy Both Frontend + Backend:**

1. **Go to Railway.app:**
   - Sign up: https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: subhra-io/GDG

2. **Add Services:**
   
   **Backend Service:**
   - Root directory: `/`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables:
     ```
     OPENAI_API_KEY=your_key_here
     DATABASE_URL=postgresql://...
     MONGODB_URL=mongodb://...
     REDIS_URL=redis://...
     ```

   **Frontend Service:**
   - Root directory: `/frontend`
   - Build command: `npm install && npm run build`
   - Start command: `npm start`
   - Environment variable:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend.railway.app
     ```

3. **Add Databases:**
   - Click "New" → "Database" → "PostgreSQL"
   - Click "New" → "Database" → "MongoDB"
   - Click "New" → "Database" → "Redis"
   - Railway will auto-connect them

4. **Deploy:**
   - Railway auto-deploys on git push
   - Get URLs from Railway dashboard

---

### Option 3: Docker Compose (Any VPS) - 15 minutes 🐳

**Deploy to DigitalOcean, AWS, or any VPS:**

1. **SSH into your server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Clone repository:**
   ```bash
   git clone https://github.com/subhra-io/GDG.git
   cd GDG
   ```

3. **Setup environment:**
   ```bash
   cp .env.example .env
   nano .env  # Add your OPENAI_API_KEY
   ```

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

5. **Setup Nginx reverse proxy:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:3000;
       }

       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

6. **Access:**
   - Frontend: http://your-domain.com
   - Backend: http://your-domain.com/api

---

## 🎯 Recommended for Hackathon: Vercel (Frontend Only)

**Pros:**
- ✅ Free
- ✅ 5 minutes to deploy
- ✅ Auto-deploys on git push
- ✅ Global CDN
- ✅ HTTPS included
- ✅ Perfect for demo/presentation

**Cons:**
- ⚠️ Backend not deployed (API calls won't work)
- ⚠️ Need to mention "Backend runs locally"

**For Submission:**
- Live Demo URL: `https://policysentinel.vercel.app`
- Note: "Backend API runs locally for security (contains OpenAI API key)"

---

## 📝 Quick Vercel Deploy Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy frontend
cd frontend
vercel --prod

# Your site is live! 🎉
```

---

## 🔐 Environment Variables Needed

**Backend (.env):**
```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://localhost/policysentinel
MONGODB_URL=mongodb://localhost:27017/policysentinel
REDIS_URL=redis://localhost:6379
```

**Frontend (.env.production):**
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## 🎬 Demo Strategy

**Option A: Frontend Deployed, Backend Local**
- Show live frontend on Vercel
- Mention: "Backend runs locally with OpenAI API key for security"
- Perfect for UI/UX demonstration

**Option B: Full Stack Deployed**
- Both frontend and backend live
- Full working demo
- Requires paid hosting for databases

**Option C: Local Demo**
- Everything runs locally
- Most reliable for live demo
- No deployment issues

---

## 🚀 Deploy Now!

**Fastest option (5 minutes):**
```bash
cd frontend
npm i -g vercel
vercel --prod
```

Your frontend will be live at: `https://policysentinel-xxx.vercel.app`

Update submission form with this URL! 🎉
