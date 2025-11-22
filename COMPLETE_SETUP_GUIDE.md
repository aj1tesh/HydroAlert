# 🚀 FLUD - Complete Setup Guide

This guide walks you through setting up both the backend and frontend to get the FLUD app working properly.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.8+** installed (`python --version` to check)
- [ ] **Node.js 18+** installed (`node --version` to check)
- [ ] **npm** or **yarn** installed (`npm --version` to check)
- [ ] **CDS API account** (free) - https://cds.climate.copernicus.eu/
- [ ] **Internet connection** (for fetching weather data)
- [ ] **Ollama** (optional, for AI analysis) - https://ollama.ai/

---

## 🔧 Part 1: Backend Setup

### Step 1.1: Install Python Dependencies

Open a terminal in the project root (`D:\E\Flud`):

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**What this installs:**
- `fastapi` & `uvicorn` - Web server
- `cdsapi` - Copernicus Data Store API client
- `xarray`, `cfgrib`, `netCDF4` - GRIB file handling
- `numpy`, `pandas` - Data processing
- `requests` - HTTP requests

### Step 1.2: Configure CDS API Credentials

The backend needs CDS API credentials to fetch weather data.

1. **Create CDS account** (if you don't have one):
   - Go to https://cds.climate.copernicus.eu/
   - Click "Login" and create an account (free)

2. **Get your API credentials**:
   - Log in to CDS
   - Go to https://cds.climate.copernicus.eu/api-how-to
   - Copy your **UID** and **API Key**

3. **Create `.cdsapirc` file** in your home directory:

   **Windows location:**
   ```
   C:\Users\YourUsername\.cdsapirc
   ```
   
   **Linux/Mac location:**
   ```
   ~/.cdsapirc
   ```

   **File content:**
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR_UID:YOUR_API_KEY
   ```
   
   Replace `YOUR_UID` and `YOUR_API_KEY` with your actual credentials.

   **Example:**
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: 123456:abcdef123456-7890-abcdef123456
   ```

### Step 1.3: Verify CDS Configuration

Test if CDS API is configured correctly:

```bash
cd flood_model
python -c "from flood_predictor import FloodPredictor; p = FloodPredictor(); print('CDS API configured successfully!')"
```

If you see an error, check your `.cdsapirc` file format and credentials.

### Step 1.4: Start the Backend Server

From the `flood_model` directory:

```bash
cd flood_model
python api_server.py
```

**Expected output:**
```
============================================================
FLUD Backend API Server
============================================================
Starting server on http://localhost:8000
API Documentation: http://localhost:8000/docs
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal window open** - the server needs to keep running.

### Step 1.5: Verify Backend is Running

Open a new terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# Or open in browser:
# http://localhost:8000/health
# http://localhost:8000/docs (Interactive API documentation)
```

You should see:
```json
{
  "status": "healthy",
  "predictor_initialized": true,
  "cds_api_configured": true
}
```

✅ **Backend is ready!** Keep it running and move to frontend setup.

---

## 🎨 Part 2: Frontend Setup

### Step 2.1: Install Node Dependencies

Open a **new terminal** (keep backend running in the first one):

```bash
cd frontend
npm install
```

This will install:
- React 18
- TypeScript
- Vite (build tool)
- Tailwind CSS
- React Leaflet (maps)
- Recharts (charts)
- Axios (HTTP client)

**Expected output:** Should complete without errors. Takes 1-2 minutes.

### Step 2.2: Verify Frontend Configuration

The frontend is already configured to connect to `http://localhost:8000` by default.

Check `frontend/src/services/api.ts` - line 3:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

If your backend runs on a different port, create `frontend/.env`:
```
VITE_API_URL=http://localhost:YOUR_PORT
```

### Step 2.3: Start the Frontend Server

From the `frontend` directory:

```bash
npm run dev
```

**Expected output:**
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

✅ **Frontend is ready!**

---

## 🌐 Part 3: Using the Application

### Step 3.1: Open the App

1. Open your browser: **http://localhost:3000**

2. You should see the FLUD dashboard with:
   - Header with "Use Mock Data" toggle
   - Location input form
   - Interactive map

### Step 3.2: Test with Mock Data First (Recommended)

1. **Enable "Use Mock Data"** toggle (top right)
2. Enter any coordinates (e.g., `16.5062`, `80.6480`)
3. Click **"Analyze Flood Risk"**
4. You should see results immediately with sample data

✅ **Frontend is working!**

### Step 3.3: Connect to Real Backend

1. **Disable "Use Mock Data"** toggle
2. Make sure backend is running (check terminal - should see server logs)
3. Enter coordinates:
   - Latitude: `16.5062`
   - Longitude: `80.6480`
   - Days: `7`
4. Click **"Analyze Flood Risk"**

**First request will take a few minutes** - the backend needs to:
- Fetch weather data from CDS API
- Process GRIB files
- Calculate flood risk
- (Optional) Query Ollama for AI analysis

**Expected behavior:**
- Loading spinner appears
- After 2-5 minutes, results appear
- You see comprehensive flood risk assessment

---

## 🤖 Part 4: Optional - Ollama AI Setup

For enhanced AI-powered flood analysis:

### Step 4.1: Install Ollama

1. Download from https://ollama.ai/
2. Install and start Ollama
3. Pull the required model:
   ```bash
   ollama pull gemma3:12b
   ```
   (This downloads ~7GB - takes time on first run)

### Step 4.2: Start Ollama Server

```bash
ollama serve
```

Keep it running. The backend will automatically detect and use it.

### Step 4.3: Verify Ollama Integration

The backend will use Ollama if available. Check backend terminal logs - you'll see:
```
[INFO] Querying Ollama for AI analysis...
```

If Ollama is not available, the backend will use deterministic analysis (still works, just without AI insights).

---

## ✅ Verification Checklist

Run through this checklist to ensure everything works:

- [ ] Backend server running on port 8000
- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Frontend server running on port 3000
- [ ] Browser opens http://localhost:3000
- [ ] "Use Mock Data" works (shows results instantly)
- [ ] Backend connection works (disable mock data, wait for results)
- [ ] No CORS errors in browser console (F12 → Console tab)
- [ ] API documentation accessible: http://localhost:8000/docs

---

## 🔍 Troubleshooting

### Backend Issues

#### ❌ "ModuleNotFoundError: No module named 'cdsapi'"
**Solution:**
```bash
pip install -r requirements.txt
# Or activate virtual environment first
```

#### ❌ "Flood predictor not initialized. Check CDS API configuration."
**Solution:**
1. Check `.cdsapirc` file exists in home directory
2. Verify file format is correct (two lines: `url:` and `key:`)
3. Ensure credentials are valid (no spaces, correct format: `UID:KEY`)
4. Test with: `python -c "import cdsapi; c = cdsapi.Client(); print('OK')"`

#### ❌ "Address already in use" (Port 8000)
**Solution:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill

# Or change port in api_server.py (line 169: port=8000)
```

#### ❌ CDS API request fails / timeout
**Solution:**
- CDS API requests can take 5-10 minutes for first request
- Be patient - check backend terminal for progress
- Verify internet connection
- Check CDS API status: https://cds.climate.copernicus.eu/

### Frontend Issues

#### ❌ "npm install" fails
**Solution:**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### ❌ "Cannot connect to backend" / CORS errors
**Solution:**
1. Verify backend is running (check http://localhost:8000/health)
2. Check browser console (F12) for specific error
3. Verify `allow_origins` in `flood_model/api_server.py` includes your frontend URL
4. Try using mock data first to isolate the issue

#### ❌ Map not loading
**Solution:**
- Check browser console for errors
- Ensure internet connection (map tiles load from OpenStreetMap)
- Try refreshing the page

#### ❌ Charts not displaying
**Solution:**
- Check browser console for errors
- Verify data format matches expected structure
- Try mock data first to verify charts work

### Connection Issues

#### ❌ Frontend shows "Failed to predict flood risk"
**Check:**
1. Backend is running: http://localhost:8000/health
2. Browser console (F12) shows the actual error
3. Network tab (F12 → Network) shows the API call
4. Backend terminal shows the request was received

#### ❌ Request hangs / never completes
**This is normal for first request!**
- CDS API downloads can take 5-10 minutes
- Check backend terminal for progress logs
- Be patient - subsequent requests may be faster if data is cached

---

## 📁 Project Structure Reference

```
Flud/
├── flood_model/              # Backend Python code
│   ├── api_server.py        # FastAPI server (main entry)
│   ├── flood_predictor.py   # Core prediction logic
│   ├── START_BACKEND.md     # Detailed backend guide
│   └── ...
│
├── frontend/                 # Frontend React app
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── ...
│   ├── package.json         # Node dependencies
│   └── ...
│
├── requirements.txt         # Python dependencies
├── COMPLETE_SETUP_GUIDE.md  # This file
└── ...
```

---

## 🚀 Quick Start Commands

**Terminal 1 - Backend:**
```bash
cd flood_model
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Browser:**
- Open http://localhost:3000
- Enable "Use Mock Data" for testing
- Disable it to use real backend

---

## 📚 Additional Resources

- **Backend API Docs**: http://localhost:8000/docs (when backend is running)
- **CDS API Guide**: https://cds.climate.copernicus.eu/api-how-to
- **Ollama Setup**: https://ollama.ai/
- **Frontend README**: `frontend/README.md`
- **Backend README**: `flood_model/START_BACKEND.md`

---

## 🎯 Next Steps

Once everything is working:

1. **Try different coordinates** - Test various locations
2. **Adjust analysis period** - Change days (1-30)
3. **Explore visualizations** - Check charts and risk breakdowns
4. **Review AI recommendations** - If Ollama is enabled
5. **Customize** - Modify frontend components or backend logic

---

## 💡 Tips

- **Development**: Use "Mock Data" toggle for faster UI development
- **Testing**: Use real backend only when you need actual predictions
- **First Request**: Always takes longest (5-10 min) - subsequent ones may be faster
- **Logs**: Check terminal output for detailed progress information
- **API Docs**: Use http://localhost:8000/docs to test API directly

---

**Need Help?** Check the troubleshooting section above or review the detailed guides:
- `flood_model/START_BACKEND.md` - Backend setup details
- `frontend/README.md` - Frontend documentation
- `frontend/BACKEND_API.md` - API integration details

