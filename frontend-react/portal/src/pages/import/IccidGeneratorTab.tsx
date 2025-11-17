/**
 * ICCID Generator Tab Component
 * Generación de rangos de ICCID con algoritmo Luhn
 */

import { useState, useRef } from 'react'
import {
  Row, Col, Card, Button, Form, Table, Badge,
  Alert, InputGroup, Modal
} from 'react-bootstrap'
import { apiService } from '../../services/api.service'

interface Batch {
  id: string
  name: string
  iccid_start: string
  iccid_end: string
  count?: number
  status: 'pending' | 'calculated'
}

export default function IccidGeneratorTab() {
  const [batches, setBatches] = useState<Batch[]>([])
  const [currentBatch, setCurrentBatch] = useState({
    name: '',
    iccid_start: '',
    iccid_end: ''
  })
  const [error, setError] = useState<string | null>(null)
  const [calculating, setCalculating] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [generating, setGenerating] = useState(false)

  const iccidStartRef = useRef<HTMLInputElement>(null)
  const iccidEndRef = useRef<HTMLInputElement>(null)

  const handleAddBatch = async () => {
    if (!currentBatch.iccid_start || !currentBatch.iccid_end) {
      setError('Por favor ingrese ICCID inicial y final')
      return
    }

    setCalculating(true)
    setError(null)

    try {
      // Validar y calcular rango en el backend
      const response = await apiService.post('/api/app2/generate-iccid-range', null, {
        params: {
          iccid_start: currentBatch.iccid_start,
          iccid_end: currentBatch.iccid_end
        }
      })

      const newBatch: Batch = {
        id: Date.now().toString(),
        name: currentBatch.name || `Lote ${batches.length + 1}`,
        iccid_start: currentBatch.iccid_start,
        iccid_end: currentBatch.iccid_end,
        count: response.count,
        status: 'calculated'
      }

      setBatches([...batches, newBatch])

      // Limpiar form
      setCurrentBatch({
        name: '',
        iccid_start: '',
        iccid_end: ''
      })

      // Focus en el primer input
      setTimeout(() => iccidStartRef.current?.focus(), 100)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al calcular el rango de ICCID')
    } finally {
      setCalculating(false)
    }
  }

  const handleRemoveBatch = (id: string) => {
    setBatches(batches.filter(b => b.id !== id))
  }

  const handlePreview = async () => {
    if (batches.length === 0) {
      setError('Agregue al menos un lote para previsualizar')
      return
    }

    setCalculating(true)
    setError(null)

    try {
      // Obtener preview del primer lote
      const firstBatch = batches[0]
      const response = await apiService.post('/api/app2/generate-iccid-range', null, {
        params: {
          iccid_start: firstBatch.iccid_start,
          iccid_end: firstBatch.iccid_end
        }
      })

      // Mostrar primeros 10
      setPreviewData({
        batch_name: firstBatch.name,
        sample: response.iccids.slice(0, 10)
      })
      setShowPreview(true)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al generar preview')
    } finally {
      setCalculating(false)
    }
  }

  const handleGenerateCSV = async () => {
    if (batches.length === 0) {
      setError('Agregue al menos un lote para generar el CSV')
      return
    }

    setGenerating(true)
    setError(null)

    try {
      const batchesData = batches.map(b => ({
        name: b.name,
        iccid_start: b.iccid_start,
        iccid_end: b.iccid_end
      }))

      const response = await apiService.post('/api/app2/generate-iccid-csv', batchesData)

      // Descargar CSV
      const blob = new Blob([response.csv_content], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', response.filename)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Mostrar éxito
      alert(`CSV generado exitosamente!\nTotal ICCIDs: ${response.total_iccids}`)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al generar el archivo CSV')
    } finally {
      setGenerating(false)
    }
  }

  const getTotalICCIDs = () => {
    return batches.reduce((sum, b) => sum + (b.count || 0), 0)
  }

  return (
    <div>
      {/* Error Alert */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      <Row>
        {/* Formulario */}
        <Col lg={5}>
          <Card className="mb-4">
            <Card.Header className="bg-primary text-white">
              <i className="bi bi-plus-circle me-2"></i>
              Agregar Lote de SIM
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Nombre del Lote (opcional)</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Ej: Lote Vodafone 2025-01"
                    value={currentBatch.name}
                    onChange={(e) => setCurrentBatch({ ...currentBatch, name: e.target.value })}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    ICCID Inicial *
                    <small className="text-muted ms-2">(19-22 dígitos)</small>
                  </Form.Label>
                  <Form.Control
                    ref={iccidStartRef}
                    type="text"
                    placeholder="8934014042530750015"
                    value={currentBatch.iccid_start}
                    onChange={(e) => setCurrentBatch({ ...currentBatch, iccid_start: e.target.value.trim() })}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        iccidEndRef.current?.focus()
                      }
                    }}
                    autoFocus
                  />
                  <Form.Text className="text-muted">
                    <i className="bi bi-upc-scan me-1"></i>
                    Puede usar lector de código de barras
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>ICCID Final *</Form.Label>
                  <Form.Control
                    ref={iccidEndRef}
                    type="text"
                    placeholder="8934014042530780004"
                    value={currentBatch.iccid_end}
                    onChange={(e) => setCurrentBatch({ ...currentBatch, iccid_end: e.target.value.trim() })}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleAddBatch()
                      }
                    }}
                  />
                </Form.Group>

                <div className="d-grid gap-2">
                  <Button
                    variant="primary"
                    onClick={handleAddBatch}
                    disabled={calculating || !currentBatch.iccid_start || !currentBatch.iccid_end}
                  >
                    {calculating ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Calculando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-plus-lg me-2"></i>
                        Agregar Lote
                      </>
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>

          {/* Información */}
          <Card className="border-info">
            <Card.Header className="bg-info text-white">
              <i className="bi bi-info-circle me-2"></i>
              Información
            </Card.Header>
            <Card.Body>
              <ul className="small mb-0">
                <li>Los ICCIDs deben tener 19-22 dígitos</li>
                <li>Se recalculará el dígito de control Luhn automáticamente</li>
                <li>Puede usar un lector de código de barras en los campos</li>
                <li>Agregue múltiples lotes antes de generar el CSV</li>
                <li>El rango es inclusivo (inicio y fin incluidos)</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>

        {/* Lista de Lotes y Acciones */}
        <Col lg={7}>
          <Card className="mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>
                <i className="bi bi-list-check me-2"></i>
                Lotes Agregados ({batches.length})
              </span>
              {batches.length > 0 && (
                <Badge bg="primary" pill>
                  Total ICCIDs: {getTotalICCIDs().toLocaleString()}
                </Badge>
              )}
            </Card.Header>
            <Card.Body className="p-0">
              {batches.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                  <p className="text-muted mt-3">No hay lotes agregados</p>
                  <p className="text-muted small">Agregue el primer lote usando el formulario</p>
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Nombre</th>
                      <th>ICCID Inicial</th>
                      <th>ICCID Final</th>
                      <th>Cantidad</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {batches.map((batch) => (
                      <tr key={batch.id}>
                        <td>
                          <strong>{batch.name}</strong>
                        </td>
                        <td>
                          <code>{batch.iccid_start}</code>
                        </td>
                        <td>
                          <code>{batch.iccid_end}</code>
                        </td>
                        <td>
                          <Badge bg="success">{batch.count?.toLocaleString()}</Badge>
                        </td>
                        <td className="text-end">
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleRemoveBatch(batch.id)}
                          >
                            <i className="bi bi-trash"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>

          {/* Botones de Acción */}
          {batches.length > 0 && (
            <div className="d-flex gap-2 justify-content-end">
              <Button
                variant="outline-primary"
                onClick={handlePreview}
                disabled={calculating}
              >
                <i className="bi bi-eye me-2"></i>
                Vista Previa
              </Button>

              <Button
                variant="success"
                size="lg"
                onClick={handleGenerateCSV}
                disabled={generating}
              >
                {generating ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2"></span>
                    Generando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-file-earmark-arrow-down me-2"></i>
                    Generar y Descargar CSV
                  </>
                )}
              </Button>
            </div>
          )}
        </Col>
      </Row>

      {/* Preview Modal */}
      <Modal show={showPreview} onHide={() => setShowPreview(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-eye me-2"></i>
            Vista Previa - {previewData?.batch_name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {previewData && (
            <>
              <p className="text-muted">Primeros 10 ICCIDs generados (se recalculó el dígito Luhn):</p>
              <Table striped bordered size="sm">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>ICCID Completo</th>
                    <th>Body</th>
                    <th>Check Digit</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.sample.map((item: any, idx: number) => (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td><code>{item.iccid}</code></td>
                      <td><small className="text-muted">{item.body}</small></td>
                      <td><Badge bg="info">{item.check_digit}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              <Alert variant="info" className="mt-3 mb-0">
                <small>
                  <i className="bi bi-info-circle me-2"></i>
                  Esta es una muestra. El archivo CSV contendrá todos los ICCIDs del rango.
                </small>
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPreview(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  )
}
