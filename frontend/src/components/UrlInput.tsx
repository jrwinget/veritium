import { useState } from 'react'
import { LinkIcon } from '@heroicons/react/24/outline'
import { documentApi } from '../services/api'
import { Document } from '../types'

interface UrlInputProps {
  onUpload: (document: Document) => void
  onError: (error: string) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function UrlInput({ onUpload, onError, isLoading, setIsLoading }: UrlInputProps) {
  const [url, setUrl] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!url.trim()) {
      onError('Please enter a URL')
      return
    }

    // Basic URL validation
    try {
      new URL(url)
    } catch {
      onError('Please enter a valid URL')
      return
    }

    setIsLoading(true)
    try {
      const document = await documentApi.uploadFromUrl(url)
      onUpload(document)
      setUrl('')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to fetch from URL'
      onError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <LinkIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
        </div>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/paper.pdf"
          disabled={isLoading}
          className="input pl-10"
          aria-label="Document URL"
          aria-describedby="url-help"
        />
      </div>

      <p id="url-help" className="text-xs text-gray-500">
        Enter a direct link to a PDF or webpage containing the article
      </p>

      <button
        type="submit"
        disabled={isLoading || !url.trim()}
        className="w-full btn-primary"
        aria-describedby="url-help"
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" aria-hidden="true"></div>
            Fetching...
          </span>
        ) : (
          'Fetch from URL'
        )}
      </button>
    </form>
  )
}