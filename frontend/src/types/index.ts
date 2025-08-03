export interface Document {
  id: number
  title: string
  authors: string[]
  abstract: string
  doi?: string
  url?: string
  file_type: string
  extracted_claims: string[]
  confidence_score: number
  method_quality_score: number
  created_at: string
}

export interface Assessment {
  id: number
  document_id: number
  user_claim: string
  similarity_score: number
  stance: 'supports' | 'contradicts' | 'neutral'
  entailment_score: number
  method_quality_score: number
  evidence_strength_score: number
  confidence_score: number
  explanation: string
  evidence_snippets: EvidenceSnippet[]
  citations: Citation[]
  share_id?: string
  created_at: string
}

export interface EvidenceSnippet {
  text: string
  similarity: number
  sentence_index: number
  word_count: number
}

export interface Citation {
  id: string
  text: string
  similarity_score: number
  document_title: string
  document_id: number
  snippet_index: number
  doi?: string
  url?: string
}

export interface UploadResponse {
  document: Document
}

export interface ApiError {
  detail: string
}