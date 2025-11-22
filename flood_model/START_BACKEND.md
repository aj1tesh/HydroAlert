# Starting the FLUD Backend Server

This guide will help you start the backend API server so the frontend can connect to it.

## Prerequisites

1. **Python 3.8+** installed
2. **CDS API credentials** configured (see CDS API setup below)
3. **Ollama** (optional, for AI analysis) - running on `http://localhost:11434`

## Step 1: Install Dependencies

From the project root directory:

```bash
pip install -r requirements.txt
```

Or if you prefer a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure CDS API

The backend needs CDS (Copernicus Data Store) API credentials to fetch weather data.

1. **Create a CDS account** at https://cds.climate.copernicus.eu/
2. **Get your API key** from https://cds.climate.copernicus.eu/api-how-to
3. **Create `.cdsapirc` file** in your home directory:

**On Windows:**
```
C:\Users\YourUsername\.cdsapirc
```

**On Linux/Mac:**
```
~/.cdsapirc
```

**File content:**
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

Replace `YOUR_UID` and `YOUR_API_KEY` with your actual credentials.

## Step 3: Start the Backend Server

Navigate to the `flood_model` directory:

```bash
cd flood_model
```

Start the server:

```bash
python api_server.py
```

Or using uvicorn directly:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
============================================================
FLUD Backend API Server
============================================================
Starting server on http://localhost:8000
API Documentation: http://localhost:8000/docs
============================================================
```

## Step 4: Verify the Server is Running

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **View API documentation:**
   Open http://localhost:8000/docs in your browser

3. **Test the predict endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/predict \
     -H "Content-Type: application/json" \
     -d '{"lat": 16.5062, "lon": 80.6480, "days": 7}'
   ```

## Step 5: Start the Frontend

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Troubleshooting

### CDS API Not Configured

**Error:** `Flood predictor not initialized. Check CDS API configuration.`

**Solution:**
- Verify `.cdsapirc` file exists in your home directory
- Check that the file contains valid credentials
- Ensure the format is: `url: ...` and `key: UID:API_KEY`

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
- Change the port in `api_server.py` (line with `port=8000`)
- Or kill the process using port 8000:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -ti:8000 | xargs kill
  ```

### Ollama Not Running (Optional)

If Ollama is not running, the AI interpretation will be skipped, but the prediction will still work with deterministic analysis.

To start Ollama:
```bash
ollama serve
```

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate your virtual environment if using one
- Check Python version: `python --version` (should be 3.8+)

### CORS Errors in Frontend

If you see CORS errors, ensure:
- The frontend URL is in the `allow_origins` list in `api_server.py`
- The backend is running on the correct port (8000)

## Running in Production

For production, use a production ASGI server:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use gunicorn with uvicorn workers:

```bash
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `POST /api/predict` - Predict flood risk

See `frontend/BACKEND_API.md` for detailed API documentation.

