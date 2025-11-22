# 🚀 How to Run FLUD App - Quick Reference

## ⚡ Fast Start (3 Commands)

### Terminal 1 - Start Backend:
```bash
cd flood_model
python api_server.py
```
✅ Backend runs at: **http://localhost:8000**

### Terminal 2 - Start Frontend:
```bash
cd frontend
npm install  # First time only
npm run dev
```
✅ Frontend runs at: **http://localhost:3000**

### Browser:
Open **http://localhost:3000** → Disable "Use Mock Data" → Analyze!

---

## 📋 Prerequisites (One-Time Setup)

### 1. Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. CDS API Credentials
Create `~/.cdsapirc` (or `C:\Users\YourUsername\.cdsapirc` on Windows):
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```
Get credentials from: https://cds.climate.copernicus.eu/api-how-to

### 3. Node Dependencies (Frontend)
```bash
cd frontend
npm install
```

---

## 🔄 Complete Workflow

```
┌─────────────────┐
│   User Browser  │
│  localhost:3000 │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  Frontend (Vite)│
│  React + TS     │
│  Port: 3000     │
└────────┬────────┘
         │ API Calls
         │ POST /api/predict
         ▼
┌─────────────────┐
│ Backend (FastAPI)│
│  Port: 8000     │
└────────┬────────┘
         │ Uses
         ▼
┌─────────────────┐      ┌─────────────┐
│ FloodPredictor  │─────▶│  CDS API    │
│  Class          │      │ (Weather)   │
└────────┬────────┘      └─────────────┘
         │ Uses (optional)
         ▼
┌─────────────────┐
│     Ollama      │
│  (AI Analysis)  │
│  Port: 11434    │
└─────────────────┘
```

---

## ✅ Verification Steps

1. **Backend Health:**
   ```bash
   curl http://localhost:8000/health
   # Or open: http://localhost:8000/health
   ```

2. **API Docs:**
   Open: http://localhost:8000/docs

3. **Frontend:**
   Open: http://localhost:3000

4. **Test Mock Data:**
   - Enable "Use Mock Data" toggle
   - Click "Analyze Flood Risk"
   - Should show results instantly

5. **Test Real Backend:**
   - Disable "Use Mock Data" toggle
   - Enter coordinates (16.5062, 80.6480)
   - Click "Analyze Flood Risk"
   - Wait 2-5 minutes for first request

---

## 🐛 Common Issues

### Backend won't start?
- ✅ Check: `pip install -r requirements.txt`
- ✅ Check: `.cdsapirc` file exists and has correct format
- ✅ Check: Port 8000 not in use

### Frontend can't connect?
- ✅ Check: Backend is running (http://localhost:8000/health)
- ✅ Check: Browser console (F12) for errors
- ✅ Check: CORS settings in `api_server.py`

### CDS API errors?
- ✅ Check: `.cdsapirc` file format
- ✅ Check: Credentials are valid
- ✅ Check: Internet connection

### First request takes forever?
- ✅ Normal! First CDS API request takes 5-10 minutes
- ✅ Check backend terminal for progress logs
- ✅ Be patient - subsequent requests may be faster

---

## 📁 Key Files

```
flood_model/
  └── api_server.py         # ← Start backend here

frontend/
  └── src/
      ├── services/api.ts   # ← API client (configured for localhost:8000)
      └── pages/Dashboard.tsx  # ← Main UI

requirements.txt            # ← Python deps
```

---

## 🎯 Quick Test Flow

1. **Terminal 1:** `cd flood_model && python api_server.py`
2. **Terminal 2:** `cd frontend && npm run dev`
3. **Browser:** http://localhost:3000
4. **Test Mock:** Enable toggle → Analyze → ✅ Instant results
5. **Test Real:** Disable toggle → Analyze → ⏳ Wait 2-5 min → ✅ Real results

---

**Full Details:** See `COMPLETE_SETUP_GUIDE.md` for comprehensive instructions.

