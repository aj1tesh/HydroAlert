import { FloodPredictionResult } from '../services/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { CloudRain } from 'lucide-react'

function WeatherCharts({ result }: { result: FloodPredictionResult }) {
  const weather = result.weather_analysis
  const timeSeries = weather.time_series

  const precipData = timeSeries?.precipitation_mm?.map((value, index) => ({
    time: `T${index + 1}`,
    precipitation: value != null && !isNaN(value) ? Number(value) : 0,
  })).filter(item => item.precipitation !== null) || []

  const soilData = timeSeries?.soil_moisture?.map((value, index) => ({
    time: `T${index + 1}`,
    moisture: value != null && !isNaN(value) ? (Number(value) * 100).toFixed(1) : '0.0',
  })).filter(item => item.moisture !== null) || []

  const safeValue = (val: number | null | undefined, defaultVal: number = 0) => {
    return val != null && !isNaN(val) ? Number(val) : defaultVal
  }

  const weatherSummary = [
    { name: 'Total Precip', value: safeValue(weather.total_precipitation_mm).toFixed(1), unit: 'mm' },
    { name: 'Max Hourly', value: safeValue(weather.max_hourly_precip_mm).toFixed(1), unit: 'mm' },
    { name: 'Avg Precip', value: safeValue(weather.avg_precipitation_mm).toFixed(1), unit: 'mm' },
    { name: 'Rain Days', value: safeValue(weather.precip_days).toString(), unit: 'days' },
    { name: 'Avg Temp', value: safeValue(weather.avg_temperature_c).toFixed(1), unit: '°C' },
    { name: 'Min Temp', value: safeValue(weather.min_temperature_c).toFixed(1), unit: '°C' },
    { name: 'Soil Moisture', value: (safeValue(weather.avg_soil_moisture) * 100).toFixed(1), unit: '%' },
    { name: 'Soil Saturation', value: (safeValue(weather.soil_saturation_ratio) * 100).toFixed(1), unit: '%' },
  ]

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <CloudRain className="text-primary-600" size={24} />
        Weather Data Analysis
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {weatherSummary.map((item, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-600 mb-1">{item.name}</div>
            <div className="text-lg font-semibold text-gray-900">
              {item.value} <span className="text-sm text-gray-500">{item.unit}</span>
            </div>
          </div>
        ))}
      </div>

      {precipData.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Precipitation Over Time</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={precipData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis label={{ value: 'mm', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="precipitation"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Precipitation (mm)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {soilData.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Soil Moisture Over Time</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={soilData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis label={{ value: '%', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="moisture" fill="#10b981" name="Soil Moisture (%)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default WeatherCharts

