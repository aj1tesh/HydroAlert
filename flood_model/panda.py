import cdsapi
import xarray as xr
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuration
LAT = 16.5062  # Example latitude (center point)
LON = 80.6480  # Example longitude (center point)
AREA = [
    LAT + 0.5,  # North
    LON - 0.5,  # West
    LAT - 0.5,  # South
    LON + 0.5   # East (1x1 degree buffer around center)
]
START_YEAR = 2021
END_YEAR = 2024  # 4 full years of data
OUTPUT_CSV = 'era5_4years_weather_data.csv'

# Initialize CDS client
c = cdsapi.Client()

# List to collect all data rows
all_data = []

print(f"[INFO] Fetching ERA5 data for {START_YEAR}-{END_YEAR} at center ({LAT}, {LON})")

for year in range(START_YEAR, END_YEAR + 1):
    print(f"[INFO] Processing year {year}...")
    grib_file = f'era5_{year}.grib'
    
    try:
        # Retrieve data for the year (all months, all days, 6-hourly times)
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': [
                    'total_precipitation',       # tp: total precipitation (m)
                    '2m_temperature',            # t2m: 2m temperature (K)
                    'soil_temperature_level_1',  # stl1: soil temperature level 1 (K)
                    'volumetric_soil_water_layer_1',  # swvl1: volumetric soil water layer 1 (m^3/m^3)
                ],
                'year': [str(year)],
                'month': [f'{m:02d}' for m in range(1, 13)],
                'day': [f'{d:02d}' for d in range(1, 32)],  # CDS skips invalid dates (e.g., Feb 30)
                'time': ['00:00', '06:00', '12:00', '18:00'],
                'area': AREA,
                'format': 'grib',
            },
            grib_file
        )
        
        if not os.path.exists(grib_file) or os.path.getsize(grib_file) == 0:
            raise ValueError(f"Failed to download data for {year}")
        
        print(f"[INFO] Loaded GRIB file for {year} (size: {os.path.getsize(grib_file)} bytes)")
        
        # Open the multi-variable GRIB dataset
        ds = xr.open_dataset(grib_file, engine='cfgrib')
        
        # Extract timestamps
        times = pd.to_datetime(ds.time.values)
        
        # Compute spatial averages (mean over latitude/longitude) and apply unit conversions
        # total_precipitation: m -> mm
        precip_mm = (ds['tp'].mean(dim=['latitude', 'longitude']) * 1000).values if 'tp' in ds.data_vars else np.full(len(times), np.nan)
        
        # 2m_temperature: K -> °C
        temp_c = (ds['t2m'].mean(dim=['latitude', 'longitude']) - 273.15).values if 't2m' in ds.data_vars else np.full(len(times), np.nan)
        
        # soil_temperature_level_1: keep in K (as original)
        soil_temp_k = ds['stl1'].mean(dim=['latitude', 'longitude']).values if 'stl1' in ds.data_vars else np.full(len(times), np.nan)
        
        # volumetric_soil_water_layer_1: keep in m³/m³ (as original)
        soil_water_m3m3 = ds['swvl1'].mean(dim=['latitude', 'longitude']).values if 'swvl1' in ds.data_vars else np.full(len(times), np.nan)
        
        # Create rows for this year
        for i, timestamp in enumerate(times):
            row = {
                'datetime': timestamp,
                'lat': LAT,  # Center point (constant)
                'lon': LON,  # Center point (constant)
                'precip_mm': float(precip_mm[i]),
                'temp_c': float(temp_c[i]),
                'soil_temp_k': float(soil_temp_k[i]),
                'soil_water_m3m3': float(soil_water_m3m3[i])
            }
            all_data.append(row)
        
        # Close dataset and clean up temporary file
        ds.close()
        os.remove(grib_file)
        print(f"[SUCCESS] Processed {len(times)} timesteps for {year}")
        
    except Exception as e:
        print(f"[ERROR] Failed to process {year}: {e}")
        if os.path.exists(grib_file):
            os.remove(grib_file)

# Compile into DataFrame and save to CSV
if all_data:
    df = pd.DataFrame(all_data)
    df = df.sort_values('datetime')  # Ensure chronological order
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[SUCCESS] Saved {len(df)} rows to {OUTPUT_CSV}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print("\nColumns:")
    print(df.columns.tolist())
else:
    print("[ERROR] No data collected. Check CDS API configuration and quotas.")

# Optional: Print sample data
if len(all_data) > 0:
    print("\nSample data (first 5 rows):")
    print(df.head())