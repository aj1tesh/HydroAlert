# FLUD Backend Setup Guide

Quick reference for setting up and running the FLUD backend API server.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure CDS API:**
   - Create account at https://cds.climate.copernicus.eu/
   - Add credentials to `~/.cdsapirc` (or `C:\Users\YourUsername\.cdsapirc` on Windows)
   - Format: `url: https://cds.climate.copernicus.eu/api/v2` and `key: YOUR_UID:YOUR_API_KEY`

3. **Start the server:**
   ```bash
   cd flood_model
   python api_server.py
   ```

4. **Verify it's working:**
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs

## File Structure

```
flood_model/
├── api_server.py          # FastAPI server
├── flood_predictor.py     # Main prediction logic
├── START_BACKEND.md       # Detailed setup guide
└── ...

requirements.txt           # Python dependencies
start_backend.bat         # Windows startup script
start_backend.sh          # Linux/Mac startup script
```

## API Endpoints

- `POST /api/predict` - Main prediction endpoint
  - Request: `{"lat": 16.5062, "lon": 80.6480, "days": 7}`
  - Returns: Comprehensive flood risk assessment

- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `cdsapi` - Copernicus Data Store API client
- `xarray`, `cfgrib` - GRIB file handling
- `numpy`, `pandas` - Data processing

## Optional: Ollama for AI Analysis

The backend can use Ollama for AI-powered flood analysis:

1. Install Ollama: https://ollama.ai/
2. Pull the model: `ollama pull gemma3:12b`
3. Start Ollama: `ollama serve`
4. The backend will automatically use it if available

## Troubleshooting

See `flood_model/START_BACKEND.md` for detailed troubleshooting guide.

Common issues:
- **CDS API not configured** → Check `.cdsapirc` file
- **Port 8000 in use** → Change port in `api_server.py`
- **Import errors** → Install dependencies: `pip install -r requirements.txt`
- **CORS errors** → Check `allow_origins` in `api_server.py`

## Next Steps

1. Start the backend: `cd flood_model && python api_server.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000 in your browser
4. Disable "Use Mock Data" toggle to connect to the backend

