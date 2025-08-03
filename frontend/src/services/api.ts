import axios from 'axios'
import { Document, Assessment } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 30000,
})

export const documentApi = {
  async uploadFile(file: File): Promise<Document> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async uploadFromUrl(url: string): Promise<Document> {
    const formData = new FormData()
    formData.append('url', url)

    const response = await api.post('/documents/upload', formData)
    return response.data
  },

  async uploadFromDoi(doi: string): Promise<Document> {
    const formData = new FormData()
    formData.append('doi', doi)

    const response = await api.post('/documents/upload', formData)
    return response.data
  },

  async getDocument(id: number): Promise<Document> {
    const response = await api.get(`/documents/${id}`)
    return response.data
  },

  async listDocuments(): Promise<Document[]> {
    const response = await api.get('/documents/')
    return response.data
  }
}

export const assessmentApi = {
  async createAssessment(documentId: number, userClaim: string): Promise<Assessment> {
    const response = await api.post('/assessments/', {
      document_id: documentId,
      user_claim: userClaim
    })
    return response.data
  },

  async getAssessment(id: number): Promise<Assessment> {
    const response = await api.get(`/assessments/${id}`)
    return response.data
  },

  async getSharedAssessment(shareId: string): Promise<Assessment> {
    const response = await api.get(`/assessments/share/${shareId}`)
    return response.data
  },

  async submitFeedback(
    assessmentId: number,
    feedbackScore: number,
    comment?: string
  ): Promise<void> {
    await api.post(`/assessments/${assessmentId}/feedback`, {
      feedback_score: feedbackScore,
      feedback_comment: comment
    })
  }
}

export default api