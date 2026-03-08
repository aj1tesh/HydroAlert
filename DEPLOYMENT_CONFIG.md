# Deployment Configuration Guide

## Will the code work without changes?

**YES, the code will work exactly the same** - but you need to configure **3 environment variables** when deploying. No code changes needed!

## Required Configuration (Environment Variables)

### 1. Backend Environment Variables

#### CDS API Credentials
The `cdsapi` library automatically checks for these environment variables:

```bash
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2
CDS_API_KEY=your_uid:your_api_key
```

**OR** you can use the `.cdsapirc` file (but environment variables are easier for cloud deployment).

#### CORS Origins (Optional - has defaults)
```bash
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

If not set, defaults to localhost URLs (which is fine for development).

### 2. Frontend Environment Variables

#### Backend API URL
```bash
VITE_API_URL=https://your-backend-domain.com
```

If not set, defaults to `http://localhost:8000` (which won't work in production).

## What Works Automatically (No Changes Needed)

✅ **All the core functionality:**
- Flood prediction logic
- GRIB file processing
- Weather data analysis
- Risk assessment calculations
- All API endpoints
- All frontend components
- Mock data mode

✅ **The code already handles:**
- Environment variables for API URLs
- Environment variables for CORS
- Fallback to localhost (for development)
- Error handling
- CDS API credential detection (checks both env vars and .cdsapirc)

## Platform-Specific Setup

### Railway
1. Go to your service → Variables
2. Add:
   - `CDS_API_URL` = `https://cds.climate.copernicus.eu/api/v2`
   - `CDS_API_KEY` = `your_uid:your_api_key`
   - `ALLOWED_ORIGINS` = `https://your-frontend.railway.app` (optional)
3. For frontend service:
   - `VITE_API_URL` = `https://your-backend.railway.app`

### Render
1. Go to your service → Environment
2. Add the same variables as above

### Vercel (Frontend)
1. Go to Project Settings → Environment Variables
2. Add:
   - `VITE_API_URL` = `https://your-backend-url.com`

### Docker
Create a `.env` file:
```env
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2
CDS_API_KEY=your_uid:your_api_key
ALLOWED_ORIGINS=http://localhost
VITE_API_URL=http://localhost:8000
```

Then run:
```bash
docker-compose up -d
```

## Testing After Deployment

1. **Backend Health Check:**
   ```
   https://your-backend-url.com/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Frontend:**
   - Open your frontend URL
   - Try the "Use Mock Data" checkbox first (to test frontend)
   - Then try a real prediction (to test backend + CDS API)

3. **If CDS API fails:**
   - Check that `CDS_API_KEY` is set correctly (format: `uid:key`)
   - Verify you've accepted terms on CDS website
   - Check backend logs for specific error messages

## Summary

**Code changes needed:** ❌ NONE

**Configuration needed:** ✅ 3 environment variables
- `CDS_API_URL` (backend)
- `CDS_API_KEY` (backend)  
- `VITE_API_URL` (frontend)

**Everything else:** ✅ Works automatically!
