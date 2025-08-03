import { useState } from 'react'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface ClaimInputProps {
  onSubmit: (claim: string) => void
  isLoading: boolean
}

export default function ClaimInput({ onSubmit, isLoading }: ClaimInputProps) {
  const [claim, setClaim] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!claim.trim()) {
      return
    }

    onSubmit(claim.trim())
  }

  const exampleClaims = [
    "Exercise reduces the risk of cardiovascular disease",
    "Meditation improves mental health outcomes",
    "Climate change is caused by human activities",
    "Vaccination reduces disease transmission rates"
  ]

  const handleExampleClick = (example: string) => {
    setClaim(example)
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="claim-input" className="block text-sm font-medium text-gray-700 mb-2">
            Enter your claim to verify
          </label>
          <div className="relative">
            <textarea
              id="claim-input"
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="Enter a specific claim you want to verify against this document..."
              disabled={isLoading}
              rows={3}
              className="input resize-none"
              aria-describedby="claim-help"
            />
            <div className="absolute bottom-3 right-3">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </div>
          </div>
          <p id="claim-help" className="mt-2 text-sm text-gray-500">
            Be specific and clear. The more precise your claim, the better the analysis.
          </p>
        </div>

        <button
          type="submit"
          disabled={isLoading || !claim.trim()}
          className="w-full btn-primary text-base py-3"
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" aria-hidden="true"></div>
              Analyzing...
            </span>
          ) : (
            <>
              <MagnifyingGlassIcon className="h-5 w-5 mr-2" aria-hidden="true" />
              Analyze Claim
            </>
          )}
        </button>
      </form>

      {/* Example Claims */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Example claims to try:
        </h3>
        <div className="grid gap-2">
          {exampleClaims.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              disabled={isLoading}
              className="text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-md border border-gray-200 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              "{example}"
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}