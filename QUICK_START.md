# FLUD - Quick Start Guide

Get both the frontend and backend running in minutes!

## Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **CDS API account** (for weather data) - https://cds.climate.copernicus.eu/

## Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 1.2 Configure CDS API

1. Create account at https://cds.climate.copernicus.eu/
2. Get your API credentials
3. Create `.cdsapirc` file in your home directory:

**Windows:** `C:\Users\YourUsername\.cdsapirc`  
**Linux/Mac:** `~/.cdsapirc`

**File content:**
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

### 1.3 Start Backend Server

**Option A: Using the startup script**
```bash
# Windows
start_backend.bat

# Linux/Mac
chmod +x start_backend.sh
./start_backend.sh
```

**Option B: Manual start**
```bash
cd flood_model
python api_server.py
```

The backend will start at **http://localhost:8000**

Verify it's working:
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

### 2.2 Start Frontend

```bash
npm run dev
```

The frontend will start at **http://localhost:3000**

## Step 3: Use the Application

1. Open http://localhost:3000 in your browser
2. **Disable "Use Mock Data"** toggle (top right)
3. Enter coordinates or click on the map
4. Click "Analyze Flood Risk"
5. Wait for the analysis (may take a few minutes for first request)

## Optional: Ollama AI Analysis

For AI-powered flood analysis:

1. Install Ollama: https://ollama.ai/
2. Pull model: `ollama pull gemma3:12b`
3. Start Ollama: `ollama serve`
4. Backend will automatically use it if available

## Troubleshooting

### Backend Issues

- **CDS API error**: Check `.cdsapirc` file exists and has correct credentials
- **Port 8000 in use**: Change port in `flood_model/api_server.py`
- **Import errors**: Run `pip install -r requirements.txt`

### Frontend Issues

- **Can't connect to backend**: 
  - Ensure backend is running on port 8000
  - Check browser console for CORS errors
  - Verify "Use Mock Data" is disabled
- **Map not loading**: Check browser console for errors

### Both Running But Not Connecting

1. Check backend is running: http://localhost:8000/health
2. Check frontend is running: http://localhost:3000
3. Open browser DevTools (F12) → Network tab → Check for errors
4. Verify CORS settings in `flood_model/api_server.py`

## File Structure

```
Flud/
├── flood_model/
│   ├── api_server.py          # Backend API server
│   ├── flood_predictor.py     # Prediction logic
│   └── START_BACKEND.md        # Detailed backend guide
├── frontend/
│   ├── src/                    # React app source
│   └── README.md               # Frontend documentation
├── requirements.txt            # Python dependencies
├── start_backend.bat          # Windows startup
├── start_backend.sh           # Linux/Mac startup
└── QUICK_START.md             # This file
```

## Next Steps

- **Backend details**: See `flood_model/START_BACKEND.md`
- **Frontend details**: See `frontend/README.md`
- **API documentation**: See `frontend/BACKEND_API.md`
- **Backend API docs**: http://localhost:8000/docs (when running)

## Development Tips

1. **Use Mock Data**: Enable "Use Mock Data" in frontend to develop UI without backend
2. **API Testing**: Use http://localhost:8000/docs for interactive API testing
3. **Hot Reload**: Both frontend and backend support hot reload on code changes
4. **Logs**: Check terminal output for detailed logs from both servers

