import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { DocumentIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'
import { documentApi } from '../services/api'
import { Document } from '../types'

interface FileUploadProps {
  onUpload: (document: Document) => void
  onError: (error: string) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function FileUpload({ onUpload, onError, isLoading, setIsLoading }: FileUploadProps) {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      onError('Please upload a PDF or DOCX file')
      return
    }

    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      onError('File size must be less than 50MB')
      return
    }

    setIsLoading(true)
    try {
      const document = await documentApi.uploadFile(file)
      onUpload(document)
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to upload file'
      onError(message)
    } finally {
      setIsLoading(false)
    }
  }, [onUpload, onError, setIsLoading])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false,
    disabled: isLoading
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-200
        ${isDragActive
          ? 'border-primary-400 bg-primary-50'
          : 'border-gray-300 hover:border-gray-400'
        }
        ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
      `}
      role="button"
      tabIndex={0}
      aria-label="Upload PDF or DOCX file"
      aria-describedby="file-upload-description"
    >
      <input {...getInputProps()} aria-hidden="true" />

      <div className="space-y-2">
        {isLoading ? (
          <>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" aria-hidden="true"></div>
            <p className="text-sm text-gray-600">Processing...</p>
          </>
        ) : (
          <>
            {isDragActive ? (
              <ArrowUpTrayIcon className="mx-auto h-8 w-8 text-primary-400" aria-hidden="true" />
            ) : (
              <DocumentIcon className="mx-auto h-8 w-8 text-gray-400" aria-hidden="true" />
            )}

            <div>
              <p className="text-sm font-medium text-gray-900">
                {isDragActive ? 'Drop the file here' : 'Drop a file here, or click to select'}
              </p>
              <p id="file-upload-description" className="text-xs text-gray-500 mt-1">
                PDF or DOCX files up to 50MB
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}