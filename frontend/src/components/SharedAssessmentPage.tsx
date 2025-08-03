import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  ChartBarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  EyeIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { assessmentApi } from '../services/api'
import { Assessment } from '../types'
import ScoreDisplay from './ScoreDisplay'
import EvidenceSnippets from './EvidenceSnippets'
import Citations from './Citations'

export default function SharedAssessmentPage() {
  const { shareId } = useParams<{ shareId: string }>()
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAssessment = async () => {
      if (!shareId) return

      try {
        const result = await assessmentApi.getSharedAssessment(shareId)
        setAssessment(result)
      } catch (error: any) {
        const message = error.response?.data?.detail || 'Failed to load shared assessment'
        toast.error(message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAssessment()
  }, [shareId])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" aria-hidden="true"></div>
        <span className="ml-2 text-gray-600">Loading shared assessment...</span>
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" aria-hidden="true" />
        <h2 className="mt-4 text-xl font-semibold text-gray-900">Shared assessment not found</h2>
        <p className="mt-2 text-gray-600">The shared assessment you're looking for doesn't exist or has been removed.</p>
        <Link to="/" className="mt-4 inline-flex items-center btn-primary">
          Create Your Own Assessment
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <EyeIcon className="h-8 w-8 text-primary-500 mr-2" aria-hidden="true" />
          <h1 className="text-3xl font-bold text-gray-900">
            Shared Assessment
          </h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          This is a shared scientific article verification assessment. 
          You can view the analysis results but cannot modify them.
        </p>
      </div>

      {/* Claim */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-3 flex items-center">
          <DocumentTextIcon className="h-5 w-5 mr-2" aria-hidden="true" />
          Analyzed Claim
        </h2>
        <blockquote className="text-lg text-gray-700 border-l-4 border-primary-500 pl-4 italic">
          "{assessment.user_claim}"
        </blockquote>
      </div>

      {/* Scores */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2" aria-hidden="true" />
          Assessment Scores
        </h2>
        
        <ScoreDisplay 
          confidence={assessment.confidence_score}
          similarity={assessment.similarity_score}
          stance={assessment.stance}
          entailment={assessment.entailment_score}
          methodQuality={assessment.method_quality_score}
          evidenceStrength={assessment.evidence_strength_score}
        />
      </div>

      {/* Explanation */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Explanation
        </h2>
        <div className="prose max-w-none text-gray-700">
          <p className="leading-relaxed">{assessment.explanation}</p>
        </div>
      </div>

      {/* Evidence */}
      {assessment.evidence_snippets.length > 0 && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Supporting Evidence
          </h2>
          <EvidenceSnippets snippets={assessment.evidence_snippets} />
        </div>
      )}

      {/* Citations */}
      {assessment.citations.length > 0 && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Citations
          </h2>
          <Citations citations={assessment.citations} />
        </div>
      )}

      {/* Call to Action */}
      <div className="card p-6 bg-primary-50 border-primary-200 text-center">
        <h2 className="text-xl font-semibold text-primary-900 mb-2">
          Want to create your own assessment?
        </h2>
        <p className="text-primary-700 mb-4">
          Upload your own documents and test your claims with Veritium's scientific verification system.
        </p>
        <Link to="/" className="btn-primary">
          Get Started
        </Link>
      </div>

      {/* Assessment Metadata */}
      <div className="text-center text-sm text-gray-500">
        <p>Assessment created: {new Date(assessment.created_at).toLocaleDateString()}</p>
        <p className="mt-1">
          <strong>Disclaimer:</strong> This automated analysis is for research purposes only. 
          Always consult original sources and domain experts for critical decisions.
        </p>
      </div>
    </div>
  )
}