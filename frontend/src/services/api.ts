import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Location {
  lat: number
  lon: number
}

export interface WeatherAnalysis {
  total_precipitation_mm: number
  max_hourly_precip_mm: number
  avg_precipitation_mm: number
  precip_days: number
  avg_temperature_c: number
  min_temperature_c: number
  avg_soil_moisture: number
  max_soil_moisture: number
  soil_saturation_ratio: number
  time_series?: {
    precipitation_mm?: number[]
    soil_moisture?: number[]
  }
}

export interface SeverityLevel {
  probability: number
  description: string
}

export interface TimeWindow {
  probability: number
  description: string
}

export interface Confidence {
  probability_estimate: number
  lower_bound: number
  upper_bound: number
  margin_of_error: number
  confidence_level: string
  interpretation: string
}

export interface RiskAssessment {
  severity_levels: {
    overall: number
    minor_flooding: SeverityLevel
    moderate_flooding: SeverityLevel
    severe_flooding: SeverityLevel
  }
  time_windows: {
    next_24_hours: TimeWindow
    next_48_hours: TimeWindow
    next_72_hours: TimeWindow
    next_7_days: TimeWindow
  }
  confidence: Confidence
  risk_factors: string[]
  overall_risk_score: number
}

export interface FloodPredictionResult {
  location: Location
  timestamp: string
  analysis_period_days: number
  weather_analysis: WeatherAnalysis
  risk_assessment: RiskAssessment
}

class ApiService {
  private baseURL: string

  constructor() {
    this.baseURL = API_BASE_URL
  }

  async predictFlood(lat: number, lon: number, days: number = 7): Promise<FloodPredictionResult> {
    try {
      const response = await axios.post(`${this.baseURL}/api/predict`, {
        lat,
        lon,
        days,
      })
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Failed to predict flood risk')
      }
      throw error
    }
  }

  // Mock data for development/testing
  getMockData(): FloodPredictionResult {
    return {
      location: { lat: 16.5062, lon: 80.6480 },
      timestamp: new Date().toISOString(),
      analysis_period_days: 7,
      weather_analysis: {
        total_precipitation_mm: 85.5,
        max_hourly_precip_mm: 12.3,
        avg_precipitation_mm: 12.2,
        precip_days: 4,
        avg_temperature_c: 28.5,
        min_temperature_c: 24.2,
        avg_soil_moisture: 0.45,
        max_soil_moisture: 0.52,
        soil_saturation_ratio: 0.65,
        time_series: {
          precipitation_mm: [0, 2.5, 5.1, 8.3, 12.3, 10.2, 7.8, 5.4, 3.2, 1.5, 0.8, 0.2],
          soil_moisture: [0.35, 0.38, 0.42, 0.45, 0.48, 0.50, 0.52, 0.51, 0.49, 0.47, 0.45, 0.44],
        },
      },
      risk_assessment: {
        severity_levels: {
          overall: 0.65,
          minor_flooding: {
            probability: 0.72,
            description: 'Water depth 0-30cm, roads passable with caution',
          },
          moderate_flooding: {
            probability: 0.45,
            description: 'Water depth 30-100cm, road closures likely',
          },
          severe_flooding: {
            probability: 0.28,
            description: 'Water depth >100cm, evacuation may be needed',
          },
        },
        time_windows: {
          next_24_hours: {
            probability: 0.45,
            description: 'Immediate risk assessment',
          },
          next_48_hours: {
            probability: 0.58,
            description: 'Short-term forecast',
          },
          next_72_hours: {
            probability: 0.65,
            description: 'Medium-term forecast',
          },
          next_7_days: {
            probability: 0.72,
            description: 'Extended forecast',
          },
        },
        confidence: {
          probability_estimate: 0.65,
          lower_bound: 0.50,
          upper_bound: 0.80,
          margin_of_error: 0.15,
          confidence_level: 'medium',
          interpretation: '65.0% (±15.0%)',
        },
        risk_factors: [
          'High total precipitation: 85.5mm',
          'Intense rainfall: 12.3mm/6h',
          'Saturated soil: 65%',
          'Continuous rain: 4 days',
        ],
        overall_risk_score: 0.65,
      },
    }
  }
}

export default new ApiService()

