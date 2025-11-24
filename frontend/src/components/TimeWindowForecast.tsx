import { FloodPredictionResult } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Clock } from 'lucide-react'

function TimeWindowForecast({ result }: { result: FloodPredictionResult }) {
  if (!result?.risk_assessment?.time_windows) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-gray-600">Time window data not available</p>
      </div>
    )
  }

  const timeWindows = result.risk_assessment.time_windows

  const forecastData = [
    {
      window: '24h',
      label: 'Next 24 Hours',
      probability: timeWindows.next_24_hours?.probability ?? 0,
      description: timeWindows.next_24_hours?.description || 'N/A',
    },
    {
      window: '48h',
      label: 'Next 48 Hours',
      probability: timeWindows.next_48_hours?.probability ?? 0,
      description: timeWindows.next_48_hours?.description || 'N/A',
    },
    {
      window: '72h',
      label: 'Next 72 Hours',
      probability: timeWindows.next_72_hours?.probability ?? 0,
      description: timeWindows.next_72_hours?.description || 'N/A',
    },
    {
      window: '7d',
      label: 'Next 7 Days',
      probability: timeWindows.next_7_days?.probability ?? 0,
      description: timeWindows.next_7_days?.description || 'N/A',
    },
  ]

  const chartData = forecastData.map((item) => ({
    window: item.label,
    probability: item.probability * 100,
  }))

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <Clock className="text-primary-600" size={24} />
        Time-Windowed Forecast
      </h2>

      <div className="mb-6">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="window" />
            <YAxis label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }} domain={[0, 100]} />
            <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
            <Legend />
            <Line
              type="monotone"
              dataKey="probability"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ fill: '#3b82f6', r: 6 }}
              name="Flood Probability"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {forecastData.map((item) => (
          <div
            key={item.window}
            className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200"
          >
            <div className="text-sm font-medium text-gray-700 mb-1">{item.label}</div>
            <div className="text-3xl font-bold text-primary-600 mb-2">
              {(item.probability * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600">{item.description}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TimeWindowForecast

