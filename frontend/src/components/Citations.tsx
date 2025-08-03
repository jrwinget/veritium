import { LinkIcon, AcademicCapIcon } from '@heroicons/react/24/outline'
import { Citation } from '../types'

interface CitationsProps {
  citations: Citation[]
}

export default function Citations({ citations }: CitationsProps) {
  const formatSimilarity = (score: number) => Math.round(score * 100)

  return (
    <div className="space-y-4">
      {citations.map((citation, index) => (
        <div
          key={citation.id}
          className="border border-gray-200 rounded-lg p-4 bg-white"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900 mb-1">
                Citation {index + 1}
              </h4>
              <p className="text-sm text-gray-600">{citation.document_title}</p>
            </div>

            <div className="text-right text-sm text-gray-600">
              <div>Relevance: {formatSimilarity(citation.similarity_score)}%</div>
            </div>
          </div>

          <blockquote className="text-gray-700 border-l-2 border-gray-300 pl-4 mb-3 italic">
            "{citation.text}"
          </blockquote>

          <div className="flex items-center justify-between text-sm">
            <div className="text-gray-500">
              Section {citation.snippet_index + 1}
            </div>

            <div className="flex items-center space-x-2">
              {citation.doi && (
                <a
                  href={`https://doi.org/${citation.doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary-600 hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-md px-2 py-1"
                  aria-label={`View DOI ${citation.doi}`}
                >
                  <AcademicCapIcon className="h-4 w-4 mr-1" aria-hidden="true" />
                  DOI
                </a>
              )}

              {citation.url && !citation.doi && (
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary-600 hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-md px-2 py-1"
                  aria-label="View source"
                >
                  <LinkIcon className="h-4 w-4 mr-1" aria-hidden="true" />
                  Source
                </a>
              )}
            </div>
          </div>
        </div>
      ))}

      {citations.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No citations available for this assessment.</p>
        </div>
      )}
    </div>
  )
}