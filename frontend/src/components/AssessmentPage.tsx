import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  ShareIcon, 
  HandThumbUpIcon, 
  HandThumbDownIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { HandThumbUpIcon as HandThumbUpSolid, HandThumbDownIcon as HandThumbDownSolid } from '@heroicons/react/24/solid'
import toast from 'react-hot-toast'
import { assessmentApi } from '../services/api'
import { Assessment } from '../types'
import ScoreDisplay from './ScoreDisplay'
import EvidenceSnippets from './EvidenceSnippets'
import Citations from './Citations'

export default function AssessmentPage() {
  const { id } = useParams<{ id: string }>()
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [feedback, setFeedback] = useState<number | null>(null)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false)

  useEffect(() => {
    const fetchAssessment = async () => {
      if (!id) return

      try {
        const result = await assessmentApi.getAssessment(parseInt(id))
        setAssessment(result)
      } catch (error: any) {
        const message = error.response?.data?.detail || 'Failed to load assessment'
        toast.error(message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAssessment()
  }, [id])

  const handleShare = async () => {
    if (!assessment?.share_id) return

    const shareUrl = `${window.location.origin}/share/${assessment.share_id}`
    
    try {
      await navigator.clipboard.writeText(shareUrl)
      toast.success('Share link copied to clipboard!')
    } catch (error) {
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea')
      textArea.value = shareUrl
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      toast.success('Share link copied to clipboard!')
    }
  }

  const handleFeedback = async (score: number) => {
    if (!assessment) return

    setIsSubmittingFeedback(true)
    try {
      await assessmentApi.submitFeedback(assessment.id, score, feedbackComment || undefined)
      setFeedback(score)
      toast.success('Thank you for your feedback!')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to submit feedback'
      toast.error(message)
    } finally {
      setIsSubmittingFeedback(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" aria-hidden="true"></div>
        <span className="ml-2 text-gray-600">Loading assessment...</span>
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" aria-hidden="true" />
        <h2 className="mt-4 text-xl font-semibold text-gray-900">Assessment not found</h2>
        <p className="mt-2 text-gray-600">The assessment you're looking for doesn't exist or has been removed.</p>
        <Link to="/" className="mt-4 inline-flex items-center btn-primary">
          Go Home
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Assessment Results
          </h1>
          <p className="text-gray-600">
            Analysis of your claim against the uploaded document
          </p>
        </div>
        
        <button
          onClick={handleShare}
          className="btn-secondary flex items-center"
          aria-label="Share assessment"
        >
          <ShareIcon className="h-4 w-4 mr-2" aria-hidden="true" />
          Share
        </button>
      </div>

      {/* Claim */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-3 flex items-center">
          <DocumentTextIcon className="h-5 w-5 mr-2" aria-hidden="true" />
          Your Claim
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

      {/* Feedback */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Was this assessment helpful?
        </h2>
        
        {feedback === null ? (
          <div className="space-y-4">
            <div className="flex space-x-4">
              <button
                onClick={() => handleFeedback(1)}
                disabled={isSubmittingFeedback}
                className="flex items-center px-4 py-2 bg-green-50 text-green-700 border border-green-200 rounded-md hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
              >
                <HandThumbUpIcon className="h-5 w-5 mr-2" aria-hidden="true" />
                Helpful
              </button>
              
              <button
                onClick={() => handleFeedback(-1)}
                disabled={isSubmittingFeedback}
                className="flex items-center px-4 py-2 bg-red-50 text-red-700 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
              >
                <HandThumbDownIcon className="h-5 w-5 mr-2" aria-hidden="true" />
                Not Helpful
              </button>
            </div>
            
            <div>
              <label htmlFor="feedback-comment" className="block text-sm font-medium text-gray-700 mb-2">
                Additional comments (optional)
              </label>
              <textarea
                id="feedback-comment"
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                placeholder="How can we improve this assessment?"
                rows={3}
                className="input resize-none"
                disabled={isSubmittingFeedback}
              />
            </div>
          </div>
        ) : (
          <div className="flex items-center text-green-700">
            {feedback === 1 ? (
              <HandThumbUpSolid className="h-5 w-5 mr-2" aria-hidden="true" />
            ) : (
              <HandThumbDownSolid className="h-5 w-5 mr-2" aria-hidden="true" />
            )}
            <span>Thank you for your feedback!</span>
          </div>
        )}
      </div>
    </div>
  )
}