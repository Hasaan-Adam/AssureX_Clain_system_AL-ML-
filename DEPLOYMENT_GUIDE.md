# AssureX Claim Engine - Deployment Guide

## Recommended Architecture for FYP Live Deployment

Deploying a full-stack AI application requires separating the Frontend and the Backend because of storage and computational limits on standard free platforms.

### 1. Frontend (React + Vite) ➔ VERCEL
**Vercel is perfect for the frontend.**
We have already created the `vercel.json` in the `frontend` folder.

**Steps to deploy Frontend on Vercel:**
1. Push your code to GitHub.
2. Go to Vercel.com and click "Add New Project".
3. Select your repository.
4. **Important:** Set the **Root Directory** to `frontend`.
5. Vercel will automatically detect Vite. Click **Deploy**.
6. Once deployed, Vercel will give you a live URL (e.g., `https://assurex-frontend.vercel.app`).

### 2. Backend (FastAPI + AI Models) ➔ RENDER.COM or RAILWAY
**Why NOT Vercel for Backend?**
- **Serverless Limits:** Vercel functions are serverless. They shut down after 10 seconds of inactivity. Loading XGBoost and Random Forest models takes a few seconds, which might cause "Cold Start Timeouts" on Vercel.
- **File Limits:** Vercel free tier limits function size to 50MB. Scikit-learn, Pandas, XGBoost, and model `.joblib` files exceed this limit.
- **Database Wipeout:** Vercel has no persistent disk. Our SQLite (`assurex.db`) and uploaded receipt images (`uploads/`) will be deleted the moment the function goes to sleep.

**How to deploy Backend on Render.com:**
1. Create a free account on [Render.com](https://render.com).
2. Create a new **Web Service** and link your GitHub repo.
3. Keep the Root Directory empty (so it uses the main Python folder).
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. *Note on Database:* For a true live deployment, you should replace the SQLite URL in `.env` with a free PostgreSQL database (Render provides a free PostgreSQL database for 90 days).

### 3. Updating the Connection (Frontend ➔ Backend)
Once your backend is live on Render (e.g., `https://assurex-api.onrender.com`), you need to tell Vercel to connect to it.
1. Go to your Vercel Project Settings > Environment Variables.
2. Add a new variable:
   - Name: `VITE_API_URL`
   - Value: `https://assurex-api.onrender.com/api/v1` (Replace with your actual Render URL).
3. Redeploy your Vercel frontend.

---

### Alternative (Easiest Method for Presentation): Hybrid Local-Live
If you just want to present this on your laptop without the headache of cloud databases and 50MB size limits:
1. Deploy the Frontend on **Vercel** (so it looks live).
2. Run the Backend on **Localhost** (`run_backend.bat`).
3. Connect your Vercel frontend to `http://localhost:8000` (or use Ngrok to tunnel it).
This way, the evaluators see a real live URL, but your laptop handles the heavy AI processing and local database!
