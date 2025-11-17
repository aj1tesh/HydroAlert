import cdsapi
import numpy as np
import json
import requests
from datetime import datetime, timedelta
import xarray as xr
import os

# ============= CONFIGURATION =============
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:12b"

class FloodPredictor:
    def __init__(self):
        self.cds_client = cdsapi.Client()
        
    def fetch_weather_data(self, lat, lon, days=7):
        """
        Fetch relevant weather data from CDS ERA5 for flood prediction
        """
        print(f"\n[INFO] Fetching weather data for coordinates: {lat}, {lon}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Prepare request parameters
        years = list(set([start_date.strftime('%Y'), end_date.strftime('%Y')]))
        months = list(set([start_date.strftime('%m'), end_date.strftime('%m')]))
        
        # Generate day list
        current = start_date
        days_list = []
        while current <= end_date:
            days_list.append(current.strftime('%d'))
            current += timedelta(days=1)
        days_list = list(set(days_list))
        
        # Define area around the point (0.5 degree buffer)
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
            print(f"[ERROR] CDS API request failed: {e}")
            raise
    
    def analyze_weather_data(self, grib_file):
        """
        Analyze the downloaded GRIB file and extract flood risk indicators with time series
        """
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
            
            # Read each variable separately
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
            
            # Process precipitation with time series
            if 'tp' in datasets:
                ds = datasets['tp']
                if 'tp' in ds.data_vars:
                    precip = ds['tp'].values
                    precip_mm = precip * 1000  # m to mm
                    
                    # Overall statistics
                    analysis['total_precipitation_mm'] = float(np.nansum(precip_mm))
                    analysis['max_hourly_precip_mm'] = float(np.nanmax(precip_mm))
                    analysis['avg_precipitation_mm'] = float(np.nanmean(precip_mm))
                    analysis['precip_days'] = int(np.sum(precip_mm > 1.0))
                    
                    # Time series for temporal analysis
                    if precip_mm.ndim >= 1:
                        # Flatten spatial dimensions, keep time
                        if precip_mm.ndim == 3:  # time, lat, lon
                            precip_time = np.mean(precip_mm, axis=(1, 2))
                        elif precip_mm.ndim == 2:  # time, space
                            precip_time = np.mean(precip_mm, axis=1)
                        else:
                            precip_time = precip_mm
                        
                        time_series['precipitation_mm'] = precip_time.tolist()
                    
                    print(f"[INFO] Precipitation - Total: {analysis['total_precipitation_mm']:.2f}mm")
            
            # Process temperature
            if 't2m' in datasets:
                ds = datasets['t2m']
                if 't2m' in ds.data_vars:
                    temp = ds['t2m'].values
                    temp_c = temp - 273.15  # K to C
                    analysis['avg_temperature_c'] = float(np.nanmean(temp_c))
                    analysis['min_temperature_c'] = float(np.nanmin(temp_c))
                    print(f"[INFO] Temperature - Avg: {analysis['avg_temperature_c']:.1f}°C")
            
            # Process soil moisture with time series
            if 'swvl1' in datasets:
                ds = datasets['swvl1']
                if 'swvl1' in ds.data_vars:
                    soil_moisture = ds['swvl1'].values
                    analysis['avg_soil_moisture'] = float(np.nanmean(soil_moisture))
                    analysis['max_soil_moisture'] = float(np.nanmax(soil_moisture))
                    analysis['soil_saturation_ratio'] = float(np.mean(soil_moisture > 0.4))
                    
                    # Time series
                    if soil_moisture.ndim >= 1:
                        if soil_moisture.ndim == 3:
                            soil_time = np.mean(soil_moisture, axis=(1, 2))
                        elif soil_moisture.ndim == 2:
                            soil_time = np.mean(soil_moisture, axis=1)
                        else:
                            soil_time = soil_moisture
                        
                        time_series['soil_moisture'] = soil_time.tolist()
                    
                    print(f"[INFO] Soil Moisture - Avg: {analysis['avg_soil_moisture']:.3f}")
            
            # Close all datasets
            for ds in datasets.values():
                ds.close()
            
            analysis['time_series'] = time_series
            print("[SUCCESS] Weather data analyzed")
            return analysis
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze GRIB data: {e}")
            raise
    
    def calculate_comprehensive_flood_risk(self, analysis):
        """
        Calculate comprehensive flood risk with:
        1. Severity levels (minor/moderate/severe)
        2. Time-windowed probabilities (24h/48h/72h)
        3. Confidence intervals
        """
        print("\n[INFO] Calculating comprehensive flood risk...")
        
        # Base risk factors
        precip_total = analysis.get('total_precipitation_mm', 0)
        precip_max = analysis.get('max_hourly_precip_mm', 0)
        soil_sat = analysis.get('soil_saturation_ratio', 0)
        precip_days = analysis.get('precip_days', 0)
        
        # === 1. SEVERITY LEVELS ===
        severity_probs = self._calculate_severity_probabilities(
            precip_total, precip_max, soil_sat, precip_days
        )
        
        # === 2. TIME-WINDOWED PROBABILITIES ===
        time_probs = self._calculate_time_windowed_probabilities(
            analysis.get('time_series', {}), precip_total, soil_sat
        )
        
        # === 3. CONFIDENCE INTERVALS ===
        base_prob = severity_probs['overall']
        confidence_intervals = self._calculate_confidence_intervals(
            base_prob, precip_total, soil_sat, precip_days
        )
        
        # Risk factors explanation
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
        """
        Calculate probability for each flood severity level
        """
        # Base score components
        precip_score = min(precip_total / 200, 1.0)  # 0-1
        intensity_score = min(precip_max / 30, 1.0)  # 0-1
        soil_score = soil_sat  # already 0-1
        duration_score = min(precip_days / 7, 1.0)  # 0-1
        
        # Overall base probability
        base_prob = (precip_score * 0.4 + intensity_score * 0.3 + 
                     soil_score * 0.2 + duration_score * 0.1)
        
        # Severity thresholds and probabilities
        # Minor: 0-30cm water depth
        prob_minor = base_prob * 0.8 if base_prob > 0.2 else base_prob * 1.2
        prob_minor = min(prob_minor, 1.0)
        
        # Moderate: 30-100cm water depth
        prob_moderate = base_prob * 0.6 if base_prob > 0.4 else base_prob * 0.3
        prob_moderate = min(prob_moderate, 1.0)
        
        # Severe: >100cm water depth
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
        """
        Calculate flood probability for different time windows
        """
        # If we have time series data, use it for better estimates
        recent_precip_trend = 0
        if 'precipitation_mm' in time_series and len(time_series['precipitation_mm']) > 0:
            precip_data = time_series['precipitation_mm']
            # Look at recent vs older data
            if len(precip_data) >= 4:
                recent_avg = np.mean(precip_data[-2:])  # Last 2 readings
                older_avg = np.mean(precip_data[:-2])  # Older readings
                recent_precip_trend = recent_avg - older_avg
        
        # Base probability
        base = min((precip_total / 100) * 0.5 + soil_sat * 0.5, 1.0)
        
        # Adjust based on trends
        trend_factor = 1.0 + (recent_precip_trend / 10)  # Normalize trend
        trend_factor = max(0.5, min(trend_factor, 2.0))  # Limit to 0.5-2x
        
        # Time windows with increasing probability
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
        """
        Calculate confidence intervals for the probability estimate
        """
        # Uncertainty factors
        data_uncertainty = 0.15  # Base uncertainty from ERA5 data
        
        # Reduce uncertainty if we have strong signals
        if precip_total > 100 or soil_sat > 0.7:
            data_uncertainty *= 0.7  # More confident
        elif precip_total < 10 and soil_sat < 0.2:
            data_uncertainty *= 0.8  # Also confident (clearly low risk)
        else:
            data_uncertainty *= 1.2  # Less confident in middle range
        
        # Calculate bounds
        lower_bound = max(0, base_prob - data_uncertainty)
        upper_bound = min(1.0, base_prob + data_uncertainty)
        
        # Confidence level
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
    
    def query_ollama(self, prompt):
        """
        Query local Ollama model for AI-powered analysis
        """
        print("\n[INFO] Querying Ollama for AI analysis...")
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            
            result = response.json()
            if 'response' in result:
                try:
                    return json.loads(result['response'])
                except json.JSONDecodeError:
                    return {"raw_response": result['response']}
            return result
            
        except Exception as e:
            print(f"[WARNING] Ollama query failed: {e}")
            return None
    
    def predict_flood(self, lat, lon, days=7):
        """
        Main prediction function with comprehensive risk assessment
        """
        print("="*60)
        print("COMPREHENSIVE FLOOD PREDICTION SYSTEM")
        print("="*60)
        print(f"Location: {lat}°N, {lon}°E")
        print(f"Analysis period: {days} days")
        
        # Step 1: Fetch weather data
        grib_file = self.fetch_weather_data(lat, lon, days)
        
        # Step 2: Analyze data
        analysis = self.analyze_weather_data(grib_file)
        
        # Step 3: Calculate comprehensive risk
        risk_assessment = self.calculate_comprehensive_flood_risk(analysis)
        
        # Step 4: Query Ollama for interpretation
        prompt = f"""You are a flood risk assessment expert. Analyze this comprehensive weather data and provide detailed insights.

Location: Latitude {lat}, Longitude {lon}
Analysis Period: Last {days} days

Weather Data:
{json.dumps(analysis, indent=2)}

Risk Assessment:
{json.dumps(risk_assessment, indent=2)}

Provide a JSON response with:
{{
  "overall_assessment": <string: brief overall assessment>,
  "severity_analysis": <string: explain the different severity probabilities>,
  "temporal_analysis": <string: explain how risk changes over time windows>,
  "confidence_notes": <string: explain the confidence level and uncertainty>,
  "recommended_actions": [<list of specific actions>],
  "key_concerns": [<list of specific concerns>],
  "monitoring_priorities": [<what to monitor closely>]
}}

Be specific and actionable. Reference the actual probabilities."""

        ollama_result = self.query_ollama(prompt)
        
        # Step 5: Compile final result
        final_result = {
            "location": {"lat": lat, "lon": lon},
            "timestamp": datetime.now().isoformat(),
            "analysis_period_days": days,
            "weather_analysis": analysis,
            "risk_assessment": risk_assessment,
            "ai_interpretation": ollama_result if ollama_result else {
                "overall_assessment": "AI analysis unavailable. Using deterministic model.",
                "severity_analysis": f"Minor flooding: {risk_assessment['severity_levels']['minor_flooding']['probability']*100:.1f}%, Moderate: {risk_assessment['severity_levels']['moderate_flooding']['probability']*100:.1f}%, Severe: {risk_assessment['severity_levels']['severe_flooding']['probability']*100:.1f}%",
                "temporal_analysis": f"Risk increases from {risk_assessment['time_windows']['next_24_hours']['probability']*100:.1f}% (24h) to {risk_assessment['time_windows']['next_7_days']['probability']*100:.1f}% (7d)",
                "confidence_notes": f"Confidence level: {risk_assessment['confidence']['confidence_level']}",
                "recommended_actions": self._get_recommendations(risk_assessment['overall_risk_score']),
                "key_concerns": risk_assessment['risk_factors'],
                "monitoring_priorities": ["Precipitation levels", "Soil saturation", "Water accumulation"]
            }
        }
        
        # Cleanup
        if os.path.exists(grib_file):
            os.remove(grib_file)
            print(f"[INFO] Cleaned up temporary file: {grib_file}")
        
        return final_result
    
    def _get_recommendations(self, score):
        if score < 0.25:
            return ["Continue routine monitoring", "No immediate action required"]
        elif score < 0.5:
            return ["Increase monitoring frequency", "Review emergency response plans", "Clear drainage systems"]
        elif score < 0.75:
            return ["Activate flood watch", "Prepare emergency supplies", "Alert vulnerable populations", "Monitor continuously"]
        else:
            return ["Activate flood warning", "Begin evacuations if needed", "Close affected roads", "Emergency response on standby"]


# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    # Example coordinates (Lucknow area)
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