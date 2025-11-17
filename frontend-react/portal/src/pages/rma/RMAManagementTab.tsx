/**
 * RMA Management Tab
 * Gestión completa de casos RMA con importación masiva y escáner
 */

import { useState, useEffect, useRef } from 'react'
import {
  Row, Col, Card, Button, Badge, Table, Modal, Form, Alert,
  InputGroup, Tabs, Tab
} from 'react-bootstrap'
import { apiService } from '../../services/api.service'

interface RMA {
  id: string
  rma_number: string
  imei: string
  customer_name: string
  rma_type: string
  status: string
  reason: string
  ticket_number?: string
  created_at: string
  processing_time_days: number
}

interface RMADetails extends RMA {
  device_id: string
  customer_id: string
  reason_detail?: string
  under_warranty: boolean
  warranty_void: boolean
  replacement_imei?: string
  notes: any[]
  resolution?: string
}

export default function RMAManagementTab() {
  const [rmas, setRmas] = useState<RMA[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Details modal
  const [showDetails, setShowDetails] = useState(false)
  const [selectedRMA, setSelectedRMA] = useState<RMADetails | null>(null)
  const [newStatus, setNewStatus] = useState('')
  const [statusNotes, setStatusNotes] = useState('')

  // CSV Import modal
  const [showImport, setShowImport] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importResults, setImportResults] = useState<any>(null)

  // Barcode Scanner modal
  const [showScanner, setShowScanner] = useState(false)
  const [scannedIMEIs, setScannedIMEIs] = useState<string[]>([])
  const [currentScan, setCurrentScan] = useState('')
  const [scannerConfig, setScannerConfig] = useState({
    rma_type: 'repair',
    reason: 'defective',
    reason_detail: ''
  })
  const scanInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadRMAs()
  }, [])

  useEffect(() => {
    // Auto-focus scanner input when modal opens
    if (showScanner && scanInputRef.current) {
      scanInputRef.current.focus()
    }
  }, [showScanner])

  const loadRMAs = async () => {
    setLoading(true)
    try {
      const response = await apiService.get('/api/app3/rma?limit=100')
      setRmas(response.rma_cases || [])
      setError(null)
    } catch (err: any) {
      setError('Error cargando casos RMA')
    } finally {
      setLoading(false)
    }
  }

  const handleViewRMA = async (rmaId: string) => {
    try {
      const response = await apiService.get(`/api/app3/rma/${rmaId}`)
      setSelectedRMA(response.rma)
      setNewStatus(response.rma.status)
      setShowDetails(true)
    } catch (err: any) {
      setError('Error cargando detalles del RMA')
    }
  }

  const handleUpdateStatus = async () => {
    if (!selectedRMA) return

    try {
      await apiService.patch(`/api/app3/rma/${selectedRMA.id}/status`, {
        status: newStatus,
        notes: statusNotes || undefined
      })

      setSuccess('Estado de RMA actualizado')
      setShowDetails(false)
      setStatusNotes('')
      loadRMAs()
    } catch (err: any) {
      setError('Error actualizando RMA')
    }
  }

  const handleImportCSV = async () => {
    if (!importFile) return

    try {
      const formData = new FormData()
      formData.append('file', importFile)

      const response = await apiService.upload('/api/app3/rma/bulk-import', formData)
      setImportResults(response.results)
      setSuccess(response.message)
      loadRMAs()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error importando RMA')
    }
  }

  const handleScanEnter = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && currentScan.trim()) {
      e.preventDefault()
      // Add to list if not duplicate
      if (!scannedIMEIs.includes(currentScan.trim())) {
        setScannedIMEIs(prev => [...prev, currentScan.trim()])
      }
      setCurrentScan('')
      // Keep focus on input
      setTimeout(() => scanInputRef.current?.focus(), 10)
    }
  }

  const handleCreateFromScanned = async () => {
    if (scannedIMEIs.length === 0) return

    try {
      const response = await apiService.post('/api/app3/rma/bulk-create', {
        imeis: scannedIMEIs,
        ...scannerConfig
      })

      setSuccess(response.message)
      setScannedIMEIs([])
      setShowScanner(false)
      loadRMAs()
    } catch (err: any) {
      setError('Error creando RMA desde escáner')
    }
  }

  const getStatusBadge = (status: string) => {
    const config: Record<string, { bg: string; label: string }> = {
      initiated: { bg: 'secondary', label: 'Iniciado' },
      pending_approval: { bg: 'warning', label: 'Pendiente Aprobación' },
      approved: { bg: 'success', label: 'Aprobado' },
      rejected: { bg: 'danger', label: 'Rechazado' },
      device_received: { bg: 'info', label: 'Dispositivo Recibido' },
      under_inspection: { bg: 'info', label: 'En Inspección' },
      repair_in_progress: { bg: 'primary', label: 'Reparando' },
      replacement_prepared: { bg: 'primary', label: 'Reemplazo Preparado' },
      shipped_to_customer: { bg: 'success', label: 'Enviado a Cliente' },
      completed: { bg: 'success', label: 'Completado' },
      cancelled: { bg: 'dark', label: 'Cancelado' }
    }
    const conf = config[status] || { bg: 'secondary', label: status }
    return <Badge bg={conf.bg}>{conf.label}</Badge>
  }

  const downloadCSVTemplate = () => {
    const template = 'imei,customer_name,customer_email,rma_type,reason,reason_detail\n' +
      '123456789012345,Juan Pérez,juan@email.com,repair,defective,Pantalla rota\n' +
      '987654321098765,María García,maria@email.com,replacement,doa,No enciende'

    const blob = new Blob([template], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'plantilla_rma.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <>
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h5 className="mb-1">
            <i className="bi bi-box-seam me-2 text-danger"></i>
            Gestión de RMA
          </h5>
          <p className="text-muted mb-0 small">
            Devoluciones, reparaciones y reemplazos
          </p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="success" size="sm" onClick={() => setShowScanner(true)}>
            <i className="bi bi-upc-scan me-2"></i>
            Escanear Códigos
          </Button>
          <Button variant="primary" size="sm" onClick={() => setShowImport(true)}>
            <i className="bi bi-file-earmark-arrow-up me-2"></i>
            Importar CSV
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Stats */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body className="py-3">
              <h4 className="mb-0">{rmas.length}</h4>
              <small className="text-muted">Total RMA</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-warning">
            <Card.Body className="py-3">
              <h4 className="mb-0 text-warning">
                {rmas.filter(r => r.status === 'pending_approval').length}
              </h4>
              <small className="text-muted">Pendientes</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-primary">
            <Card.Body className="py-3">
              <h4 className="mb-0 text-primary">
                {rmas.filter(r => ['repair_in_progress', 'under_inspection'].includes(r.status)).length}
              </h4>
              <small className="text-muted">En Proceso</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-success">
            <Card.Body className="py-3">
              <h4 className="mb-0 text-success">
                {rmas.filter(r => r.status === 'completed').length}
              </h4>
              <small className="text-muted">Completados</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* RMA Table */}
      <Card>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Cargando...</span>
              </div>
            </div>
          ) : rmas.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
              <p className="text-muted mt-3">No hay casos RMA registrados</p>
              <Button variant="primary" onClick={() => setShowScanner(true)}>
                Crear primer RMA
              </Button>
            </div>
          ) : (
            <Table hover responsive className="mb-0">
              <thead className="table-light">
                <tr>
                  <th>RMA #</th>
                  <th>IMEI</th>
                  <th>Cliente</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Razón</th>
                  <th>Ticket</th>
                  <th>Días</th>
                  <th>Fecha</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rmas.map((rma) => (
                  <tr key={rma.id}>
                    <td><strong>{rma.rma_number}</strong></td>
                    <td><code>{rma.imei}</code></td>
                    <td>{rma.customer_name}</td>
                    <td>
                      <Badge bg="info">{rma.rma_type}</Badge>
                    </td>
                    <td>{getStatusBadge(rma.status)}</td>
                    <td><small>{rma.reason}</small></td>
                    <td>
                      {rma.ticket_number ? (
                        <code className="small">{rma.ticket_number}</code>
                      ) : (
                        <span className="text-muted">-</span>
                      )}
                    </td>
                    <td>
                      <Badge bg={rma.processing_time_days > 7 ? 'danger' : 'secondary'}>
                        {rma.processing_time_days}d
                      </Badge>
                    </td>
                    <td>
                      <small className="text-muted">
                        {new Date(rma.created_at).toLocaleDateString()}
                      </small>
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => handleViewRMA(rma.id)}
                      >
                        <i className="bi bi-eye"></i>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* RMA Details Modal */}
      <Modal show={showDetails} onHide={() => setShowDetails(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedRMA?.rma_number} - {getStatusBadge(selectedRMA?.status || '')}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedRMA && (
            <>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>IMEI:</strong> <code>{selectedRMA.imei}</code>
                </Col>
                <Col md={6}>
                  <strong>Cliente:</strong> {selectedRMA.customer_name}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Tipo RMA:</strong> <Badge bg="info">{selectedRMA.rma_type}</Badge>
                </Col>
                <Col md={6}>
                  <strong>Razón:</strong> {selectedRMA.reason}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Garantía:</strong>{' '}
                  {selectedRMA.under_warranty ? (
                    <Badge bg="success">Válida</Badge>
                  ) : (
                    <Badge bg="secondary">No</Badge>
                  )}
                </Col>
                <Col md={6}>
                  <strong>Días en proceso:</strong>{' '}
                  <Badge bg={selectedRMA.processing_time_days > 7 ? 'danger' : 'secondary'}>
                    {selectedRMA.processing_time_days} días
                  </Badge>
                </Col>
              </Row>

              {selectedRMA.reason_detail && (
                <div className="mb-3">
                  <strong>Detalle:</strong>
                  <p className="mt-1 text-muted">{selectedRMA.reason_detail}</p>
                </div>
              )}

              {selectedRMA.replacement_imei && (
                <div className="mb-3">
                  <strong>IMEI de reemplazo:</strong> <code>{selectedRMA.replacement_imei}</code>
                </div>
              )}

              <hr />

              {/* Change Status */}
              <h6>Cambiar Estado</h6>
              <Form.Group className="mb-3">
                <Form.Select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
                  <option value="initiated">Iniciado</option>
                  <option value="pending_approval">Pendiente Aprobación</option>
                  <option value="approved">Aprobado</option>
                  <option value="rejected">Rechazado</option>
                  <option value="device_received">Dispositivo Recibido</option>
                  <option value="under_inspection">En Inspección</option>
                  <option value="repair_in_progress">Reparación en Progreso</option>
                  <option value="replacement_prepared">Reemplazo Preparado</option>
                  <option value="shipped_to_customer">Enviado a Cliente</option>
                  <option value="completed">Completado</option>
                  <option value="cancelled">Cancelado</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Notas del cambio (opcional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  placeholder="Comentarios sobre el cambio de estado..."
                  value={statusNotes}
                  onChange={(e) => setStatusNotes(e.target.value)}
                />
              </Form.Group>

              <Button
                variant="primary"
                onClick={handleUpdateStatus}
                disabled={newStatus === selectedRMA.status}
              >
                Actualizar Estado
              </Button>

              {/* Notes */}
              {selectedRMA.notes && selectedRMA.notes.length > 0 && (
                <>
                  <hr />
                  <h6>Historial de Notas</h6>
                  <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    {selectedRMA.notes.map((note: any, idx: number) => (
                      <Card key={idx} className="mb-2">
                        <Card.Body className="p-2">
                          <small className="text-muted">
                            {note.author_name} - {new Date(note.timestamp).toLocaleString()}
                          </small>
                          <p className="mb-0 mt-1">{note.text}</p>
                        </Card.Body>
                      </Card>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </Modal.Body>
      </Modal>

      {/* CSV Import Modal */}
      <Modal show={showImport} onHide={() => setShowImport(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Importar RMA desde CSV</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="info">
            <strong>Formato del archivo CSV:</strong>
            <br />
            <code>imei,customer_name,customer_email,rma_type,reason,reason_detail</code>
            <br />
            <br />
            <strong>Tipos de RMA:</strong> repair, replacement, refund, exchange
            <br />
            <strong>Razones:</strong> defective, doa, warranty_claim, customer_dissatisfaction, wrong_product, damaged_in_transit, other
          </Alert>

          <Button variant="outline-secondary" size="sm" className="mb-3" onClick={downloadCSVTemplate}>
            <i className="bi bi-download me-2"></i>
            Descargar Plantilla CSV
          </Button>

          <Form.Group className="mb-3">
            <Form.Label>Seleccionar archivo CSV</Form.Label>
            <Form.Control
              type="file"
              accept=".csv"
              onChange={(e: any) => setImportFile(e.target.files?.[0] || null)}
            />
          </Form.Group>

          {importResults && (
            <Alert variant={importResults.errors.length > 0 ? 'warning' : 'success'}>
              <strong>Resultados:</strong>
              <br />
              Total: {importResults.total} | Exitosos: {importResults.success} | Errores: {importResults.errors.length}
              {importResults.errors.length > 0 && (
                <div className="mt-2">
                  <strong>Errores:</strong>
                  <ul className="mb-0">
                    {importResults.errors.slice(0, 5).map((err: any, idx: number) => (
                      <li key={idx}>
                        Fila {err.row}: {err.error}
                      </li>
                    ))}
                    {importResults.errors.length > 5 && (
                      <li>... y {importResults.errors.length - 5} más</li>
                    )}
                  </ul>
                </div>
              )}
            </Alert>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => {
            setShowImport(false)
            setImportResults(null)
            setImportFile(null)
          }}>
            Cerrar
          </Button>
          <Button
            variant="primary"
            onClick={handleImportCSV}
            disabled={!importFile}
          >
            <i className="bi bi-upload me-2"></i>
            Importar
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Barcode Scanner Modal */}
      <Modal show={showScanner} onHide={() => setShowScanner(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-upc-scan me-2"></i>
            Escanear Códigos de Barras
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="info">
            <strong>Instrucciones:</strong>
            <ol className="mb-0">
              <li>Configure el tipo y razón del RMA</li>
              <li>Use su lector de códigos de barras o escriba el IMEI</li>
              <li>Presione Enter después de cada escaneo</li>
              <li>Los códigos aparecerán en la lista inferior</li>
            </ol>
          </Alert>

          {/* Scanner Configuration */}
          <Row className="mb-3">
            <Col md={4}>
              <Form.Group>
                <Form.Label>Tipo RMA</Form.Label>
                <Form.Select
                  value={scannerConfig.rma_type}
                  onChange={(e) => setScannerConfig({ ...scannerConfig, rma_type: e.target.value })}
                >
                  <option value="repair">Reparación</option>
                  <option value="replacement">Reemplazo</option>
                  <option value="refund">Reembolso</option>
                  <option value="exchange">Intercambio</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>Razón</Form.Label>
                <Form.Select
                  value={scannerConfig.reason}
                  onChange={(e) => setScannerConfig({ ...scannerConfig, reason: e.target.value })}
                >
                  <option value="defective">Defectuoso</option>
                  <option value="doa">DOA (No Funciona)</option>
                  <option value="warranty_claim">Garantía</option>
                  <option value="damaged_in_transit">Dañado en envío</option>
                  <option value="other">Otro</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>Detalle (opcional)</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Ej: Pantalla rota"
                  value={scannerConfig.reason_detail}
                  onChange={(e) => setScannerConfig({ ...scannerConfig, reason_detail: e.target.value })}
                />
              </Form.Group>
            </Col>
          </Row>

          {/* Scanner Input */}
          <Form.Group className="mb-3">
            <Form.Label>Escanear IMEI (presione Enter después de cada código)</Form.Label>
            <Form.Control
              ref={scanInputRef}
              type="text"
              placeholder="Escanee o escriba el IMEI..."
              value={currentScan}
              onChange={(e) => setCurrentScan(e.target.value)}
              onKeyDown={handleScanEnter}
              autoFocus
            />
            <Form.Text className="text-muted">
              Total escaneados: {scannedIMEIs.length}
            </Form.Text>
          </Form.Group>

          {/* Scanned List */}
          {scannedIMEIs.length > 0 && (
            <Card>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <span>IMEIs Escaneados ({scannedIMEIs.length})</span>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => setScannedIMEIs([])}
                >
                  Limpiar
                </Button>
              </Card.Header>
              <Card.Body style={{ maxHeight: '200px', overflowY: 'auto' }}>
                <div className="d-flex flex-wrap gap-2">
                  {scannedIMEIs.map((imei, idx) => (
                    <Badge
                      key={idx}
                      bg="primary"
                      className="d-flex align-items-center gap-2"
                    >
                      <code>{imei}</code>
                      <i
                        className="bi bi-x-circle"
                        style={{ cursor: 'pointer' }}
                        onClick={() => setScannedIMEIs(prev => prev.filter((_, i) => i !== idx))}
                      ></i>
                    </Badge>
                  ))}
                </div>
              </Card.Body>
            </Card>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => {
            setShowScanner(false)
            setScannedIMEIs([])
            setCurrentScan('')
          }}>
            Cancelar
          </Button>
          <Button
            variant="success"
            onClick={handleCreateFromScanned}
            disabled={scannedIMEIs.length === 0}
          >
            <i className="bi bi-check-circle me-2"></i>
            Crear {scannedIMEIs.length} RMA
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  )
}
