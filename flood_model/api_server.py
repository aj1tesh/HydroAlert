from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flood_predictor import FloodPredictor

app = FastAPI(
    title="FLUD API",
    description="Flood Prediction and Risk Assessment API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = None

def get_predictor():
    """Lazy initialization of predictor"""
    global predictor
    if predictor is None:
        try:
            predictor = FloodPredictor()
        except Exception as e:
            print(f"[WARNING] Failed to initialize FloodPredictor: {e}")
            print("[INFO] Make sure CDS API is configured (see .cdsapirc)")
    return predictor


class PredictionRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    days: int = Field(default=7, ge=1, le=30, description="Analysis period in days (1-30)")


@app.get("/")
async def root():
    return {
        "name": "FLUD API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/api/predict": "POST - Predict flood risk for given coordinates",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }


@app.get("/health")
async def health_check():
    predictor = get_predictor()
    return {
        "status": "healthy",
        "predictor_initialized": predictor is not None,
        "cds_api_configured": predictor is not None
    }


@app.post("/api/predict")
async def predict_flood(request: PredictionRequest):
    try:
        predictor = get_predictor()
        if predictor is None:
            raise HTTPException(
                status_code=503,
                detail="Flood predictor not initialized. Check CDS API configuration."
            )
        
        if not (-90 <= request.lat <= 90):
            raise HTTPException(
                status_code=400,
                detail="Latitude must be between -90 and 90"
            )
        
        if not (-180 <= request.lon <= 180):
            raise HTTPException(
                status_code=400,
                detail="Longitude must be between -180 and 180"
            )
        
        if not (1 <= request.days <= 30):
            raise HTTPException(
                status_code=400,
                detail="Days must be between 1 and 30"
            )
        
        print(f"\n[API] Received prediction request: lat={request.lat}, lon={request.lon}, days={request.days}")
        
        result = predictor.predict_flood(
            lat=request.lat,
            lon=request.lon,
            days=request.days
        )
        
        print(f"[API] Prediction completed successfully")
        
        return result
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"[API ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("FLUD Backend API Server")
    print("="*60)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

