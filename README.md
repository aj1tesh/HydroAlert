# FLUD - Flood Prediction System

A comprehensive flood prediction and risk assessment system using ERA5 weather data and AI analysis.

## Prerequisites

### Backend Requirements
- Python 3.8 or higher
- CDS API account and credentials (for ERA5 data access)

### Frontend Requirements
- Node.js 16+ and npm

## Setup Instructions

### 1. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure CDS API
The backend requires CDS (Copernicus Data Store) API credentials to fetch ERA5 weather data.

1. Create a CDS account at: https://cds.climate.copernicus.eu/
2. Get your API key from: https://cds.climate.copernicus.eu/api-how-to
3. Create a `.cdsapirc` file in your home directory:

**On Windows:**
```
C:\Users\YourUsername\.cdsapirc
```

**On Linux/Mac:**
```
~/.cdsapirc
```

4. Add your credentials to the file:
```ini
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

Replace `YOUR_UID` and `YOUR_API_KEY` with your actual credentials from the CDS website.

#### Test CDS API Connection (Optional)
```bash
cd flood_model
python test.py
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Project

### Start the Backend Server

```bash
cd flood_model
python api_server.py
```

The API server will start on `http://localhost:8000`

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Start the Frontend Development Server

Open a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173` (or another port if 5173 is busy)

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Enter coordinates (latitude and longitude) or click on the map to select a location
3. Choose the analysis period (1-30 days)
4. Click "Analyze Flood Risk"
5. View the comprehensive flood risk assessment including:
   - Overall risk score
   - Severity breakdown (minor/moderate/severe)
   - Time-windowed forecasts (24h, 48h, 72h, 7 days)
   - Weather data analysis
   - Confidence intervals

### Mock Data Mode

If CDS API is not configured, you can use the "Use Mock Data" checkbox to see the interface with sample data.

## Project Structure

```
Flud/
├── flood_model/          # Backend Python code
│   ├── api_server.py     # FastAPI server
│   └── flood_predictor.py # Flood prediction logic
├── frontend/             # React frontend
│   └── src/
│       ├── pages/        # Page components
│       └── components/   # Reusable components
└── requirements.txt      # Python dependencies
```

## Troubleshooting

### Backend Issues

**CDS API not configured:**
- Make sure `.cdsapirc` file exists in your home directory
- Verify your API key is correct
- Check that you've accepted the terms of use on the CDS website

**Port 8000 already in use:**
- Change the port in `api_server.py` (line 168) or stop the process using port 8000

### Frontend Issues

**Port 5173 already in use:**
- Vite will automatically use the next available port
- Or specify a port: `npm run dev -- --port 3000`

**API connection errors:**
- Ensure the backend is running on `http://localhost:8000`
- Check CORS settings in `api_server.py` if using a different frontend port
- Use mock data mode if CDS API is not available

## Environment Variables

### Frontend
Create a `.env` file in the `frontend/` directory (optional):
```
VITE_API_URL=http://localhost:8000
```

## Notes

- ERA5 data has a delay of ~5-7 days, so predictions use historical data
- The system downloads GRIB files temporarily and processes them
- GRIB files are automatically cleaned up after processing
