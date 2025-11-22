# 🚀 FLUD - Start Here

Welcome to FLUD (Flood Prediction System)! This guide will get you up and running quickly.

## ⚡ Quick Start (3 Steps)

### 1️⃣ Start Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Configure CDS API (one-time setup)
# Create ~/.cdsapirc with your CDS credentials
# See flood_model/START_BACKEND.md for details

# Start server
cd flood_model
python api_server.py
```

✅ Backend running at **http://localhost:8000**

### 2️⃣ Start Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at **http://localhost:3000**

### 3️⃣ Use the App

1. Open http://localhost:3000
2. **Disable "Use Mock Data"** toggle
3. Enter coordinates or click map
4. Click "Analyze Flood Risk"

## 📚 Documentation

- **Quick Start**: `QUICK_START.md` - Complete setup guide
- **Backend Setup**: `flood_model/START_BACKEND.md` - Detailed backend instructions
- **Frontend Docs**: `frontend/README.md` - Frontend documentation
- **API Reference**: `frontend/BACKEND_API.md` - API integration guide

## 🛠️ Troubleshooting

**Backend won't start?**
- Check CDS API is configured (`.cdsapirc` file)
- Install dependencies: `pip install -r requirements.txt`
- See `flood_model/START_BACKEND.md`

**Frontend can't connect?**
- Ensure backend is running on port 8000
- Check browser console (F12) for errors
- Try enabling "Use Mock Data" to test frontend

**Need help?**
- Check the detailed guides above
- Review error messages in terminal/browser console
- API docs available at http://localhost:8000/docs (when backend is running)

## 📁 Project Structure

```
Flud/
├── flood_model/          # Backend Python code
│   ├── api_server.py     # FastAPI server
│   └── flood_predictor.py # Prediction logic
├── frontend/             # React frontend
│   └── src/              # React components
├── requirements.txt      # Python dependencies
└── QUICK_START.md        # Full setup guide
```

## 🎯 What You Need

- Python 3.8+ ✅
- Node.js 18+ ✅
- CDS API account (free) - https://cds.climate.copernicus.eu/
- Ollama (optional, for AI analysis)

---

**Ready?** Follow the 3 steps above or read `QUICK_START.md` for detailed instructions!

