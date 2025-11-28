/**
 * App 2: Data Import Page
 * Importación masiva de dispositivos desde Excel/CSV
 */

import { useState, useEffect, useRef } from 'react'
import {
  Container, Row, Col, Card, Button, Alert, Table,
  ProgressBar, Badge, Form, Modal, Tabs, Tab,
  Spinner
} from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import importTemplateService from '../../services/import-template.service'
import brandService, { Brand } from '../../services/brand.service'
import type { ImportTemplateListItem, ImportTemplate } from '../../types/import-template'
import IccidGeneratorTab from './IccidGeneratorTab'
import toast from 'react-hot-toast'

interface ImportSummary {
  total_rows: number
  success_count: number
  error_count: number
  duplicate_count: number
  success_rate: number
  processing_time_seconds: number
}

interface ImportResult {
  success: boolean
  message: string
  import_id: string
  summary: ImportSummary
  data_summary: any
  has_errors: boolean
  errors: any[]
  warnings: any[]
}

interface ImportHistory {
  id: string
  filename: string
  file_type: string
  status: string
  total_rows: number
  success_count: number
  error_count: number
  duplicate_count: number
  success_rate: number
  processing_time_seconds: number
  imported_by: string
  created_at: string
  completed_at: string
}

export default function DataImportPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [history, setHistory] = useState<ImportHistory[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [showResultModal, setShowResultModal] = useState(false)
  const [activeTab, setActiveTab] = useState<string>('upload')

  // Template management state
  const [templates, setTemplates] = useState<ImportTemplateListItem[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [loadingTemplates, setLoadingTemplates] = useState(false)
  const [creatingTemplate, setCreatingTemplate] = useState(false)
  const [selectedTemplateDetails, setSelectedTemplateDetails] = useState<ImportTemplate | null>(null)
  const [showTemplateModal, setShowTemplateModal] = useState(false)

  // Brand selector state
  const [selectedBrand, setSelectedBrand] = useState<string>('')
  const [brands, setBrands] = useState<Brand[]>([])
  const [loadingBrands, setLoadingBrands] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadHistory()
    loadTemplates()
    loadBrands()
  }, [])

  const loadHistory = async () => {
    setLoadingHistory(true)
    try {
      const response = await apiService.get('/api/app2/history?limit=10')
      setHistory(response.imports || [])
    } catch (err: any) {
      console.error('Error cargando historial:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  const loadTemplates = async () => {
    setLoadingTemplates(true)
    try {
      const templateList = await importTemplateService.getTemplates()
      setTemplates(templateList)
    } catch (err: any) {
      console.error('Error cargando plantillas:', err)
      toast.error('Error al cargar las plantillas')
    } finally {
      setLoadingTemplates(false)
    }
  }

  const loadBrands = async () => {
    setLoadingBrands(true)
    try {
      const response = await brandService.getBrands(true) // Only active brands
      if (response.success && response.brands) {
        setBrands(response.brands)
      }
    } catch (err: any) {
      console.error('Error cargando marcas:', err)
    } finally {
      setLoadingBrands(false)
    }
  }

  const handleCreateNeowayTemplate = async () => {
    setCreatingTemplate(true)
    try {
      const response = await importTemplateService.createNeowayTemplate()
      toast.success(response.message || 'Plantilla NEOWAY creada exitosamente')
      await loadTemplates()
    } catch (err: any) {
      console.error('Error creando plantilla NEOWAY:', err)
      toast.error('Error al crear la plantilla NEOWAY')
    } finally {
      setCreatingTemplate(false)
    }
  }

  const handleViewTemplate = async (templateId: string) => {
    try {
      const template = await importTemplateService.getTemplateById(templateId)
      setSelectedTemplateDetails(template)
      setShowTemplateModal(true)
    } catch (err: any) {
      console.error('Error cargando detalles de plantilla:', err)
      toast.error('Error al cargar los detalles de la plantilla')
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
      setError(null)
      setImportResult(null)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)

    const files = event.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]

      // Validar tipo de archivo
      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
        setSelectedFile(file)
        setError(null)
        setImportResult(null)
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

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Por favor seleccione un archivo')
      return
    }

    setUploading(true)
    setUploadProgress(0)
    setError(null)
    setImportResult(null)

    try {
      // Simular progreso
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      let response

      // Upload with template if selected
      if (selectedTemplate) {
        response = await importTemplateService.uploadWithTemplate(selectedFile, selectedTemplate, selectedBrand)
      } else {
        // Use default upload endpoint
        const formData = new FormData()
        formData.append('file', selectedFile)

        // Add brand parameter if selected
        if (selectedBrand) {
          formData.append('brand', selectedBrand)
        }

        response = await apiService.upload('/api/app2/upload', formData)
      }

      clearInterval(progressInterval)
      setUploadProgress(100)

      setImportResult(response)
      setShowResultModal(true)

      // Recargar historial
      await loadHistory()

      // Limpiar archivo seleccionado, plantilla y marca
      setSelectedFile(null)
      setSelectedTemplate('')
      setSelectedBrand('')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al importar el archivo')
    } finally {
      setUploading(false)
      setTimeout(() => setUploadProgress(0), 2000)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      processing: 'primary',
      completed: 'success',
      completed_with_errors: 'warning',
      failed: 'danger'
    }
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / 1048576).toFixed(2) + ' MB'
  }

  return (
    <Container fluid className="p-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-1">
            <i className="bi bi-file-earmark-arrow-down-fill me-2 text-success"></i>
            App 2: Importación de Datos
          </h4>
          <p className="text-muted mb-0">
            Carga masiva de dispositivos desde archivos Excel o CSV
          </p>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k || 'upload')}
        className="mb-4"
      >
        {/* Tab: Cargar Archivo */}
        <Tab eventKey="upload" title={<span><i className="bi bi-upload me-2"></i>Cargar Archivo</span>}>
          <Row>
            <Col lg={8}>
              {/* Template Selector */}
              <Card className="mb-4">
                <Card.Body>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      <i className="bi bi-file-earmark-ruled me-2"></i>
                      Plantilla de Importación (Opcional)
                    </Form.Label>
                    <Form.Select
                      value={selectedTemplate}
                      onChange={(e) => setSelectedTemplate(e.target.value)}
                      disabled={uploading}
                    >
                      <option value="">Sin plantilla (mapeo automático)</option>
                      {templates.map(template => (
                        <option key={template.id} value={template.id}>
                          {template.name} - {template.destination}
                        </option>
                      ))}
                    </Form.Select>
                    {selectedTemplate && (
                      <Form.Text className="text-muted">
                        La plantilla aplicará mapeo de columnas y validaciones personalizadas
                      </Form.Text>
                    )}
                  </Form.Group>

                  <Form.Group>
                    <Form.Label>
                      <i className="bi bi-tag me-2"></i>
                      Marca del Dispositivo (Opcional)
                    </Form.Label>
                    <Form.Select
                      value={selectedBrand}
                      onChange={(e) => setSelectedBrand(e.target.value)}
                      disabled={uploading || loadingBrands}
                    >
                      <option value="">Usar marca del archivo o plantilla</option>
                      {brands.map((brand) => (
                        <option key={brand.id} value={brand.name}>
                          {brand.name}
                        </option>
                      ))}
                    </Form.Select>
                    <Form.Text className="text-muted">
                      Si se especifica, esta marca se aplicará a todos los dispositivos del archivo
                    </Form.Text>
                  </Form.Group>
                </Card.Body>
              </Card>

              {/* Drag & Drop Zone */}
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
                    disabled={uploading}
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
                    <div className="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 className="mb-1">
                          <i className="bi bi-file-earmark-text me-2 text-success"></i>
                          {selectedFile.name}
                        </h6>
                        <small className="text-muted">
                          {formatFileSize(selectedFile.size)}
                        </small>
                      </div>
                      <div>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => {
                            setSelectedFile(null)
                            if (fileInputRef.current) {
                              fileInputRef.current.value = ''
                            }
                          }}
                          disabled={uploading}
                        >
                          <i className="bi bi-x-lg"></i>
                        </Button>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Upload Progress */}
              {uploading && (
                <Card className="mb-4">
                  <Card.Body>
                    <div className="d-flex align-items-center mb-2">
                      <Spinner animation="border" size="sm" className="me-2" />
                      <span>Procesando importación...</span>
                    </div>
                    <ProgressBar now={uploadProgress} label={`${uploadProgress}%`} animated />
                  </Card.Body>
                </Card>
              )}

              {/* Upload Button */}
              {selectedFile && !uploading && (
                <div className="text-end">
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={handleUpload}
                    disabled={!selectedFile}
                  >
                    <i className="bi bi-upload me-2"></i>
                    Iniciar Importación
                  </Button>
                </div>
              )}
            </Col>

            {/* Instrucciones */}
            <Col lg={4}>
              <Card>
                <Card.Header className="bg-info text-white">
                  <i className="bi bi-info-circle me-2"></i>
                  Instrucciones
                </Card.Header>
                <Card.Body>
                  <h6>Campos requeridos:</h6>
                  <ul className="small">
                    <li><strong>imei</strong> o <strong>imei_1</strong>: 15 dígitos</li>
                    <li><strong>iccid</strong> o <strong>ccid</strong>: 19-22 dígitos</li>
                  </ul>

                  <h6 className="mt-3">Campos opcionales:</h6>
                  <ul className="small">
                    <li>imei_2 (validación)</li>
                    <li>package_no</li>
                    <li>orden_produccion</li>
                    <li>lote</li>
                    <li>codigo_innerbox</li>
                    <li>codigo_unitario</li>
                    <li>num_palet</li>
                    <li>marca</li>
                    <li>cliente</li>
                    <li>num_deposito</li>
                    <li>ubicacion_actual</li>
                  </ul>

                  <Alert variant="warning" className="mt-3">
                    <small>
                      <i className="bi bi-exclamation-triangle me-2"></i>
                      Los IMEIs duplicados serán rechazados
                    </small>
                  </Alert>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        {/* Tab: Plantillas */}
        <Tab eventKey="templates" title={<span><i className="bi bi-file-earmark-ruled me-2"></i>Plantillas</span>}>
          <Card className="mb-4">
            <Card.Header className="bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <span>
                  <i className="bi bi-file-earmark-ruled me-2"></i>
                  Plantillas de Importación
                </span>
                <Button
                  variant="light"
                  size="sm"
                  onClick={handleCreateNeowayTemplate}
                  disabled={creatingTemplate || templates.some(t => t.name === 'NEOWAY_PRODUCCION_IMPORT')}
                >
                  {creatingTemplate ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Creando...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-plus-circle me-1"></i>
                      Crear Plantilla NEOWAY
                    </>
                  )}
                </Button>
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              {loadingTemplates ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                  <p className="text-muted mt-3">Cargando plantillas...</p>
                </div>
              ) : templates.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                  <p className="text-muted mt-3 mb-2">No hay plantillas configuradas</p>
                  <p className="text-muted small">Crea la plantilla NEOWAY para empezar</p>
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Nombre</th>
                      <th>Descripción</th>
                      <th>Destino</th>
                      <th>Usos</th>
                      <th>Último Uso</th>
                      <th>Creada</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {templates.map((template) => (
                      <tr key={template.id}>
                        <td>
                          <strong>{template.name}</strong>
                        </td>
                        <td>
                          <small className="text-muted">{template.description || '-'}</small>
                        </td>
                        <td>
                          <Badge bg="info">{template.destination}</Badge>
                        </td>
                        <td>
                          <Badge bg="secondary">{template.usage_count}</Badge>
                        </td>
                        <td>
                          <small className="text-muted">
                            {template.last_used_at
                              ? new Date(template.last_used_at).toLocaleDateString()
                              : 'Nunca'}
                          </small>
                        </td>
                        <td>
                          <small className="text-muted">
                            {new Date(template.created_at).toLocaleDateString()}
                          </small>
                        </td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleViewTemplate(template.id)}
                          >
                            <i className="bi bi-eye me-1"></i>
                            Ver Detalles
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>

          {/* Info Card */}
          <Card className="border-info">
            <Card.Header className="bg-info text-white">
              <i className="bi bi-info-circle me-2"></i>
              Información sobre Plantillas
            </Card.Header>
            <Card.Body>
              <h6>¿Qué son las plantillas de importación?</h6>
              <p className="small text-muted mb-3">
                Las plantillas permiten configurar cómo se deben mapear las columnas de tus archivos Excel/CSV
                a los campos de la base de datos. También pueden incluir validaciones personalizadas y valores
                por defecto.
              </p>

              <h6>Plantilla NEOWAY_PRODUCCION_IMPORT</h6>
              <p className="small text-muted mb-2">
                Esta plantilla está diseñada específicamente para importar datos de producción Neoway con los
                siguientes campos:
              </p>
              <ul className="small text-muted">
                <li><strong>imei</strong>: Número IMEI del dispositivo (15 dígitos, requerido)</li>
                <li><strong>iccid</strong>: Número ICCID de la SIM (19-22 caracteres)</li>
                <li><strong>package_no</strong>: Número de paquete o cartón</li>
                <li><strong>work_order_id</strong>: ID de orden de producción</li>
                <li><strong>info5</strong>: Información adicional</li>
              </ul>
              <p className="small text-muted">
                <strong>Valores por defecto:</strong> marca=NEOWAY, estado=APROBADO
              </p>
            </Card.Body>
          </Card>
        </Tab>

        {/* Tab: Historial */}
        <Tab eventKey="history" title={<span><i className="bi bi-clock-history me-2"></i>Historial</span>}>
          <Card>
            <Card.Body className="p-0">
              {loadingHistory ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                </div>
              ) : history.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                  <p className="text-muted mt-3">No hay importaciones previas</p>
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Archivo</th>
                      <th>Estado</th>
                      <th>Total</th>
                      <th>Éxito</th>
                      <th>Errores</th>
                      <th>Duplicados</th>
                      <th>% Éxito</th>
                      <th>Tiempo</th>
                      <th>Importado por</th>
                      <th>Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <i className={`bi bi-file-earmark-${item.file_type === 'csv' ? 'text' : 'spreadsheet'} me-2`}></i>
                          {item.filename}
                        </td>
                        <td>{getStatusBadge(item.status)}</td>
                        <td>{item.total_rows}</td>
                        <td>
                          <Badge bg="success">{item.success_count}</Badge>
                        </td>
                        <td>
                          {item.error_count > 0 ? (
                            <Badge bg="danger">{item.error_count}</Badge>
                          ) : (
                            <span className="text-muted">0</span>
                          )}
                        </td>
                        <td>
                          {item.duplicate_count > 0 ? (
                            <Badge bg="warning">{item.duplicate_count}</Badge>
                          ) : (
                            <span className="text-muted">0</span>
                          )}
                        </td>
                        <td>
                          <strong className={item.success_rate >= 80 ? 'text-success' : item.success_rate >= 50 ? 'text-warning' : 'text-danger'}>
                            {item.success_rate.toFixed(0)}%
                          </strong>
                        </td>
                        <td>
                          <small className="text-muted">
                            {item.processing_time_seconds ? `${item.processing_time_seconds.toFixed(1)}s` : '-'}
                          </small>
                        </td>
                        <td>
                          <small className="text-muted">{item.imported_by}</small>
                        </td>
                        <td>
                          <small className="text-muted">
                            {new Date(item.created_at).toLocaleString()}
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

        {/* Tab: Generar ICCID */}
        <Tab eventKey="generate" title={<span><i className="bi bi-calculator me-2"></i>Generar ICCID</span>}>
          <IccidGeneratorTab />
        </Tab>
      </Tabs>

      {/* Result Modal */}
      <Modal show={showResultModal} onHide={() => setShowResultModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {importResult?.has_errors ? (
              <span className="text-warning">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                Importación completada con errores
              </span>
            ) : (
              <span className="text-success">
                <i className="bi bi-check-circle-fill me-2"></i>
                Importación exitosa
              </span>
            )}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {importResult && (
            <>
              {/* Resumen */}
              <Row className="mb-4">
                <Col md={3}>
                  <Card className="text-center">
                    <Card.Body>
                      <h5 className="text-muted mb-1">Total</h5>
                      <h2>{importResult.summary.total_rows}</h2>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center bg-success text-white">
                    <Card.Body>
                      <h5 className="mb-1">Éxito</h5>
                      <h2>{importResult.summary.success_count}</h2>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center bg-danger text-white">
                    <Card.Body>
                      <h5 className="mb-1">Errores</h5>
                      <h2>{importResult.summary.error_count}</h2>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center bg-warning text-dark">
                    <Card.Body>
                      <h5 className="mb-1">Duplicados</h5>
                      <h2>{importResult.summary.duplicate_count}</h2>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Tasa de éxito */}
              <div className="mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <strong>Tasa de éxito</strong>
                  <strong>{importResult.summary.success_rate.toFixed(2)}%</strong>
                </div>
                <ProgressBar
                  now={importResult.summary.success_rate}
                  variant={importResult.summary.success_rate >= 80 ? 'success' : importResult.summary.success_rate >= 50 ? 'warning' : 'danger'}
                />
              </div>

              {/* Resumen de datos */}
              {importResult.data_summary && (
                <Card className="mb-3">
                  <Card.Header>Resumen de Datos Importados</Card.Header>
                  <Card.Body>
                    <Row>
                      {importResult.data_summary.ordenes_unicas > 0 && (
                        <Col md={6}>
                          <strong>Órdenes de producción:</strong> {importResult.data_summary.ordenes_unicas}
                        </Col>
                      )}
                      {importResult.data_summary.lotes_unicos > 0 && (
                        <Col md={6}>
                          <strong>Lotes:</strong> {importResult.data_summary.lotes_unicos}
                        </Col>
                      )}
                      {importResult.data_summary.marcas_unicas > 0 && (
                        <Col md={6}>
                          <strong>Marcas:</strong> {importResult.data_summary.marcas_unicas}
                        </Col>
                      )}
                      {importResult.data_summary.clientes_unicos > 0 && (
                        <Col md={6}>
                          <strong>Clientes:</strong> {importResult.data_summary.clientes_unicos}
                        </Col>
                      )}
                      {importResult.data_summary.packages_unicos > 0 && (
                        <Col md={6}>
                          <strong>Paquetes:</strong> {importResult.data_summary.packages_unicos}
                        </Col>
                      )}
                    </Row>
                  </Card.Body>
                </Card>
              )}

              {/* Errores */}
              {importResult.has_errors && importResult.errors.length > 0 && (
                <Card className="border-danger">
                  <Card.Header className="bg-danger text-white">
                    Errores Encontrados (Primeros 50)
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
                        {importResult.errors.map((err, idx) => (
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

              {/* Advertencias */}
              {importResult.warnings && importResult.warnings.length > 0 && (
                <Card className="border-warning mt-3">
                  <Card.Header className="bg-warning text-dark">
                    Advertencias
                  </Card.Header>
                  <Card.Body style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    <Table size="sm">
                      <thead>
                        <tr>
                          <th>Fila</th>
                          <th>Campo</th>
                          <th>Mensaje</th>
                        </tr>
                      </thead>
                      <tbody>
                        {importResult.warnings.map((warn, idx) => (
                          <tr key={idx}>
                            <td><Badge bg="secondary">{warn.row}</Badge></td>
                            <td><code>{warn.field}</code></td>
                            <td><small>{warn.message}</small></td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              )}

              <div className="text-muted text-center mt-3">
                <small>
                  Tiempo de procesamiento: {importResult.summary.processing_time_seconds.toFixed(2)} segundos
                </small>
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowResultModal(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Template Details Modal */}
      <Modal show={showTemplateModal} onHide={() => setShowTemplateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-file-earmark-ruled me-2"></i>
            Detalles de la Plantilla
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTemplateDetails && (
            <>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Nombre:</strong>
                  <p>{selectedTemplateDetails.name}</p>
                </Col>
                <Col md={6}>
                  <strong>Destino:</strong>
                  <p><Badge bg="info">{selectedTemplateDetails.destination}</Badge></p>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col>
                  <strong>Descripción:</strong>
                  <p className="text-muted">{selectedTemplateDetails.description || '-'}</p>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <strong>Formatos Soportados:</strong>
                  <p>{selectedTemplateDetails.file_types.join(', ')}</p>
                </Col>
                <Col md={6}>
                  <strong>Encoding:</strong>
                  <p>{selectedTemplateDetails.encoding}</p>
                </Col>
              </Row>

              <hr />

              <h6>Mapeo de Columnas</h6>
              <Table size="sm" bordered className="mb-3">
                <thead className="table-light">
                  <tr>
                    <th>Columna en Excel/CSV</th>
                    <th>Campo en Base de Datos</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(selectedTemplateDetails.mapping).map(([excelCol, dbField]) => (
                    <tr key={excelCol}>
                      <td><code>{excelCol}</code></td>
                      <td><code>{dbField}</code></td>
                    </tr>
                  ))}
                </tbody>
              </Table>

              {selectedTemplateDetails.required_fields && selectedTemplateDetails.required_fields.length > 0 && (
                <>
                  <h6>Campos Requeridos</h6>
                  <div className="mb-3">
                    {selectedTemplateDetails.required_fields.map(field => (
                      <Badge key={field} bg="danger" className="me-2 mb-2">
                        {field}
                      </Badge>
                    ))}
                  </div>
                </>
              )}

              {selectedTemplateDetails.default_values && Object.keys(selectedTemplateDetails.default_values).length > 0 && (
                <>
                  <h6>Valores por Defecto</h6>
                  <Table size="sm" bordered className="mb-3">
                    <thead className="table-light">
                      <tr>
                        <th>Campo</th>
                        <th>Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(selectedTemplateDetails.default_values).map(([field, value]) => (
                        <tr key={field}>
                          <td><code>{field}</code></td>
                          <td><Badge bg="success">{String(value)}</Badge></td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </>
              )}

              <Row className="mt-3">
                <Col md={4}>
                  <small className="text-muted">
                    <strong>Veces usado:</strong> {selectedTemplateDetails.usage_count}
                  </small>
                </Col>
                <Col md={4}>
                  <small className="text-muted">
                    <strong>Última uso:</strong>{' '}
                    {selectedTemplateDetails.last_used_at
                      ? new Date(selectedTemplateDetails.last_used_at).toLocaleString()
                      : 'Nunca'}
                  </small>
                </Col>
                <Col md={4}>
                  <small className="text-muted">
                    <strong>Creada:</strong>{' '}
                    {new Date(selectedTemplateDetails.created_at).toLocaleString()}
                  </small>
                </Col>
              </Row>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowTemplateModal(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}
