import { useState, Component, ErrorInfo, ReactNode } from 'react'
import LocationInput from '../components/LocationInput'
import RiskOverview from '../components/RiskOverview'
import WeatherCharts from '../components/WeatherCharts'
import SeverityBreakdown from '../components/SeverityBreakdown'
import TimeWindowForecast from '../components/TimeWindowForecast'
import api, { FloodPredictionResult } from '../services/api'
import { AlertCircle, Loader2 } from 'lucide-react'

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Component error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold mb-2">Error rendering component</h3>
          <p className="text-red-700 text-sm">{this.state.error?.message || 'Unknown error'}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-2 text-sm text-red-600 underline"
          >
            Try again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<FloodPredictionResult | null>(null)
  const [useMockData, setUseMockData] = useState(false)

  const handlePredict = async (lat: number, lon: number, days: number) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      let data: FloodPredictionResult
      if (useMockData) {
        await new Promise((resolve) => setTimeout(resolve, 1500))
        data = api.getMockData()
      } else {
        data = await api.predictFlood(lat, lon, days)
      }
      
      console.log('Prediction result received:', data)
      
      if (!data || !data.risk_assessment) {
        throw new Error('Invalid response format: missing risk_assessment')
      }
      
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      console.error('Prediction error:', err)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">HydroAlert</h1>
              <p className="text-sm text-gray-600 mt-1">Flood Prediction & Risk Assessment System</p>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={useMockData}
                  onChange={(e) => setUseMockData(e.target.checked)}
                  className="rounded border-gray-300"
                />
                Use Mock Data
              </label>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <LocationInput onPredict={handlePredict} loading={loading} />
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              <p className="text-red-600 text-xs mt-2">
                Tip: Enable "Use Mock Data" to see the interface with sample data.
              </p>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="animate-spin text-primary-600 mb-4" size={48} />
            <p className="text-gray-600">Analyzing flood risk... This may take a few moments.</p>
          </div>
        )}

        {result && !loading && (
          <div className="space-y-6">
            <ErrorBoundary>
              <RiskOverview result={result} />
            </ErrorBoundary>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ErrorBoundary>
                <WeatherCharts result={result} />
              </ErrorBoundary>
              <ErrorBoundary>
                <SeverityBreakdown result={result} />
              </ErrorBoundary>
            </div>

            <ErrorBoundary>
              <TimeWindowForecast result={result} />
            </ErrorBoundary>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Get Started
                </h2>
                <p className="text-gray-600 mb-4">
                  Enter coordinates or select a location on the map to begin flood risk assessment.
                </p>
                <p className="text-sm text-gray-500">
                  The system will analyze weather data, soil conditions, and precipitation patterns
                  to provide comprehensive flood risk predictions.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            FLUD - Flood Prediction System | Powered by ERA5 Weather Data & AI Analysis
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard

