import cdsapi
import xarray as xr
import numpy as np
import json
import requests
from datetime import datetime, timezone

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:12b"                                   
TIMEZONE = "UTC"
RETURN_PERIOD = 2                                             

def get_bounding_box(lat, lon, delta=0.1):
    """Small bounding box around point to subset data"""
    return [lat + delta, lon - delta, lat - delta, lon + delta]

def fetch_historical_discharge(lat, lon):
    """Fetch historical GloFAS data to compute return period threshold"""
    area = get_bounding_box(lat, lon)
    c = cdsapi.Client()
    years = [str(y) for y in range(1995, 2025)] 
    months = [f'{m:02d}' for m in range(1, 13)]
    days = [f'{d:02d}' for d in range(1, 32)]
    print(f"Fetching historical GloFAS data for {lat},{lon}...")
    c.retrieve(
        'cems-glofas-historical',
        {
            'system_version': 'version_4_0',
            'hydrological_model': 'lisflood',
            'product_type': 'consolidated',
            'variable': 'river_discharge_in_the_last_24_hours',
            'year': years,
            'month': months,
            'day': days,
            'area': area,
            'format': 'netcdf',
        },
        'historical.nc'
    )
    ds = xr.open_dataset('historical.nc')
    point = ds.sel(latitude=lat, longitude=lon, method='nearest')
    return point['dis24']

def compute_flood_threshold(historical_discharge, return_period=RETURN_PERIOD):
    """Compute return period threshold from annual maxima"""
    # Extract annual maxima
    annual_max = historical_discharge.resample(time='1Y').max().values
    annual_max = annual_max[~np.isnan(annual_max)]
    if len(annual_max) < 10:
        raise ValueError("Not enough historical data for reliable threshold")
    # Percentile for return period T: (1 - 1/T) * 100
    percentile = (1 - 1 / return_period) * 100
    threshold = np.percentile(annual_max, percentile)
    return float(threshold)

def fetch_forecast_discharge(lat, lon, days=7):
    """Fetch ensemble forecast from GloFAS via CDS"""
    area = get_bounding_box(lat, lon)
    today = datetime.now()
    year = str(today.year)
    month = f'{today.month:02d}'
    day = f'{today.day:02d}'
    leadtimes = [str(i * 24) for i in range(1, days + 1)]
    c = cdsapi.Client()
    print(f"Fetching forecast GloFAS data for {lat},{lon}...")
    c.retrieve(
        'cems-glofas-forecast',
        {
            'system_version': 'version_4_0',
            'hydrological_model': 'lisflood',
            'product_type': ['control_forecast', 'ensemble_perturbed_forecasts'],
            'variable': 'river_discharge_in_the_last_24_hours',
            'year': year,
            'month': month,
            'day': day,
            'leadtime_hour': leadtimes,
            'area': area,
            'format': 'netcdf',
        },
        'forecast.nc'
    )
    ds = xr.open_dataset('forecast.nc')
    point = ds.sel(latitude=lat, longitude=lon, method='nearest')
    # Ensemble discharges: shape (number, step)
    ensemble = point['dis24'].values
    # Valid times
    base_time = ds['time'].values[0]
    steps = ds['step'].values
    times = [(np.datetime64(base_time) + step).astype('datetime64[ns]').item().isoformat() for step in steps]
    meta = {
        'units': ds['dis24'].attrs.get('units', 'm^3/s'),
        'source': 'GloFAS via CDSAPI',
        'grid_point': f"nearest to {lat},{lon}"
    }
    return times, ensemble, meta

def compute_exceedance_probability(ensemble, threshold):
    if ensemble.size == 0:
        return 0.0, None, 0.0
    exceed = ensemble > threshold
    frac_per_t = exceed.mean(axis=0)
    per_member_any = exceed.any(axis=1).astype(float)
    prob_any = per_member_any.mean()
    max_frac = frac_per_t.max()
    return float(prob_any), frac_per_t.tolist(), float(max_frac)

def call_ollama_explain(model, prompt, format_json=True, timeout=60):
    payload = {"model": model, "prompt": prompt, "stream": False}
    if format_json:
        payload["format"] = "json"
    headers = {"Content-Type": "application/json"}
    resp = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(payload), timeout=timeout)
    resp.raise_for_status()
    out = resp.json()
    if "response" in out and out["response"]:
        try:
            return json.loads(out["response"])
        except Exception:
            return out["response"]
    return out

# === Main high-level function ===

def predict_flood_probability_with_ollama(lat, lon, threshold=None, days=7, ollama_model=OLLAMA_MODEL, return_period=RETURN_PERIOD):
    auto_thresh_used = False
    if threshold is None:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching historical data for threshold...")
        hist_discharge = fetch_historical_discharge(lat, lon)
        threshold = compute_flood_threshold(hist_discharge, return_period=return_period)
        auto_thresh_used = True

    print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching GloFAS forecast data for {lat},{lon} ...")
    times, ensemble, meta = fetch_forecast_discharge(lat, lon, days=days)

    prob_any, frac_per_t, max_frac = compute_exceedance_probability(ensemble, threshold)

    # Prepare prompt for Ollama
    thresh_desc = f"{return_period}-year return period discharge (computed from historical annual maxima)" if auto_thresh_used else "user-provided"
    prompt = (
        f"You are a technical flood analyst. I give you numeric results from a GloFAS (CDSAPI) query for location "
        f"latitude={lat}, longitude={lon}.\n\n"
        f"Metadata: {json.dumps(meta)}\n\n"
        f"Forecast times (first 8 shown): {times[:8]}\n"
        f"Ensemble shape: members={ensemble.shape[0]}, timesteps={ensemble.shape[1]}\n"
        f"Computed summary:\n"
        f" - exceedance_threshold = {threshold} ({thresh_desc})\n"
        f" - probability_at_least_one_member_exceeds_threshold = {prob_any:.3f}\n"
        f" - max_fraction_of_members_exceeding_at_a_timestep = {max_frac:.3f}\n"
        f" - fraction_per_timestep_sample(first 8) = {frac_per_t[:8] if frac_per_t else None}\n\n"
        f"Please return a JSON object with these fields:\n"
        f"{{\n"
        f"  'location': {{'lat': {lat}, 'lon': {lon}}},\n"
        f"  'probability_any_exceed': <float 0-1>,\n"
        f"  'max_fraction_members_exceeding': <float 0-1>,\n"
        f"  'exceedance_threshold': <number>,\n"
        f"  'confidence_explanation': <string short explanation of confidence & caveats>,\n"
        f"  'recommended_action': <string: 'monitor'|'alert'|'no-action' etc.>,\n"
        f"  'raw_meta': <the metadata object>\n"
        f"}}\n\nBe concise. Use the numeric values above to fill the JSON. Do not invent other numeric probabilities."
    )

    try:
        ollama_out = call_ollama_explain(ollama_model, prompt, format_json=True)
    except Exception as e:
        ollama_out = {
            "location": {"lat": lat, "lon": lon},
            "probability_any_exceed": prob_any,
            "max_fraction_members_exceeding": max_frac,
            "exceedance_threshold": threshold,
            "confidence_explanation": f"Ollama call failed: {str(e)}. Numeric probability computed from GloFAS ensemble.",
            "recommended_action": "alert" if prob_any > 0.5 else "monitor" if prob_any > 0.1 else "no-action",
            "raw_meta": meta
        }

    if isinstance(ollama_out, dict):
        ollama_out["probability_any_exceed"] = prob_any
        ollama_out["max_fraction_members_exceeding"] = max_frac
        ollama_out["exceedance_threshold"] = threshold
        ollama_out["raw_meta"] = meta
    return ollama_out

if __name__ == "__main__":
    # Example coordinates
    lat = 26.8467
    lon = 80.9462

    result = predict_flood_probability_with_ollama(lat, lon, threshold=None, days=7, ollama_model=OLLAMA_MODEL)
    print("=== FINAL RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))