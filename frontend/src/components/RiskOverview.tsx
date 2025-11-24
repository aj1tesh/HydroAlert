import { FloodPredictionResult } from '../services/api'
import { AlertTriangle, CheckCircle, Info } from 'lucide-react'

function RiskOverview({ result }: { result: FloodPredictionResult }) {
  if (!result?.risk_assessment) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-gray-600">Risk assessment data not available</p>
      </div>
    )
  }

  const riskScore = result.risk_assessment.overall_risk_score ?? 0
  const confidence = result.risk_assessment.confidence

  const getRiskLevel = (score: number) => {
    if (score < 0.25) return { label: 'Low', colorClass: 'green', icon: CheckCircle, iconClass: 'text-green-600', badgeClass: 'bg-green-100 text-green-800' }
    if (score < 0.5) return { label: 'Moderate', colorClass: 'yellow', icon: Info, iconClass: 'text-yellow-600', badgeClass: 'bg-yellow-100 text-yellow-800' }
    if (score < 0.75) return { label: 'High', colorClass: 'orange', icon: AlertTriangle, iconClass: 'text-orange-600', badgeClass: 'bg-orange-100 text-orange-800' }
    return { label: 'Critical', colorClass: 'red', icon: AlertTriangle, iconClass: 'text-red-600', badgeClass: 'bg-red-100 text-red-800' }
  }

  const riskLevel = getRiskLevel(riskScore)
  const Icon = riskLevel.icon

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Risk Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-700">Overall Risk Score</h3>
            <Icon className={riskLevel.iconClass} size={24} />
          </div>
          <div className="space-y-2">
            <div className="text-4xl font-bold text-gray-900">
              {((riskScore ?? 0) * 100).toFixed(1)}%
            </div>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${riskLevel.badgeClass}`}>
              {riskLevel.label} Risk
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-700 mb-4">Confidence</h3>
          <div className="space-y-2">
            <div className="text-2xl font-bold text-gray-900 capitalize">
              {confidence?.confidence_level || 'unknown'}
            </div>
            <div className="text-sm text-gray-600">
              {confidence?.interpretation || 'N/A'}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Range: {((confidence?.lower_bound ?? 0) * 100).toFixed(1)}% - {((confidence?.upper_bound ?? 0) * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-700 mb-4">Location</h3>
          <div className="space-y-1">
            <div className="text-lg font-semibold text-gray-900">
              {result.location.lat.toFixed(4)}°N
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {result.location.lon.toFixed(4)}°E
            </div>
            <div className="text-xs text-gray-600 mt-2">
              Analysis Period: {result.analysis_period_days} days
            </div>
            <div className="text-xs text-gray-500">
              {new Date(result.timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {result.risk_assessment.risk_factors && result.risk_assessment.risk_factors.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Key Risk Factors</h3>
          <div className="flex flex-wrap gap-2">
            {result.risk_assessment.risk_factors.map((factor, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800"
              >
                {factor}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default RiskOverview

