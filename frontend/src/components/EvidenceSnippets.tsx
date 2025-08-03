import { EvidenceSnippet } from '../types'

interface EvidenceSnippetsProps {
  snippets: EvidenceSnippet[]
}

export default function EvidenceSnippets({ snippets }: EvidenceSnippetsProps) {
  const formatSimilarity = (score: number) => Math.round(score * 100)

  return (
    <div className="space-y-4">
      {snippets.map((snippet, index) => (
        <div
          key={index}
          className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200"
        >
          <div className="flex items-start justify-between mb-2">
            <span className="text-sm font-medium text-gray-900">
              Evidence #{index + 1}
            </span>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <span>Similarity:</span>
              <span 
                className={`font-semibold ${
                  snippet.similarity >= 0.7 ? 'text-green-600' :
                  snippet.similarity >= 0.4 ? 'text-yellow-600' : 'text-red-600'
                }`}
              >
                {formatSimilarity(snippet.similarity)}%
              </span>
            </div>
          </div>
          
          <blockquote className="text-gray-700 border-l-2 border-primary-200 pl-4 italic leading-relaxed">
            "{snippet.text}"
          </blockquote>
          
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <span>Words: {snippet.word_count}</span>
            <span>Position: {snippet.sentence_index}</span>
          </div>
        </div>
      ))}
      
      {snippets.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No evidence snippets found for this claim.</p>
        </div>
      )}
    </div>
  )
}