import { useState } from 'react'
import { AcademicCapIcon } from '@heroicons/react/24/outline'
import { documentApi } from '../services/api'
import { Document } from '../types'

interface DoiInputProps {
  onUpload: (document: Document) => void
  onError: (error: string) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function DoiInput({ onUpload, onError, isLoading, setIsLoading }: DoiInputProps) {
  const [doi, setDoi] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!doi.trim()) {
      onError('Please enter a DOI')
      return
    }

    // Basic DOI validation
    const doiPattern = /^10\..+\/.+/
    const cleanDoi = doi.replace(/^(https?:\/\/)?(dx\.)?doi\.org\//, '')
    
    if (!doiPattern.test(cleanDoi)) {
      onError('Please enter a valid DOI (e.g., 10.1000/123456)')
      return
    }

    setIsLoading(true)
    try {
      const document = await documentApi.uploadFromDoi(cleanDoi)
      onUpload(document)
      setDoi('')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to fetch DOI'
      onError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <AcademicCapIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
        </div>
        <input
          type="text"
          value={doi}
          onChange={(e) => setDoi(e.target.value)}
          placeholder="10.1000/123456"
          disabled={isLoading}
          className="input pl-10"
          aria-label="DOI"
          aria-describedby="doi-help"
        />
      </div>
      
      <p id="doi-help" className="text-xs text-gray-500">
        Enter a Digital Object Identifier (DOI) to fetch the paper
      </p>
      
      <button
        type="submit"
        disabled={isLoading || !doi.trim()}
        className="w-full btn-primary"
        aria-describedby="doi-help"
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" aria-hidden="true"></div>
            Fetching...
          </span>
        ) : (
          'Fetch from DOI'
        )}
      </button>
    </form>
  )
}