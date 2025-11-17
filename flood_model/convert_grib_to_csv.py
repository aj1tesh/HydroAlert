import xarray as xr
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuration (update paths if needed)
LAT = 16.5062  # Center point
LON = 80.6480  # Center point
START_YEAR = 2021
END_YEAR = 2024
OUTPUT_CSV = 'era5_4years_weather_data.csv'  # Final merged CSV

# List to collect all data rows
all_data = []

print(f"[INFO] Converting existing ERA5 GRIB/.idx files to CSV for {START_YEAR}-{END_YEAR}")

for year in range(START_YEAR, END_YEAR + 1):
    grib_file = f'era5_{year}.grib'  # Assumes .grib exists alongside .idx
    idx_file = f'era5_{year}.idx'    # The .idx is auto-used by cfgrib
    
    if not os.path.exists(grib_file):
        print(f"[WARNING] GRIB file missing for {year}: {grib_file}. Skipping.")
        continue
    
    if os.path.getsize(grib_file) == 0:
        print(f"[WARNING] Empty GRIB file for {year}. Skipping.")
        continue
    
    print(f"[INFO] Processing {grib_file} (with {idx_file} index)...")
    
    try:
        # Open the multi-variable GRIB dataset (cfgrib uses .idx automatically)
        ds = xr.open_dataset(grib_file, engine='cfgrib')
        
        # Extract timestamps
        times = pd.to_datetime(ds.time.values)
        
        # Compute spatial averages and unit conversions
        # total_precipitation: m -> mm
        precip_mm = (ds['tp'].mean(dim=['latitude', 'longitude']) * 1000).values if 'tp' in ds.data_vars else np.full(len(times), np.nan)
        
        # 2m_temperature: K -> °C
        temp_c = (ds['t2m'].mean(dim=['latitude', 'longitude']) - 273.15).values if 't2m' in ds.data_vars else np.full(len(times), np.nan)
        
        # soil_temperature_level_1: K (original)
        soil_temp_k = ds['stl1'].mean(dim=['latitude', 'longitude']).values if 'stl1' in ds.data_vars else np.full(len(times), np.nan)
        
        # volumetric_soil_water_layer_1: m³/m³ (original)
        soil_water_m3m3 = ds['swvl1'].mean(dim=['latitude', 'longitude']).values if 'swvl1' in ds.data_vars else np.full(len(times), np.nan)
        
        # Create rows for this year
        for i, timestamp in enumerate(times):
            row = {
                'datetime': timestamp,
                'lat': LAT,
                'lon': LON,
                'precip_mm': float(precip_mm[i]),
                'temp_c': float(temp_c[i]),
                'soil_temp_k': float(soil_temp_k[i]),
                'soil_water_m3m3': float(soil_water_m3m3[i])
            }
            all_data.append(row)
        
        # Close dataset
        ds.close()
        print(f"[SUCCESS] Processed {len(times)} timesteps for {year}")
        
        # Optional: Clean up files after processing
        # os.remove(grib_file)  # Uncomment to delete .grib
        # os.remove(idx_file)   # Uncomment to delete .idx
        
    except Exception as e:
        print(f"[ERROR] Failed to process {year}: {e}")
        continue

# Compile into DataFrame and save to CSV
if all_data:
    df = pd.DataFrame(all_data)
    df = df.sort_values('datetime')  # Chronological order
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[SUCCESS] Merged {len(df)} rows into {OUTPUT_CSV}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print("\nColumns:", df.columns.tolist())
    
    # Sample preview
    print("\nFirst 5 rows:")
    print(df.head())
else:
    print("[ERROR] No data processed. Check if .grib files exist and are valid.")

# Cleanup .idx files (optional, if you want to delete them now)
for year in range(START_YEAR, END_YEAR + 1):
    idx_file = f'era5_{year}.idx'
    if os.path.exists(idx_file):
        os.remove(idx_file)
        print(f"[INFO] Deleted {idx_file}")