import { FloodPredictionResult } from '../services/api'
import { Progress } from './Progress'
import { AlertCircle, AlertTriangle, AlertOctagon } from 'lucide-react'

function SeverityBreakdown({ result }: { result: FloodPredictionResult }) {
  if (!result?.risk_assessment?.severity_levels) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-gray-600">Severity data not available</p>
      </div>
    )
  }

  const severity = result.risk_assessment.severity_levels

  const severityLevels = [
    {
      key: 'minor_flooding' as const,
      label: 'Minor Flooding',
      icon: AlertCircle,
      color: 'yellow' as const,
      iconClass: 'text-yellow-600',
      description: severity.minor_flooding?.description || 'N/A',
      probability: severity.minor_flooding?.probability ?? 0,
    },
    {
      key: 'moderate_flooding' as const,
      label: 'Moderate Flooding',
      icon: AlertTriangle,
      color: 'orange' as const,
      iconClass: 'text-orange-600',
      description: severity.moderate_flooding?.description || 'N/A',
      probability: severity.moderate_flooding?.probability ?? 0,
    },
    {
      key: 'severe_flooding' as const,
      label: 'Severe Flooding',
      icon: AlertOctagon,
      color: 'red' as const,
      iconClass: 'text-red-600',
      description: severity.severe_flooding?.description || 'N/A',
      probability: severity.severe_flooding?.probability ?? 0,
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Flood Severity Probabilities</h2>

      <div className="space-y-6">
        {severityLevels.map((level) => {
          const Icon = level.icon
          return (
            <div key={level.key} className="space-y-2">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Icon className={level.iconClass} size={20} />
                  <span className="font-medium text-gray-900">{level.label}</span>
                </div>
                <span className="text-lg font-bold text-gray-900">
                  {(level.probability * 100).toFixed(1)}%
                </span>
              </div>
              <Progress value={level.probability * 100} color={level.color} />
              <p className="text-sm text-gray-600">{level.description}</p>
            </div>
          )
        })}
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-gray-900">Overall Flood Probability</span>
          <span className="text-2xl font-bold text-primary-600">
            {((severity.overall ?? 0) * 100).toFixed(1)}%
          </span>
        </div>
        <Progress value={(severity.overall ?? 0) * 100} color="blue" />
      </div>
    </div>
  )
}

export default SeverityBreakdown

