/**
 * OSE Platform - Brand Update Page
 * Página para actualizar marcas mediante archivo
 */

import { useState } from 'react'
import { Container, Row, Col, Card, Form, Button, Alert, Table, Badge, ProgressBar, Spinner } from 'react-bootstrap'
import apiService from '@/services/api.service'
import toast from 'react-hot-toast'

interface UpdateResult {
  numero_serie: string
  marca?: string
  marca_anterior?: string
  marca_nueva?: string
  status: 'updated' | 'not_found' | 'no_change'
  message: string
}

interface ProcessingStats {
  total: number
  found: number
  updated: number
  not_found: number
  no_change: number
  errors: any[]
  details: UpdateResult[]
}

export default function BrandUpdatePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [processing, setProcessing] = useState(false)
  const [results, setResults] = useState<ProcessingStats | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validar extensión
      const validExtensions = ['.xlsx', '.xls', '.csv']
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()

      if (!validExtensions.includes(fileExtension)) {
        toast.error('Formato de archivo no válido. Use Excel (.xlsx, .xls) o CSV (.csv)')
        return
      }

      setSelectedFile(file)
      setResults(null) // Limpiar resultados anteriores
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Por favor seleccione un archivo')
      return
    }

    setProcessing(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await apiService.upload<any>('/api/v1/upload-brand-file', formData)

      setResults(response.statistics)
      toast.success(response.message)

    } catch (error: any) {
      console.error('Error al procesar archivo:', error)
      const errorMessage = error.response?.data?.detail || 'Error al procesar el archivo'
      toast.error(errorMessage)
    } finally {
      setProcessing(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { variant: string; text: string }> = {
      updated: { variant: 'success', text: 'Actualizado' },
      not_found: { variant: 'danger', text: 'No encontrado' },
      no_change: { variant: 'info', text: 'Sin cambios' }
    }
    return badges[status] || { variant: 'secondary', text: status }
  }

  return (
    <Container fluid className="p-4">
      <Row className="mb-4">
        <Col>
          <h2>
            <i className="bi bi-tag-fill me-2"></i>
            Actualización de Marcas
          </h2>
          <p className="text-muted">
            Suba un archivo Excel o CSV para actualizar las marcas de los dispositivos
          </p>
        </Col>
      </Row>

      {/* Instrucciones */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <i className="bi bi-info-circle me-2"></i>
              Instrucciones
            </Card.Header>
            <Card.Body>
              <h6>Formato del archivo:</h6>
              <p className="mb-2">El archivo debe contener las siguientes columnas:</p>
              <ul>
                <li>
                  <strong>numero_serie</strong> (o imei, iccid, serial): Número de serie IMEI o ICCID del dispositivo
                </li>
                <li>
                  <strong>marca</strong> (o brand, manufacturer): Nueva marca a asignar
                </li>
              </ul>

              <Alert variant="info" className="mb-0">
                <i className="bi bi-lightbulb me-2"></i>
                <strong>Tip:</strong> El sistema buscará automáticamente cada dispositivo por IMEI o ICCID y actualizará la marca si es necesaria
              </Alert>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Upload Section */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <i className="bi bi-cloud-upload me-2"></i>
              Subir Archivo
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Seleccionar archivo Excel o CSV</Form.Label>
                <Form.Control
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileChange}
                  disabled={processing}
                />
                {selectedFile && (
                  <Form.Text className="text-muted">
                    <i className="bi bi-file-earmark me-1"></i>
                    {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                  </Form.Text>
                )}
              </Form.Group>

              <Button
                variant="primary"
                onClick={handleUpload}
                disabled={!selectedFile || processing}
                className="w-100"
              >
                {processing ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Procesando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-upload me-2"></i>
                    Procesar Archivo
                  </>
                )}
              </Button>
            </Card.Body>
          </Card>
        </Col>

        {/* Statistics */}
        {results && (
          <Col md={6}>
            <Card>
              <Card.Header>
                <i className="bi bi-graph-up me-2"></i>
                Estadísticas
              </Card.Header>
              <Card.Body>
                <Table bordered size="sm" className="mb-0">
                  <tbody>
                    <tr>
                      <td><strong>Total de registros:</strong></td>
                      <td className="text-end">{results.total.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td><strong>Encontrados en BD:</strong></td>
                      <td className="text-end text-success">{results.found.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td><strong>Actualizados:</strong></td>
                      <td className="text-end text-primary fw-bold">{results.updated.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td><strong>Sin cambios:</strong></td>
                      <td className="text-end text-info">{results.no_change.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td><strong>No encontrados:</strong></td>
                      <td className="text-end text-danger">{results.not_found.toLocaleString()}</td>
                    </tr>
                    {results.errors.length > 0 && (
                      <tr>
                        <td><strong>Errores:</strong></td>
                        <td className="text-end text-warning">{results.errors.length}</td>
                      </tr>
                    )}
                  </tbody>
                </Table>

                <div className="mt-3">
                  <small className="text-muted">Tasa de éxito</small>
                  <ProgressBar>
                    <ProgressBar
                      variant="success"
                      now={(results.updated / results.total) * 100}
                      label={`${results.updated}`}
                    />
                    <ProgressBar
                      variant="info"
                      now={(results.no_change / results.total) * 100}
                      label={`${results.no_change}`}
                    />
                    <ProgressBar
                      variant="danger"
                      now={(results.not_found / results.total) * 100}
                      label={`${results.not_found}`}
                    />
                  </ProgressBar>
                </div>
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Results Table */}
      {results && results.details.length > 0 && (
        <Row>
          <Col>
            <Card>
              <Card.Header>
                <i className="bi bi-list-check me-2"></i>
                Detalles del Procesamiento ({results.details.length} registros)
              </Card.Header>
              <Card.Body style={{ maxHeight: '500px', overflowY: 'auto' }}>
                <Table striped bordered hover size="sm">
                  <thead style={{ position: 'sticky', top: 0, background: 'white', zIndex: 1 }}>
                    <tr>
                      <th>Número de Serie</th>
                      <th>Estado</th>
                      <th>Marca Anterior</th>
                      <th>Marca Nueva</th>
                      <th>Mensaje</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.details.map((detail, index) => {
                      const badge = getStatusBadge(detail.status)
                      return (
                        <tr key={index}>
                          <td>
                            <code>{detail.numero_serie}</code>
                          </td>
                          <td>
                            <Badge bg={badge.variant}>{badge.text}</Badge>
                          </td>
                          <td>{detail.marca_anterior || '-'}</td>
                          <td>{detail.marca_nueva || detail.marca || '-'}</td>
                          <td className="small text-muted">{detail.message}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Errors Table */}
      {results && results.errors.length > 0 && (
        <Row className="mt-4">
          <Col>
            <Card border="warning">
              <Card.Header className="bg-warning text-dark">
                <i className="bi bi-exclamation-triangle me-2"></i>
                Errores ({results.errors.length})
              </Card.Header>
              <Card.Body>
                <Table striped bordered hover size="sm">
                  <thead>
                    <tr>
                      <th>Fila</th>
                      <th>Número de Serie</th>
                      <th>Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.errors.map((error, index) => (
                      <tr key={index}>
                        <td>{error.row}</td>
                        <td><code>{error.numero_serie}</code></td>
                        <td className="text-danger">{error.error}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  )
}
