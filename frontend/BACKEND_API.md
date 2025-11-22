# Backend API Integration Guide

This document describes the API endpoint that the frontend expects from the backend.

## Endpoint

**POST** `/api/predict`

## Request Body

```json
{
  "lat": 16.5062,
  "lon": 80.6480,
  "days": 7
}
```

### Parameters

- `lat` (number, required): Latitude coordinate (-90 to 90)
- `lon` (number, required): Longitude coordinate (-180 to 180)
- `days` (number, optional): Analysis period in days (default: 7, max: 30)

## Response

The API should return a JSON object matching the `FloodPredictionResult` interface:

```typescript
{
  location: {
    lat: number,
    lon: number
  },
  timestamp: string,  // ISO 8601 format
  analysis_period_days: number,
  weather_analysis: {
    total_precipitation_mm: number,
    max_hourly_precip_mm: number,
    avg_precipitation_mm: number,
    precip_days: number,
    avg_temperature_c: number,
    min_temperature_c: number,
    avg_soil_moisture: number,
    max_soil_moisture: number,
    soil_saturation_ratio: number,
    time_series?: {
      precipitation_mm?: number[],
      soil_moisture?: number[]
    }
  },
  risk_assessment: {
    severity_levels: {
      overall: number,  // 0-1
      minor_flooding: {
        probability: number,  // 0-1
        description: string
      },
      moderate_flooding: {
        probability: number,  // 0-1
        description: string
      },
      severe_flooding: {
        probability: number,  // 0-1
        description: string
      }
    },
    time_windows: {
      next_24_hours: {
        probability: number,  // 0-1
        description: string
      },
      next_48_hours: {
        probability: number,  // 0-1
        description: string
      },
      next_72_hours: {
        probability: number,  // 0-1
        description: string
      },
      next_7_days: {
        probability: number,  // 0-1
        description: string
      }
    },
    confidence: {
      probability_estimate: number,  // 0-1
      lower_bound: number,  // 0-1
      upper_bound: number,  // 0-1
      margin_of_error: number,  // 0-1
      confidence_level: string,  // "low" | "medium" | "high"
      interpretation: string
    },
    risk_factors: string[],
    overall_risk_score: number  // 0-1
  },
  ai_interpretation: {
    overall_assessment?: string,
    severity_analysis?: string,
    temporal_analysis?: string,
    confidence_notes?: string,
    recommended_actions?: string[],
    key_concerns?: string[],
    monitoring_priorities?: string[]
  }
}
```

## Error Response

If an error occurs, return a JSON object with an `error` field:

```json
{
  "error": "Error message describing what went wrong"
}
```

Status code should be 4xx or 5xx.

## Example Flask/FastAPI Implementation

### Flask Example

```python
from flask import Flask, request, jsonify
from flood_model.flood_predictor import FloodPredictor

app = Flask(__name__)
predictor = FloodPredictor()

@app.route('/api/predict', methods=['POST'])
def predict_flood():
    try:
        data = request.get_json()
        lat = float(data['lat'])
        lon = float(data['lon'])
        days = int(data.get('days', 7))
        
        if not (-90 <= lat <= 90):
            return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        if not (-180 <= lon <= 180):
            return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        if not (1 <= days <= 30):
            return jsonify({'error': 'Days must be between 1 and 30'}), 400
        
        result = predictor.predict_flood(lat, lon, days)
        return jsonify(result)
    
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)
```

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flood_model.flood_predictor import FloodPredictor

app = FastAPI()
predictor = FloodPredictor()

class PredictionRequest(BaseModel):
    lat: float
    lon: float
    days: int = 7

@app.post('/api/predict')
async def predict_flood(request: PredictionRequest):
    try:
        if not (-90 <= request.lat <= 90):
            raise HTTPException(status_code=400, detail='Latitude must be between -90 and 90')
        if not (-180 <= request.lon <= 180):
            raise HTTPException(status_code=400, detail='Longitude must be between -180 and 180')
        if not (1 <= request.days <= 30):
            raise HTTPException(status_code=400, detail='Days must be between 1 and 30')
        
        result = predictor.predict_flood(request.lat, request.lon, request.days)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## CORS Configuration

If your backend is on a different origin, make sure to enable CORS:

### Flask-CORS

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

### FastAPI

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing

You can test the API using curl:

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"lat": 16.5062, "lon": 80.6480, "days": 7}'
```

Or using the frontend's mock data toggle to see the expected response format.

