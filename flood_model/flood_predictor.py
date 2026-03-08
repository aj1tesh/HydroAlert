import cdsapi
import numpy as np
import json
from datetime import datetime, timedelta
import xarray as xr
import os
import math
import re


class FloodPredictor:
    def __init__(self):
        self.cds_client = cdsapi.Client()
    
    def _clean_json_values(self, obj):
        if isinstance(obj, dict):
            return {key: self._clean_json_values(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_json_values(item) for item in obj]
        elif isinstance(obj, float):
            if math.isnan(obj):
                return None
            elif math.isinf(obj):
                # Replace infinity with a large but reasonable number
                return 1e10 if obj > 0 else -1e10
            else:
                return obj
        elif isinstance(obj, np.floating):
            # Handle numpy float types
            if np.isnan(obj):
                return None
            elif np.isinf(obj):
                return 1e10 if obj > 0 else -1e10
            else:
                return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        else:
            return obj
        
    def fetch_weather_data(self, lat, lon, days=7):
        print(f"\n[INFO] Fetching weather data for coordinates: {lat}, {lon}")
        
        today = datetime.now()
        data_delay_days = 7
        latest_available_date = today - timedelta(days=data_delay_days)
        
        end_date = latest_available_date
        start_date = end_date - timedelta(days=days)
        
        if start_date.year < 1940:
            start_date = datetime(1940, 1, 1)
            print(f"[WARNING] Adjusted start date to 1940-01-01 (ERA5 data limit)")
        
        print(f"[INFO] Requesting data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"[INFO] Note: Using historical data due to ERA5 delay (~{data_delay_days} days)")
        
        years = list(set([start_date.strftime('%Y'), end_date.strftime('%Y')]))
        months = list(set([start_date.strftime('%m'), end_date.strftime('%m')]))
        
        current = start_date
        days_list = []
        while current <= end_date:
            days_list.append(current.strftime('%d'))
            current += timedelta(days=1)
        days_list = list(set(days_list))
        
        area = [
            lat + 0.5,  # North
            lon - 0.5,  # West
            lat - 0.5,  # South
            lon + 0.5   # East
        ]
        
        output_file = 'flood_data.grib'
        
        print("[INFO] Requesting data from CDS API...")
        try:
            self.cds_client.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        'total_precipitation',
                        '2m_temperature',
                        'soil_temperature_level_1',
                        'volumetric_soil_water_layer_1',
                    ],
                    'year': years,
                    'month': months,
                    'day': days_list,
                    'time': [
                        '00:00', '06:00', '12:00', '18:00'
                    ],
                    'area': area,
                    'format': 'grib',
                },
                output_file
            )
            print(f"[SUCCESS] Data downloaded to {output_file}")
            return output_file
        except Exception as e:
            error_msg = str(e)
            if "not available yet" in error_msg or "latest date available" in error_msg.lower():
                print(f"[ERROR] CDS API request failed: {e}")
                print(f"[INFO] ERA5 data has a delay. The error suggests using dates before the latest available date.")
                print(f"[INFO] Try reducing the number of days or using historical dates.")
                if "latest date available" in error_msg.lower():
                    try:
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', error_msg)
                        if date_match:
                            latest_date_str = date_match.group(1)
                            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
                            print(f"[INFO] Latest available date: {latest_date_str}")
                            print(f"[INFO] Retrying with adjusted date range...")
                            end_date = latest_date
                            start_date = end_date - timedelta(days=days)
                            
                            years = list(set([start_date.strftime('%Y'), end_date.strftime('%Y')]))
                            months = list(set([start_date.strftime('%m'), end_date.strftime('%m')]))
                            current = start_date
                            days_list = []
                            while current <= end_date:
                                days_list.append(current.strftime('%d'))
                                current += timedelta(days=1)
                            days_list = list(set(days_list))
                            
                            print(f"[INFO] Retrying with dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                            
                            self.cds_client.retrieve(
                                'reanalysis-era5-single-levels',
                                {
                                    'product_type': 'reanalysis',
                                    'variable': [
                                        'total_precipitation',
                                        '2m_temperature',
                                        'soil_temperature_level_1',
                                        'volumetric_soil_water_layer_1',
                                    ],
                                    'year': years,
                                    'month': months,
                                    'day': days_list,
                                    'time': [
                                        '00:00', '06:00', '12:00', '18:00'
                                    ],
                                    'area': area,
                                    'format': 'grib',
                                },
                                output_file
                            )
                            print(f"[SUCCESS] Data downloaded to {output_file} (using adjusted dates)")
                            return output_file
                    except Exception as retry_error:
                        print(f"[ERROR] Retry also failed: {retry_error}")
                        raise Exception(f"CDS API data availability error. Latest available date may be in the past. Original error: {error_msg}")
            
            print(f"[ERROR] CDS API request failed: {e}")
            raise
    
    def analyze_weather_data(self, grib_file):
        print("\n[INFO] Analyzing weather data...")
        
        if not os.path.exists(grib_file):
            raise FileNotFoundError(f"GRIB file not found: {grib_file}")
        
        file_size = os.path.getsize(grib_file)
        print(f"[INFO] GRIB file size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("GRIB file is empty")
        
        try:
            print("[INFO] Opening GRIB file with cfgrib engine...")
            
            analysis = {}
            time_series = {}
            
            variable_mapping = {
                'tp': 'total_precipitation',
                't2m': '2m_temperature', 
                'stl1': 'soil_temperature',
                'swvl1': 'soil_moisture'
            }
            
            datasets = {}
            for short_name, full_name in variable_mapping.items():
                try:
                    ds = xr.open_dataset(
                        grib_file, 
                        engine='cfgrib',
                        backend_kwargs={'filter_by_keys': {'shortName': short_name}}
                    )
                    datasets[short_name] = ds
                    print(f"[INFO] Loaded variable: {full_name} ({short_name})")
                except Exception as e:
                    print(f"[WARNING] Could not load {short_name}: {str(e)[:80]}")
            
            if not datasets:
                raise ValueError("Could not load any variables from GRIB file")
            
            if 'tp' in datasets:
                ds = datasets['tp']
                if 'tp' in ds.data_vars:
                    precip = ds['tp'].values
                    precip_mm = precip * 1000
                    
                    total_precip = np.nansum(precip_mm)
                    if np.all(np.isnan(precip_mm)):
                        max_precip = 0.0
                        avg_precip = 0.0
                    else:
                        max_precip = np.nanmax(precip_mm)
                        avg_precip = np.nanmean(precip_mm)
                    
                    analysis['total_precipitation_mm'] = float(total_precip) if not (math.isnan(total_precip) or math.isinf(total_precip)) else 0.0
                    analysis['max_hourly_precip_mm'] = float(max_precip) if not (math.isnan(max_precip) or math.isinf(max_precip)) else 0.0
                    analysis['avg_precipitation_mm'] = float(avg_precip) if not (math.isnan(avg_precip) or math.isinf(avg_precip)) else 0.0
                    analysis['precip_days'] = int(np.nansum(precip_mm > 1.0))
                    
                    if precip_mm.ndim >= 1:
                        if precip_mm.ndim == 3:
                            precip_time = np.nanmean(precip_mm, axis=(1, 2))
                        elif precip_mm.ndim == 2:
                            precip_time = np.nanmean(precip_mm, axis=1)
                        else:
                            precip_time = precip_mm
                        
                        precip_time = precip_time.flatten() if precip_time.ndim > 1 else precip_time
                        
                        def clean_value(x):
                            """Helper to clean a single value"""
                            if isinstance(x, (list, np.ndarray)):
                                x = np.nanmean(np.array(x))
                            if isinstance(x, np.floating):
                                if np.isnan(x):
                                    return None
                                return float(x)
                            elif isinstance(x, float):
                                if math.isnan(x):
                                    return None
                                return x
                            else:
                                try:
                                    val = float(x)
                                    if math.isnan(val):
                                        return None
                                    return val
                                except (ValueError, TypeError):
                                    return None
                        
                        time_series['precipitation_mm'] = [clean_value(x) for x in precip_time.tolist()]
                    
                    print(f"[INFO] Precipitation - Total: {analysis['total_precipitation_mm']:.2f}mm")
            
            if 't2m' in datasets:
                ds = datasets['t2m']
                if 't2m' in ds.data_vars:
                    temp = ds['t2m'].values
                    temp_c = temp - 273.15
                    if np.all(np.isnan(temp_c)):
                        avg_temp = 0.0
                        min_temp = 0.0
                    else:
                        avg_temp = np.nanmean(temp_c)
                        min_temp = np.nanmin(temp_c)
                    
                    analysis['avg_temperature_c'] = float(avg_temp) if not (math.isnan(avg_temp) or math.isinf(avg_temp)) else 0.0
                    analysis['min_temperature_c'] = float(min_temp) if not (math.isnan(min_temp) or math.isinf(min_temp)) else 0.0
                    print(f"[INFO] Temperature - Avg: {analysis['avg_temperature_c']:.1f}°C")
            
            if 'swvl1' in datasets:
                ds = datasets['swvl1']
                if 'swvl1' in ds.data_vars:
                    soil_moisture = ds['swvl1'].values
                    if np.all(np.isnan(soil_moisture)):
                        avg_soil = 0.0
                        max_soil = 0.0
                        sat_ratio = 0.0
                    else:
                        avg_soil = np.nanmean(soil_moisture)
                        max_soil = np.nanmax(soil_moisture)
                        sat_ratio = np.nanmean(soil_moisture > 0.4)
                    
                    analysis['avg_soil_moisture'] = float(avg_soil) if not (math.isnan(avg_soil) or math.isinf(avg_soil)) else 0.0
                    analysis['max_soil_moisture'] = float(max_soil) if not (math.isnan(max_soil) or math.isinf(max_soil)) else 0.0
                    analysis['soil_saturation_ratio'] = float(sat_ratio) if not (math.isnan(sat_ratio) or math.isinf(sat_ratio)) else 0.0
                    
                    if soil_moisture.ndim >= 1:
                        if soil_moisture.ndim == 3:
                            soil_time = np.nanmean(soil_moisture, axis=(1, 2))
                        elif soil_moisture.ndim == 2:
                            soil_time = np.nanmean(soil_moisture, axis=1)
                        else:
                            soil_time = soil_moisture
                        
                        soil_time = soil_time.flatten() if soil_time.ndim > 1 else soil_time
                        
                        def clean_value(x):
                            """Helper to clean a single value"""
                            if isinstance(x, (list, np.ndarray)):
                                x = np.nanmean(np.array(x))
                            if isinstance(x, np.floating):
                                if np.isnan(x):
                                    return None
                                return float(x)
                            elif isinstance(x, float):
                                if math.isnan(x):
                                    return None
                                return x
                            else:
                                try:
                                    val = float(x)
                                    if math.isnan(val):
                                        return None
                                    return val
                                except (ValueError, TypeError):
                                    return None
                        
                        time_series['soil_moisture'] = [clean_value(x) for x in soil_time.tolist()]
                    
                    print(f"[INFO] Soil Moisture - Avg: {analysis['avg_soil_moisture']:.3f}")
            
            for ds in datasets.values():
                ds.close()
            
            analysis['time_series'] = time_series
            print("[SUCCESS] Weather data analyzed")
            return analysis
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze GRIB data: {e}")
            raise
    
    def calculate_comprehensive_flood_risk(self, analysis):
        print("\n[INFO] Calculating comprehensive flood risk...")
        
        precip_total = analysis.get('total_precipitation_mm', 0)
        precip_max = analysis.get('max_hourly_precip_mm', 0)
        soil_sat = analysis.get('soil_saturation_ratio', 0)
        precip_days = analysis.get('precip_days', 0)
        
        severity_probs = self._calculate_severity_probabilities(
            precip_total, precip_max, soil_sat, precip_days
        )
        
        time_probs = self._calculate_time_windowed_probabilities(
            analysis.get('time_series', {}), precip_total, soil_sat
        )
        
        base_prob = severity_probs['overall']
        confidence_intervals = self._calculate_confidence_intervals(
            base_prob, precip_total, soil_sat, precip_days
        )
        
        risk_factors = []
        if precip_total > 50:
            risk_factors.append(f"High total precipitation: {precip_total:.1f}mm")
        if precip_max > 10:
            risk_factors.append(f"Intense rainfall: {precip_max:.1f}mm/6h")
        if soil_sat > 0.5:
            risk_factors.append(f"Saturated soil: {soil_sat*100:.0f}%")
        if precip_days > 3:
            risk_factors.append(f"Continuous rain: {precip_days} days")
        
        return {
            'severity_levels': severity_probs,
            'time_windows': time_probs,
            'confidence': confidence_intervals,
            'risk_factors': risk_factors,
            'overall_risk_score': base_prob
        }
    
    def _calculate_severity_probabilities(self, precip_total, precip_max, soil_sat, precip_days):
        precip_score = min(precip_total / 200, 1.0)
        intensity_score = min(precip_max / 30, 1.0)
        soil_score = soil_sat
        duration_score = min(precip_days / 7, 1.0)
        
        base_prob = (precip_score * 0.4 + intensity_score * 0.3 + 
                     soil_score * 0.2 + duration_score * 0.1)
        
        prob_minor = base_prob * 0.8 if base_prob > 0.2 else base_prob * 1.2
        prob_minor = min(prob_minor, 1.0)
        
        prob_moderate = base_prob * 0.6 if base_prob > 0.4 else base_prob * 0.3
        prob_moderate = min(prob_moderate, 1.0)
        
        prob_severe = base_prob * 0.4 if base_prob > 0.6 else base_prob * 0.1
        prob_severe = min(prob_severe, 1.0)
        
        return {
            'overall': base_prob,
            'minor_flooding': {
                'probability': prob_minor,
                'description': 'Water depth 0-30cm, roads passable with caution'
            },
            'moderate_flooding': {
                'probability': prob_moderate,
                'description': 'Water depth 30-100cm, road closures likely'
            },
            'severe_flooding': {
                'probability': prob_severe,
                'description': 'Water depth >100cm, evacuation may be needed'
            }
        }
    
    def _calculate_time_windowed_probabilities(self, time_series, precip_total, soil_sat):
        recent_precip_trend = 0
        if 'precipitation_mm' in time_series and len(time_series['precipitation_mm']) > 0:
            precip_data = time_series['precipitation_mm']
            if len(precip_data) >= 4:
                recent_avg = np.mean(precip_data[-2:])
                older_avg = np.mean(precip_data[:-2])
                recent_precip_trend = recent_avg - older_avg
        
        base = min((precip_total / 100) * 0.5 + soil_sat * 0.5, 1.0)
        
        trend_factor = 1.0 + (recent_precip_trend / 10)
        trend_factor = max(0.5, min(trend_factor, 2.0))
        
        prob_24h = min(base * 0.6 * trend_factor, 1.0)
        prob_48h = min(base * 0.8 * trend_factor, 1.0)
        prob_72h = min(base * 1.0 * trend_factor, 1.0)
        prob_7d = min(base * 1.2 * trend_factor, 1.0)
        
        return {
            'next_24_hours': {
                'probability': prob_24h,
                'description': 'Immediate risk assessment'
            },
            'next_48_hours': {
                'probability': prob_48h,
                'description': 'Short-term forecast'
            },
            'next_72_hours': {
                'probability': prob_72h,
                'description': 'Medium-term forecast'
            },
            'next_7_days': {
                'probability': prob_7d,
                'description': 'Extended forecast'
            }
        }
    
    def _calculate_confidence_intervals(self, base_prob, precip_total, soil_sat, precip_days):
        data_uncertainty = 0.15
        
        if precip_total > 100 or soil_sat > 0.7:
            data_uncertainty *= 0.7
        elif precip_total < 10 and soil_sat < 0.2:
            data_uncertainty *= 0.8
        else:
            data_uncertainty *= 1.2
        
        lower_bound = max(0, base_prob - data_uncertainty)
        upper_bound = min(1.0, base_prob + data_uncertainty)
        
        if data_uncertainty < 0.1:
            confidence_level = "high"
        elif data_uncertainty < 0.15:
            confidence_level = "medium"
        else:
            confidence_level = "low"
        
        return {
            'probability_estimate': base_prob,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'margin_of_error': data_uncertainty,
            'confidence_level': confidence_level,
            'interpretation': f"{base_prob*100:.1f}% (±{data_uncertainty*100:.1f}%)"
        }
    
    def predict_flood(self, lat, lon, days=7):
        print("="*60)
        print("COMPREHENSIVE FLOOD PREDICTION SYSTEM")
        print("="*60)
        print(f"Location: {lat}°N, {lon}°E")
        print(f"Analysis period: {days} days")
        
        grib_file = self.fetch_weather_data(lat, lon, days)
        
        analysis = self.analyze_weather_data(grib_file)
        
        risk_assessment = self.calculate_comprehensive_flood_risk(analysis)
        
        final_result = {
            "location": {"lat": lat, "lon": lon},
            "timestamp": datetime.now().isoformat(),
            "analysis_period_days": days,
            "weather_analysis": analysis,
            "risk_assessment": risk_assessment
        }
        
        final_result = self._clean_json_values(final_result)
        
        if os.path.exists(grib_file):
            os.remove(grib_file)
            print(f"[INFO] Cleaned up temporary file: {grib_file}")
        
        return final_result


if __name__ == "__main__":
    LAT = 16.5062
    LON = 80.6480
    
    predictor = FloodPredictor()
    
    try:
        result = predictor.predict_flood(LAT, LON, days=7)
        
        print("\n" + "="*60)
        print("COMPREHENSIVE FLOOD RISK ASSESSMENT")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Print human-readable summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        risk = result['risk_assessment']
        
        print("\n📊 SEVERITY PROBABILITIES:")
        print(f"  Minor Flooding:    {risk['severity_levels']['minor_flooding']['probability']*100:.1f}%")
        print(f"  Moderate Flooding: {risk['severity_levels']['moderate_flooding']['probability']*100:.1f}%")
        print(f"  Severe Flooding:   {risk['severity_levels']['severe_flooding']['probability']*100:.1f}%")
        
        print("\n⏰ TIME-BASED PROBABILITIES:")
        print(f"  Next 24 hours: {risk['time_windows']['next_24_hours']['probability']*100:.1f}%")
        print(f"  Next 48 hours: {risk['time_windows']['next_48_hours']['probability']*100:.1f}%")
        print(f"  Next 72 hours: {risk['time_windows']['next_72_hours']['probability']*100:.1f}%")
        print(f"  Next 7 days:   {risk['time_windows']['next_7_days']['probability']*100:.1f}%")
        
        print("\n🎯 CONFIDENCE INTERVAL:")
        print(f"  Estimate: {risk['confidence']['interpretation']}")
        print(f"  Confidence Level: {risk['confidence']['confidence_level'].upper()}")
        
        # Save to file
        with open('flood_assessment.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n[SUCCESS] Detailed results saved to flood_assessment.json")
        
    except Exception as e:
        print(f"\n[FATAL ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()