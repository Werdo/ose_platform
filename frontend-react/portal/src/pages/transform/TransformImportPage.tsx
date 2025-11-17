/**
 * App 4: Transform & Import Page
 * Transformación e importación de documentos con plantillas
 */

import { useState, useEffect, useRef } from 'react'
import {
  Container, Row, Col, Card, Button, Alert, Table,
  ProgressBar, Badge, Form, Modal, Tabs, Tab,
  Spinner
} from 'react-bootstrap'
import { apiService } from '../../services/api.service'

// ════════════════════════════════════════════════════════════════════════
// INTERFACES
// ════════════════════════════════════════════════════════════════════════

interface Template {
  id: string
  name: string
  description: string
  destination: string
  file_types: string[]
  mapping: Record<string, string>
  usage_count: number
  created_at: string
  last_used_at: string
}

interface TransformResult {
  success: boolean
  total_rows: number
  preview_rows: number
  columns: string[]
  preview: any[]
  template_applied: string | null
}

interface ImportJob {
  id: string
  job_number: string
  filename: string
  destination: string
  status: string
  progress: number
  total_rows: number
  successful_rows: number
  failed_rows: number
  created_at: string
  employee_name: string
}

interface JobDetail extends ImportJob {
  file_type: string
  processed_rows: number
  skipped_rows: number
  errors: any[]
  warnings: any[]
  preview_data: any[]
  started_at: string
  completed_at: string
  duration_seconds: number
  success_rate: number
  template_name: string
}

// ════════════════════════════════════════════════════════════════════════
// COMPONENT
// ════════════════════════════════════════════════════════════════════════

export default function TransformImportPage() {
  // State
  const [activeTab, setActiveTab] = useState<string>('transform')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [selectedDestination, setSelectedDestination] = useState<string>('devices')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  // Transform
  const [transformResult, setTransformResult] = useState<TransformResult | null>(null)

  // Templates
  const [templates, setTemplates] = useState<Template[]>([])
  const [loadingTemplates, setLoadingTemplates] = useState(false)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    destination: 'devices',
    mapping: '{}',
    validation: '{}',
    default_values: '{}'
  })

  // Jobs
  const [jobs, setJobs] = useState<ImportJob[]>([])
  const [loadingJobs, setLoadingJobs] = useState(false)
  const [selectedJob, setSelectedJob] = useState<JobDetail | null>(null)
  const [showJobModal, setShowJobModal] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  // ════════════════════════════════════════════════════════════════════
  // EFFECTS
  // ════════════════════════════════════════════════════════════════════

  useEffect(() => {
    loadTemplates()
    loadJobs()
  }, [])

  // ════════════════════════════════════════════════════════════════════
  // API CALLS
  // ════════════════════════════════════════════════════════════════════

  const loadTemplates = async () => {
    setLoadingTemplates(true)
    try {
      const response = await apiService.get('/api/app4/plantillas')
      setTemplates(response.templates || [])
    } catch (err: any) {
      console.error('Error cargando plantillas:', err)
    } finally {
      setLoadingTemplates(false)
    }
  }

  const loadJobs = async () => {
    setLoadingJobs(true)
    try {
      const response = await apiService.get('/api/app4/jobs?limit=20')
      setJobs(response.jobs || [])
    } catch (err: any) {
      console.error('Error cargando jobs:', err)
    } finally {
      setLoadingJobs(false)
    }
  }

  const loadJobDetail = async (jobId: string) => {
    try {
      const response = await apiService.get(`/api/app4/jobs/${jobId}`)
      setSelectedJob(response.job)
      setShowJobModal(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error cargando detalle del job')
    }
  }

  // ════════════════════════════════════════════════════════════════════
  // FILE HANDLERS
  // ════════════════════════════════════════════════════════════════════

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
      setError(null)
      setSuccess(null)
      setTransformResult(null)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)

    const files = event.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]

      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
        setSelectedFile(file)
        setError(null)
        setSuccess(null)
        setTransformResult(null)
      } else {
        setError('Tipo de archivo no válido. Use .xlsx, .xls o .csv')
      }
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
  }

  // ════════════════════════════════════════════════════════════════════
  // TRANSFORM & IMPORT
  // ════════════════════════════════════════════════════════════════════

  const handleTransform = async () => {
    if (!selectedFile) {
      setError('Por favor seleccione un archivo')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    setTransformResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (selectedTemplate) {
        formData.append('template_id', selectedTemplate)
      }

      const response = await apiService.upload('/api/app4/transformar', formData)

      setTransformResult(response)
      setSuccess('Archivo transformado exitosamente. Vista previa disponible.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al transformar el archivo')
    } finally {
      setLoading(false)
    }
  }

  const handleImport = async () => {
    if (!selectedFile) {
      setError('Por favor seleccione un archivo')
      return
    }

    if (!selectedDestination) {
      setError('Por favor seleccione un destino')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (selectedTemplate) {
        formData.append('template_id', selectedTemplate)
      }

      const response = await apiService.upload(
        `/api/app4/importar/${selectedDestination}`,
        formData
      )

      setSuccess(`Importación completada exitosamente. Job: ${response.job.job_number}`)
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Recargar jobs
      await loadJobs()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al importar el archivo')
    } finally {
      setLoading(false)
    }
  }

  // ════════════════════════════════════════════════════════════════════
  // TEMPLATE MANAGEMENT
  // ════════════════════════════════════════════════════════════════════

  const handleCreateTemplate = async () => {
    setLoading(true)
    setError(null)

    try {
      // Validar JSONs
      const mapping = JSON.parse(templateForm.mapping)
      const validation = JSON.parse(templateForm.validation)
      const default_values = JSON.parse(templateForm.default_values)

      await apiService.post('/api/app4/plantillas', {
        name: templateForm.name,
        description: templateForm.description,
        destination: templateForm.destination,
        mapping,
        validation,
        default_values
      })

      setSuccess('Plantilla creada exitosamente')
      setShowTemplateModal(false)
      setTemplateForm({
        name: '',
        description: '',
        destination: 'devices',
        mapping: '{}',
        validation: '{}',
        default_values: '{}'
      })

      await loadTemplates()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear plantilla')
    } finally {
      setLoading(false)
    }
  }

  // ════════════════════════════════════════════════════════════════════
  // UTILITIES
  // ════════════════════════════════════════════════════════════════════

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: 'secondary',
      processing: 'primary',
      completed: 'success',
      failed: 'danger',
      partial: 'warning'
    }
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / 1048576).toFixed(2) + ' MB'
  }

  // ════════════════════════════════════════════════════════════════════
  // RENDER
  // ════════════════════════════════════════════════════════════════════

  return (
    <Container fluid className="p-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-1">
            <i className="bi bi-arrow-left-right me-2 text-primary"></i>
            App 4: Transform & Import
          </h4>
          <p className="text-muted mb-0">
            Transformación e importación de documentos con plantillas configurables
          </p>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          <i className="bi bi-check-circle-fill me-2"></i>
          {success}
        </Alert>
      )}

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k || 'transform')}
        className="mb-4"
      >
        {/* ═══════════════════════════════════════════════════════════ */}
        {/* TAB: TRANSFORMAR */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <Tab eventKey="transform" title={<span><i className="bi bi-shuffle me-2"></i>Transformar</span>}>
          <Row>
            <Col lg={8}>
              {/* File Upload */}
              <Card
                className={`mb-4 ${isDragging ? 'border-primary bg-light' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                style={{ borderStyle: 'dashed', borderWidth: '2px' }}
              >
                <Card.Body className="text-center py-5">
                  <i className="bi bi-cloud-upload" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
                  <h5 className="mt-3">Arrastra tu archivo aquí</h5>
                  <p className="text-muted">o haz clic para seleccionar</p>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />

                  <Button
                    variant="outline-primary"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                  >
                    <i className="bi bi-folder2-open me-2"></i>
                    Seleccionar Archivo
                  </Button>

                  <div className="mt-3">
                    <small className="text-muted">
                      Formatos soportados: .xlsx, .xls, .csv (máx. 50MB)
                    </small>
                  </div>
                </Card.Body>
              </Card>

              {/* Selected File Info */}
              {selectedFile && (
                <Card className="mb-4">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <div>
                        <h6 className="mb-1">
                          <i className="bi bi-file-earmark-text me-2 text-success"></i>
                          {selectedFile.name}
                        </h6>
                        <small className="text-muted">
                          {formatFileSize(selectedFile.size)}
                        </small>
                      </div>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => {
                          setSelectedFile(null)
                          setTransformResult(null)
                          if (fileInputRef.current) {
                            fileInputRef.current.value = ''
                          }
                        }}
                        disabled={loading}
                      >
                        <i className="bi bi-x-lg"></i>
                      </Button>
                    </div>

                    {/* Template Selector */}
                    <Form.Group className="mb-3">
                      <Form.Label>Plantilla (opcional)</Form.Label>
                      <Form.Select
                        value={selectedTemplate}
                        onChange={(e) => setSelectedTemplate(e.target.value)}
                        disabled={loading}
                      >
                        <option value="">Sin plantilla</option>
                        {templates.map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.name} - {t.destination}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>

                    <Button
                      variant="primary"
                      onClick={handleTransform}
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          Transformando...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-shuffle me-2"></i>
                          Transformar (Vista Previa)
                        </>
                      )}
                    </Button>
                  </Card.Body>
                </Card>
              )}

              {/* Transform Result */}
              {transformResult && (
                <Card>
                  <Card.Header className="bg-success text-white">
                    <i className="bi bi-check-circle me-2"></i>
                    Vista Previa de Transformación
                  </Card.Header>
                  <Card.Body>
                    <Row className="mb-3">
                      <Col md={4}>
                        <div className="text-center">
                          <h4>{transformResult.total_rows}</h4>
                          <small className="text-muted">Filas totales</small>
                        </div>
                      </Col>
                      <Col md={4}>
                        <div className="text-center">
                          <h4>{transformResult.columns.length}</h4>
                          <small className="text-muted">Columnas</small>
                        </div>
                      </Col>
                      <Col md={4}>
                        <div className="text-center">
                          <h4>{transformResult.preview_rows}</h4>
                          <small className="text-muted">Vista previa</small>
                        </div>
                      </Col>
                    </Row>

                    {transformResult.template_applied && (
                      <Alert variant="info">
                        <small>
                          <i className="bi bi-info-circle me-2"></i>
                          Plantilla aplicada: <strong>{transformResult.template_applied}</strong>
                        </small>
                      </Alert>
                    )}

                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                      <Table striped bordered hover size="sm">
                        <thead>
                          <tr>
                            {transformResult.columns.map((col, idx) => (
                              <th key={idx}><small>{col}</small></th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {transformResult.preview.map((row, idx) => (
                            <tr key={idx}>
                              {transformResult.columns.map((col, cidx) => (
                                <td key={cidx}>
                                  <small>{String(row[col] || '')}</small>
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </div>
                  </Card.Body>
                </Card>
              )}
            </Col>

            {/* Sidebar - Info */}
            <Col lg={4}>
              <Card>
                <Card.Header className="bg-info text-white">
                  <i className="bi bi-info-circle me-2"></i>
                  Información
                </Card.Header>
                <Card.Body>
                  <h6>Transformación:</h6>
                  <p className="small">
                    La transformación te permite visualizar cómo se procesarán tus datos antes de importarlos.
                  </p>

                  <h6 className="mt-3">Plantillas:</h6>
                  <p className="small">
                    Las plantillas definen cómo mapear las columnas de tu archivo a los campos del sistema.
                  </p>

                  <Alert variant="warning" className="mt-3">
                    <small>
                      <i className="bi bi-exclamation-triangle me-2"></i>
                      Esta acción solo muestra una vista previa, no guarda los datos.
                    </small>
                  </Alert>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/* TAB: IMPORTAR */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <Tab eventKey="import" title={<span><i className="bi bi-upload me-2"></i>Importar</span>}>
          <Row>
            <Col lg={8}>
              {/* File Upload */}
              <Card
                className={`mb-4 ${isDragging ? 'border-primary bg-light' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                style={{ borderStyle: 'dashed', borderWidth: '2px' }}
              >
                <Card.Body className="text-center py-5">
                  <i className="bi bi-cloud-upload" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
                  <h5 className="mt-3">Arrastra tu archivo aquí</h5>
                  <p className="text-muted">o haz clic para seleccionar</p>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />

                  <Button
                    variant="outline-primary"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                  >
                    <i className="bi bi-folder2-open me-2"></i>
                    Seleccionar Archivo
                  </Button>
                </Card.Body>
              </Card>

              {/* Selected File + Import Options */}
              {selectedFile && (
                <Card className="mb-4">
                  <Card.Body>
                    <h6 className="mb-1">
                      <i className="bi bi-file-earmark-text me-2 text-success"></i>
                      {selectedFile.name}
                    </h6>
                    <small className="text-muted d-block mb-3">
                      {formatFileSize(selectedFile.size)}
                    </small>

                    <Form.Group className="mb-3">
                      <Form.Label>Destino *</Form.Label>
                      <Form.Select
                        value={selectedDestination}
                        onChange={(e) => setSelectedDestination(e.target.value)}
                        disabled={loading}
                      >
                        <option value="devices">Dispositivos</option>
                        <option value="inventory">Inventario</option>
                        <option value="customers">Clientes</option>
                        <option value="service_tickets">Tickets de Servicio</option>
                      </Form.Select>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Plantilla (opcional)</Form.Label>
                      <Form.Select
                        value={selectedTemplate}
                        onChange={(e) => setSelectedTemplate(e.target.value)}
                        disabled={loading}
                      >
                        <option value="">Sin plantilla</option>
                        {templates
                          .filter((t) => t.destination === selectedDestination)
                          .map((t) => (
                            <option key={t.id} value={t.id}>
                              {t.name}
                            </option>
                          ))}
                      </Form.Select>
                    </Form.Group>

                    <div className="d-flex gap-2">
                      <Button
                        variant="success"
                        onClick={handleImport}
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <Spinner animation="border" size="sm" className="me-2" />
                            Importando...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-upload me-2"></i>
                            Importar a Base de Datos
                          </>
                        )}
                      </Button>

                      <Button
                        variant="outline-danger"
                        onClick={() => {
                          setSelectedFile(null)
                          if (fileInputRef.current) {
                            fileInputRef.current.value = ''
                          }
                        }}
                        disabled={loading}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              )}
            </Col>

            {/* Sidebar */}
            <Col lg={4}>
              <Card>
                <Card.Header className="bg-warning text-dark">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  Advertencia
                </Card.Header>
                <Card.Body>
                  <p className="small">
                    Esta acción importará los datos directamente a la base de datos.
                  </p>
                  <p className="small mb-0">
                    <strong>Asegúrate de:</strong>
                  </p>
                  <ul className="small">
                    <li>Seleccionar el destino correcto</li>
                    <li>Usar la plantilla apropiada</li>
                    <li>Verificar los datos antes de importar</li>
                  </ul>
                </Card.Body>
              </Card>

              <Card className="mt-3">
                <Card.Header className="bg-info text-white">
                  <i className="bi bi-lightbulb me-2"></i>
                  Consejo
                </Card.Header>
                <Card.Body>
                  <p className="small mb-0">
                    Puedes usar la pestaña <strong>Transformar</strong> para ver una vista previa antes de importar.
                  </p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/* TAB: PLANTILLAS */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <Tab eventKey="templates" title={<span><i className="bi bi-file-text me-2"></i>Plantillas</span>}>
          <div className="d-flex justify-content-end mb-3">
            <Button variant="primary" onClick={() => setShowTemplateModal(true)}>
              <i className="bi bi-plus-circle me-2"></i>
              Nueva Plantilla
            </Button>
          </div>

          <Card>
            <Card.Body className="p-0">
              {loadingTemplates ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                </div>
              ) : templates.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                  <p className="text-muted mt-3">No hay plantillas configuradas</p>
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Nombre</th>
                      <th>Descripción</th>
                      <th>Destino</th>
                      <th>Formatos</th>
                      <th>Usos</th>
                      <th>Creado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {templates.map((template) => (
                      <tr key={template.id}>
                        <td><strong>{template.name}</strong></td>
                        <td><small>{template.description}</small></td>
                        <td><Badge bg="primary">{template.destination}</Badge></td>
                        <td>
                          {template.file_types.map((ft, idx) => (
                            <Badge key={idx} bg="secondary" className="me-1">{ft}</Badge>
                          ))}
                        </td>
                        <td>{template.usage_count}</td>
                        <td>
                          <small className="text-muted">
                            {new Date(template.created_at).toLocaleDateString()}
                          </small>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/* TAB: JOBS */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <Tab eventKey="jobs" title={<span><i className="bi bi-clock-history me-2"></i>Jobs</span>}>
          <Card>
            <Card.Body className="p-0">
              {loadingJobs ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                </div>
              ) : jobs.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                  <p className="text-muted mt-3">No hay jobs de importación</p>
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Job #</th>
                      <th>Archivo</th>
                      <th>Destino</th>
                      <th>Estado</th>
                      <th>Progreso</th>
                      <th>Filas</th>
                      <th>Éxito</th>
                      <th>Errores</th>
                      <th>Usuario</th>
                      <th>Fecha</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map((job) => (
                      <tr key={job.id}>
                        <td><Badge bg="secondary">{job.job_number}</Badge></td>
                        <td><small>{job.filename}</small></td>
                        <td><Badge bg="primary">{job.destination}</Badge></td>
                        <td>{getStatusBadge(job.status)}</td>
                        <td style={{ width: '150px' }}>
                          <ProgressBar now={job.progress} label={`${job.progress}%`} className="small" />
                        </td>
                        <td>{job.total_rows}</td>
                        <td>
                          <Badge bg="success">{job.successful_rows}</Badge>
                        </td>
                        <td>
                          {job.failed_rows > 0 ? (
                            <Badge bg="danger">{job.failed_rows}</Badge>
                          ) : (
                            <span className="text-muted">0</span>
                          )}
                        </td>
                        <td><small className="text-muted">{job.employee_name}</small></td>
                        <td>
                          <small className="text-muted">
                            {new Date(job.created_at).toLocaleString()}
                          </small>
                        </td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => loadJobDetail(job.id)}
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
        </Tab>
      </Tabs>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* MODAL: CREATE TEMPLATE */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <Modal show={showTemplateModal} onHide={() => setShowTemplateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Nueva Plantilla</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Nombre *</Form.Label>
              <Form.Control
                type="text"
                value={templateForm.name}
                onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                placeholder="Ej: Importación de Dispositivos GPS"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Descripción</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={templateForm.description}
                onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
                placeholder="Descripción opcional"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Destino *</Form.Label>
              <Form.Select
                value={templateForm.destination}
                onChange={(e) => setTemplateForm({ ...templateForm, destination: e.target.value })}
              >
                <option value="devices">Dispositivos</option>
                <option value="inventory">Inventario</option>
                <option value="customers">Clientes</option>
                <option value="service_tickets">Tickets de Servicio</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Mapeo (JSON) *</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={templateForm.mapping}
                onChange={(e) => setTemplateForm({ ...templateForm, mapping: e.target.value })}
                placeholder='{"columna_origen": "campo_destino"}'
                style={{ fontFamily: 'monospace', fontSize: '0.9em' }}
              />
              <Form.Text className="text-muted">
                Mapeo de columnas del archivo a campos del sistema
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Validación (JSON)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={templateForm.validation}
                onChange={(e) => setTemplateForm({ ...templateForm, validation: e.target.value })}
                placeholder='{}'
                style={{ fontFamily: 'monospace', fontSize: '0.9em' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Valores por Defecto (JSON)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={templateForm.default_values}
                onChange={(e) => setTemplateForm({ ...templateForm, default_values: e.target.value })}
                placeholder='{}'
                style={{ fontFamily: 'monospace', fontSize: '0.9em' }}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowTemplateModal(false)}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleCreateTemplate} disabled={loading}>
            {loading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Creando...
              </>
            ) : (
              'Crear Plantilla'
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* MODAL: JOB DETAIL */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <Modal show={showJobModal} onHide={() => setShowJobModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedJob?.job_number}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedJob && (
            <>
              <Row className="mb-4">
                <Col md={3}>
                  <Card className="text-center">
                    <Card.Body>
                      <h5 className="text-muted mb-1">Total</h5>
                      <h2>{selectedJob.total_rows}</h2>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center bg-success text-white">
                    <Card.Body>
                      <h5 className="mb-1">Éxito</h5>
                      <h2>{selectedJob.successful_rows}</h2>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center bg-danger text-white">
                    <Card.Body>
                      <h5 className="mb-1">Errores</h5>
                      <h2>{selectedJob.failed_rows}</h2>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center bg-warning text-dark">
                    <Card.Body>
                      <h5 className="mb-1">Omitidos</h5>
                      <h2>{selectedJob.skipped_rows}</h2>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              <div className="mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <strong>Tasa de éxito</strong>
                  <strong>{selectedJob.success_rate.toFixed(2)}%</strong>
                </div>
                <ProgressBar
                  now={selectedJob.success_rate}
                  variant={selectedJob.success_rate >= 80 ? 'success' : selectedJob.success_rate >= 50 ? 'warning' : 'danger'}
                />
              </div>

              {selectedJob.errors && selectedJob.errors.length > 0 && (
                <Card className="border-danger mb-3">
                  <Card.Header className="bg-danger text-white">
                    Errores
                  </Card.Header>
                  <Card.Body style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <Table size="sm">
                      <thead>
                        <tr>
                          <th>Fila</th>
                          <th>Campo</th>
                          <th>Mensaje</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedJob.errors.map((err, idx) => (
                          <tr key={idx}>
                            <td><Badge bg="secondary">{err.row}</Badge></td>
                            <td><code>{err.field}</code></td>
                            <td><small>{err.message}</small></td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              )}

              {selectedJob.preview_data && selectedJob.preview_data.length > 0 && (
                <Card>
                  <Card.Header>Vista Previa</Card.Header>
                  <Card.Body style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <pre style={{ fontSize: '0.8em' }}>
                      {JSON.stringify(selectedJob.preview_data, null, 2)}
                    </pre>
                  </Card.Body>
                </Card>
              )}

              <div className="text-muted text-center mt-3">
                <small>
                  Duración: {selectedJob.duration_seconds} segundos
                </small>
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowJobModal(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}
