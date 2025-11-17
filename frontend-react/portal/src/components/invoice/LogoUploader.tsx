/**
 * Logo Uploader Component
 * Componente para subir y previsualizar el logo de la empresa
 */

import { useState, useRef } from 'react'
import { Card, Button, Spinner } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import toast from 'react-hot-toast'

interface LogoUploaderProps {
  currentLogoUrl?: string
  onLogoUploaded: (url: string) => void
}

export default function LogoUploader({ currentLogoUrl, onLogoUploaded }: LogoUploaderProps) {
  const [uploading, setUploading] = useState(false)
  const [preview, setPreview] = useState<string | undefined>(currentLogoUrl)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Por favor selecciona una imagen válida')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('La imagen es muy grande. Máximo 5MB')
      return
    }

    try {
      setUploading(true)

      // Preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)

      // Upload
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiService.upload('/api/app5/config/upload-logo', formData)

      if (response.logo_url) {
        onLogoUploaded(response.logo_url)
        toast.success('Logo subido correctamente')
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error subiendo logo')
      setPreview(currentLogoUrl)
    } finally {
      setUploading(false)
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)

    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => {
    setDragOver(false)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemove = () => {
    setPreview(undefined)
    onLogoUploaded('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
      />

      <Card
        className={`text-center ${dragOver ? 'border-primary' : ''}`}
        style={{
          cursor: 'pointer',
          borderStyle: 'dashed',
          borderWidth: '2px',
          transition: 'all 0.3s'
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <Card.Body className="py-4">
          {uploading ? (
            <div>
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 mb-0 text-muted">Subiendo logo...</p>
            </div>
          ) : preview ? (
            <div>
              <img
                src={preview}
                alt="Logo preview"
                style={{
                  maxWidth: '200px',
                  maxHeight: '100px',
                  objectFit: 'contain'
                }}
              />
              <div className="mt-3">
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRemove()
                  }}
                >
                  <i className="bi bi-trash me-1"></i>
                  Eliminar
                </Button>
              </div>
            </div>
          ) : (
            <div>
              <i className="bi bi-cloud-upload" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
              <p className="mt-3 mb-1">
                <strong>Arrastra una imagen aquí</strong>
              </p>
              <p className="text-muted mb-0">
                o haz clic para seleccionar
              </p>
              <small className="text-muted">Formatos: PNG, JPG, SVG (max. 5MB)</small>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  )
}
