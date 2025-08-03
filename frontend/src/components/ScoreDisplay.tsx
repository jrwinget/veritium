import {
  CheckCircleIcon,
  XCircleIcon,
  MinusCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

interface ScoreDisplayProps {
  confidence: number
  similarity: number
  stance: 'supports' | 'contradicts' | 'neutral'
  entailment: number
  methodQuality: number
  evidenceStrength: number
}

export default function ScoreDisplay({
  confidence,
  similarity,
  stance,
  entailment,
  methodQuality,
  evidenceStrength
}: ScoreDisplayProps) {
  const getStanceIcon = (stance: string) => {
    switch (stance) {
      case 'supports':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" aria-hidden="true" />
      case 'contradicts':
        return <XCircleIcon className="h-6 w-6 text-red-500" aria-hidden="true" />
      default:
        return <MinusCircleIcon className="h-6 w-6 text-gray-500" aria-hidden="true" />
    }
  }

  const getStanceColor = (stance: string) => {
    switch (stance) {
      case 'supports':
        return 'text-green-700 bg-green-50 border-green-200'
      case 'contradicts':
        return 'text-red-700 bg-red-50 border-red-200'
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200'
    }
  }

  const formatPercentage = (score: number) => Math.round(score * 100)

  const ScoreBar = ({ label, score, description }: { label: string; score: number; description: string }) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">{formatPercentage(score)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${score >= 0.7 ? 'bg-green-500' :
              score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
          style={{ width: `${formatPercentage(score)}%` }}
          role="progressbar"
          aria-valuenow={formatPercentage(score)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${label}: ${formatPercentage(score)}%`}
        />
      </div>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Overall Confidence */}
      <div className="text-center p-6 bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg border border-primary-200">
        <h3 className="text-lg font-semibold text-primary-900 mb-2">Overall Confidence</h3>
        <div className="text-4xl font-bold text-primary-700 mb-2">
          {formatPercentage(confidence)}%
        </div>
        <p className="text-sm text-primary-600">
          How confident we are in this assessment based on all factors
        </p>
      </div>

      {/* Stance */}
      <div className={`flex items-center justify-center p-4 rounded-lg border ${getStanceColor(stance)}`}>
        <div className="flex items-center space-x-3">
          {getStanceIcon(stance)}
          <div>
            <span className="font-semibold capitalize">{stance}</span>
            <p className="text-sm mt-1">
              The document {stance === 'supports' ? 'supports' : stance === 'contradicts' ? 'contradicts' : 'is neutral about'} your claim
            </p>
          </div>
        </div>
      </div>

      {/* Component Scores */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900 flex items-center">
            <InformationCircleIcon className="h-4 w-4 mr-2" aria-hidden="true" />
            Content Analysis
          </h4>

          <ScoreBar
            label="Similarity Score"
            score={similarity}
            description="How similar your claim is to the document's findings"
          />

          <ScoreBar
            label="Entailment Score"
            score={entailment}
            description="How strongly the document supports or contradicts your claim"
          />
        </div>

        <div className="space-y-4">
          <h4 className="font-medium text-gray-900 flex items-center">
            <InformationCircleIcon className="h-4 w-4 mr-2" aria-hidden="true" />
            Study Quality
          </h4>

          <ScoreBar
            label="Method Quality"
            score={methodQuality}
            description="Quality of the study's research methodology"
          />

          <ScoreBar
            label="Evidence Strength"
            score={evidenceStrength}
            description="Strength of evidence found for your claim"
          />
        </div>
      </div>

      {/* Score Interpretation */}
      <div className="bg-gray-50 p-4 rounded-lg text-sm">
        <h4 className="font-medium text-gray-900 mb-2">Score Interpretation</h4>
        <div className="grid md:grid-cols-3 gap-4 text-xs">
          <div>
            <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>
            <strong>High (70-100%):</strong> Strong evidence or quality
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
            <strong>Medium (40-69%):</strong> Moderate evidence or quality
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span>
            <strong>Low (0-39%):</strong> Weak evidence or quality
          </div>
        </div>
      </div>
    </div>
  )
}