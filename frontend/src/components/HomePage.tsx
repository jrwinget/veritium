import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import FileUpload from './FileUpload'
import UrlInput from './UrlInput'
import DoiInput from './DoiInput'
import ClaimInput from './ClaimInput'
import { assessmentApi } from '../services/api'
import { Document } from '../types'

export default function HomePage() {
  const [document, setDocument] = useState<Document | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleDocumentUploaded = (uploadedDocument: Document) => {
    setDocument(uploadedDocument)
    toast.success('Document processed successfully!')
  }

  const handleError = (error: string) => {
    toast.error(error)
    setIsLoading(false)
  }

  const handleClaimSubmit = async (claim: string) => {
    if (!document) {
      toast.error('Please upload a document first')
      return
    }

    setIsLoading(true)
    try {
      const assessment = await assessmentApi.createAssessment(document.id, claim)
      navigate(`/assessment/${assessment.id}`)
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create assessment'
      handleError(message)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Scientific Article Verification
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Upload a research paper or enter a URL/DOI, then test how well it supports your claims. 
          Get transparent, evidence-based assessments with detailed explanations.
        </p>
      </div>

      {/* Upload Section */}
      <div className="card p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          Step 1: Upload Document
        </h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              Upload File
            </h3>
            <FileUpload
              onUpload={handleDocumentUploaded}
              onError={handleError}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              From URL
            </h3>
            <UrlInput
              onUpload={handleDocumentUploaded}
              onError={handleError}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              From DOI
            </h3>
            <DoiInput
              onUpload={handleDocumentUploaded}
              onError={handleError}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
        </div>
      </div>

      {/* Document Summary */}
      {document && (
        <div className="card p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Document Summary
          </h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-900">Title</h3>
              <p className="text-gray-700">{document.title}</p>
            </div>
            
            {document.authors.length > 0 && (
              <div>
                <h3 className="font-medium text-gray-900">Authors</h3>
                <p className="text-gray-700">{document.authors.join(', ')}</p>
              </div>
            )}
            
            {document.abstract && (
              <div>
                <h3 className="font-medium text-gray-900">Abstract</h3>
                <p className="text-gray-700 text-sm leading-relaxed">
                  {document.abstract.length > 300 
                    ? `${document.abstract.substring(0, 300)}...` 
                    : document.abstract
                  }
                </p>
              </div>
            )}
            
            {document.extracted_claims.length > 0 && (
              <div>
                <h3 className="font-medium text-gray-900">Extracted Claims</h3>
                <ul className="mt-2 space-y-2">
                  {document.extracted_claims.slice(0, 3).map((claim, index) => (
                    <li key={index} className="text-sm text-gray-700 border-l-2 border-gray-200 pl-3">
                      {claim.length > 150 ? `${claim.substring(0, 150)}...` : claim}
                    </li>
                  ))}
                  {document.extracted_claims.length > 3 && (
                    <li className="text-sm text-gray-500 italic">
                      And {document.extracted_claims.length - 3} more...
                    </li>
                  )}
                </ul>
              </div>
            )}
            
            <div className="flex space-x-4 text-sm text-gray-600">
              <span>Quality Score: {(document.method_quality_score * 100).toFixed(0)}%</span>
              <span>Confidence: {(document.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Claim Input */}
      {document && (
        <div className="card p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Step 2: Enter Your Claim
          </h2>
          
          <ClaimInput 
            onSubmit={handleClaimSubmit}
            isLoading={isLoading}
          />
        </div>
      )}

      {/* Instructions */}
      <div className="card p-6 bg-primary-50 border-primary-200">
        <h2 className="text-xl font-semibold text-primary-900 mb-4">
          How It Works
        </h2>
        
        <div className="grid md:grid-cols-2 gap-6 text-sm text-primary-800">
          <div>
            <h3 className="font-medium mb-2">Document Analysis</h3>
            <ul className="space-y-1 list-disc list-inside">
              <li>Extracts text, metadata, and claims</li>
              <li>Assesses methodological quality</li>
              <li>Identifies key findings and conclusions</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Claim Verification</h3>
            <ul className="space-y-1 list-disc list-inside">
              <li>Compares your claim with document content</li>
              <li>Calculates semantic similarity</li>
              <li>Determines support/contradiction stance</li>
              <li>Provides evidence-based explanations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}