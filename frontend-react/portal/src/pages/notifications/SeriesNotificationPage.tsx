/**
 * OSE Platform - Series Notification Page
 * Notify device series (IMEI/ICCID) to clients
 * Based on specifications from "App1 Notificación Series.md"
 */

import { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Nav, Tab, Button, Form, Alert, Table, Badge, Spinner, Modal } from 'react-bootstrap'
import toast from 'react-hot-toast'
import seriesNotificationService from '../../services/series-notification.service'
import type {
  DeviceSerial,
  Customer,
  CSVFormat,
  ValidationResult,
  BulkValidationResult,
  SeriesNotificationRequest,
  NotificationHistoryItem,
} from '../../types/series-notification'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function SeriesNotificationPage() {
  // State for Step 1: Input
  const [inputText, setInputText] = useState('')
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [parsedSerials, setParsedSerials] = useState<DeviceSerial[]>([])
  const [parseErrors, setParseErrors] = useState<{ input: string; error: string }[]>([])

  // State for Smart Scan
  const [scanCode, setScanCode] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [scanResult, setScanResult] = useState<{ type: string; count: number; message: string } | null>(null)

  // State for Step 2: Validation
  const [validationResult, setValidationResult] = useState<BulkValidationResult | null>(null)
  const [isValidating, setIsValidating] = useState(false)
  const [validatedSerials, setValidatedSerials] = useState<DeviceSerial[]>([])

  // State for Step 3: Configuration
  const [customers, setCustomers] = useState<Customer[]>([])
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [location, setLocation] = useState('')
  const [csvFormat, setCsvFormat] = useState<CSVFormat>('separated')
  const [emailTo, setEmailTo] = useState('')
  const [emailCC, setEmailCC] = useState('')
  const [notes, setNotes] = useState('')

  // State for Step 4: Send
  const [isSending, setIsSending] = useState(false)
  const [csvPreview, setCsvPreview] = useState('')

  // State for History Tab
  const [history, setHistory] = useState<NotificationHistoryItem[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [showHistoryDetail, setShowHistoryDetail] = useState(false)
  const [selectedHistory, setSelectedHistory] = useState<NotificationHistoryItem | null>(null)

  // Current tab
  const [activeTab, setActiveTab] = useState<string>('input')

  // Load customers on mount
  useEffect(() => {
    // TODO: Descomentar cuando haya clientes en la BD
    // loadCustomers()
  }, [])

  const loadCustomers = async () => {
    // TODO: Descomentar cuando haya clientes en la BD
    // const data = await seriesNotificationService.getCustomers()
    // setCustomers(data)
  }

  const loadHistory = async () => {
    setHistoryLoading(true)
    try {
      const data = await seriesNotificationService.getHistory()
      setHistory(data.items)
    } catch (error) {
      toast.error('Error al cargar historial')
    } finally {
      setHistoryLoading(false)
    }
  }

  // Handle manual input parse
  const handleParseInput = () => {
    if (!inputText.trim()) {
      toast.error('Introduce al menos un número de serie')
      return
    }

    const result = seriesNotificationService.parseInput(inputText)
    setParsedSerials(result.valid)
    setParseErrors(result.invalid)

    if (result.valid.length > 0) {
      toast.success(`${result.valid.length} serie(s) parseada(s) correctamente`)
      setActiveTab('validate')
    }

    if (result.invalid.length > 0) {
      toast.error(`${result.invalid.length} línea(s) con errores`)
    }
  }

  // Handle CSV file upload
  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setCsvFile(file)

    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result as string
      const result = seriesNotificationService.parseCSV(content)
      setParsedSerials(result.valid)
      setParseErrors(result.invalid)

      if (result.valid.length > 0) {
        toast.success(`${result.valid.length} serie(s) cargada(s) desde CSV`)
        setActiveTab('validate')
      }
    }
    reader.readAsText(file)
  }

  // Handle smart scan (Lote/Cartón/Pallet)
  const handleSmartScan = async () => {
    if (!scanCode.trim()) {
      toast.error('Introduce un código para escanear')
      return
    }

    setIsScanning(true)
    setScanResult(null)

    try {
      const result = await seriesNotificationService.smartScan(scanCode.trim())

      if (result.success && result.serials.length > 0) {
        // Añadir los dispositivos encontrados a la lista
        const newSerials = result.serials.map(s => ({
          imei: s.imei || '',
          iccid: s.iccid || '',
          package_no: s.package_no || ''
        }))

        setParsedSerials(prev => [...prev, ...newSerials])

        setScanResult({
          type: result.type,
          count: result.count,
          message: result.message
        })

        toast.success(result.message)

        // Limpiar el campo de escaneo
        setScanCode('')

        // Si hay resultados, pasar a validar
        if (newSerials.length > 0) {
          setActiveTab('validate')
        }
      } else {
        toast.error(result.message || 'No se encontraron dispositivos')
        setScanResult({
          type: 'error',
          count: 0,
          message: result.message || 'No se encontraron dispositivos'
        })
      }
    } catch (error) {
      console.error('Error en smart scan:', error)
      toast.error('Error al buscar dispositivos')
      setScanResult({
        type: 'error',
        count: 0,
        message: 'Error al buscar dispositivos'
      })
    } finally {
      setIsScanning(false)
    }
  }

  // Handle validation
  const handleValidate = async () => {
    if (parsedSerials.length === 0) {
      toast.error('No hay series para validar')
      return
    }

    setIsValidating(true)
    try {
      const result = await seriesNotificationService.validateBulk(parsedSerials)
      setValidationResult(result)

      const valid = result.results.filter(r => r.valid).map(r => r.serial)
      setValidatedSerials(valid)

      if (result.valid > 0) {
        toast.success(`${result.valid} dispositivo(s) válido(s)`)
        setActiveTab('config')
      } else {
        toast.error('No hay dispositivos válidos para notificar')
      }
    } catch (error) {
      toast.error('Error al validar dispositivos')
    } finally {
      setIsValidating(false)
    }
  }

  // Handle customer selection
  const handleCustomerSelect = (customerId: string) => {
    const customer = customers.find(c => c.id === customerId)
    setSelectedCustomer(customer || null)
    if (customer) {
      setEmailTo(customer.email)
    }
  }

  // Handle CSV preview
  const handlePreview = () => {
    if (!location.trim()) {
      toast.error('Introduce el número de LOTE o Albarán')
      return
    }

    if (!emailTo.trim()) {
      toast.error('Introduce el email destinatario')
      return
    }

    const preview = seriesNotificationService.generateCSV(validatedSerials, csvFormat)
    setCsvPreview(preview)
    setActiveTab('preview')
  }

  // Handle send notification
  const handleSend = async () => {
    if (!emailTo || validatedSerials.length === 0 || !location.trim()) {
      toast.error('Completa todos los campos requeridos (Email y Número de LOTE/Albarán)')
      return
    }

    const request: SeriesNotificationRequest = {
      serials: validatedSerials,
      customer_id: selectedCustomer?.id,
      customer_name: selectedCustomer?.name || 'Sin cliente',
      location: location.trim(),
      csv_format: csvFormat,
      email_to: emailTo,
      email_cc: emailCC ? emailCC.split(',').map(e => e.trim()) : undefined,
      notes: notes.trim() || undefined,
    }

    setIsSending(true)
    try {
      const response = await seriesNotificationService.sendNotification(request)

      if (response.success) {
        toast.success(`✅ Notificación enviada: ${response.notified_count} dispositivos`)

        // Download CSV
        seriesNotificationService.downloadCSV(response.csv_content, response.csv_filename)

        // Reset form
        handleReset()

        // Switch to history tab
        setActiveTab('history')
        loadHistory()
      } else {
        toast.error('Error al enviar notificación')
      }
    } catch (error) {
      toast.error('Error al enviar notificación')
    } finally {
      setIsSending(false)
    }
  }

  // Reset form
  const handleReset = () => {
    setInputText('')
    setCsvFile(null)
    setParsedSerials([])
    setParseErrors([])
    setValidationResult(null)
    setValidatedSerials([])
    setSelectedCustomer(null)
    setLocation('')
    setEmailTo('')
    setEmailCC('')
    setNotes('')
    setCsvPreview('')
    setActiveTab('input')
  }

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">
                <i className="bi bi-send-check-fill me-2 text-primary"></i>
                Notificación de Números de Serie
              </h2>
              <p className="text-muted mb-0">Notificar IMEI/ICCID de dispositivos a clientes</p>
            </div>
            <Button variant="outline-secondary" onClick={handleReset}>
              <i className="bi bi-arrow-clockwise me-1"></i>
              Reiniciar
            </Button>
          </div>
        </Col>
      </Row>

      {/* Main Tabs */}
      <Tab.Container activeKey={activeTab} onSelect={(k) => k && setActiveTab(k)}>
        <Card className="border-0 shadow-sm">
          <Card.Header className="bg-white">
            <Nav variant="tabs" className="border-0">
              <Nav.Item>
                <Nav.Link eventKey="input">
                  <i className="bi bi-input-cursor me-2"></i>
                  1. Entrada
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="validate" disabled={parsedSerials.length === 0}>
                  <i className="bi bi-check2-square me-2"></i>
                  2. Validar
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="config" disabled={validatedSerials.length === 0}>
                  <i className="bi bi-gear me-2"></i>
                  3. Configurar
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="preview" disabled={!csvPreview}>
                  <i className="bi bi-eye me-2"></i>
                  4. Previsualizar
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="history">
                  <i className="bi bi-clock-history me-2"></i>
                  Historial
                </Nav.Link>
              </Nav.Item>
            </Nav>
          </Card.Header>

          <Card.Body className="p-4">
            <Tab.Content>
              {/* TAB 1: INPUT */}
              <Tab.Pane eventKey="input">
                <h4 className="mb-3">Introducir Números de Serie</h4>
                <p className="text-muted">
                  Introduce IMEI, ICCID, o números de paquete (package_no). Un número por línea o separados por espacios.
                </p>

                <Form.Group className="mb-4">
                  <Form.Label>Entrada Manual</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={10}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={`Ejemplos válidos:\n861888082667623\n89882390001210884632\n861888082667623 89882390001210884632\n9912182508200007739500205`}
                    style={{ fontFamily: 'monospace' }}
                  />
                  <Form.Text className="text-muted">
                    Formatos: IMEI (15 dígitos), ICCID (19-20 dígitos), Package No (25 dígitos empezando con 99)
                  </Form.Text>
                </Form.Group>

                <div className="d-flex gap-2 mb-4">
                  <Button variant="primary" onClick={handleParseInput} disabled={!inputText.trim()}>
                    <i className="bi bi-arrow-right-circle me-1"></i>
                    Parsear y Continuar
                  </Button>
                  <Button variant="outline-secondary" onClick={() => setInputText('')}>
                    <i className="bi bi-x-circle me-1"></i>
                    Limpiar
                  </Button>
                </div>

                <hr className="my-4" />

                {/* Scan by Lote/Cartón/Pallet */}
                <h5 className="mb-3">
                  <i className="bi bi-qr-code-scan me-2"></i>
                  Búsqueda por Código
                </h5>
                <p className="text-muted">
                  Escanea o introduce un código de Lote, Cartón, Pallet, IMEI o ICCID para cargar automáticamente los dispositivos.
                </p>

                <Form.Group className="mb-3">
                  <Form.Label>Código a Escanear</Form.Label>
                  <div className="d-flex gap-2">
                    <Form.Control
                      type="text"
                      value={scanCode}
                      onChange={(e) => setScanCode(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && scanCode.trim()) {
                          handleSmartScan()
                        }
                      }}
                      placeholder="Introduce o escanea: Lote, Cartón, Pallet, IMEI, ICCID..."
                      disabled={isScanning}
                      style={{ fontFamily: 'monospace' }}
                    />
                    <Button
                      variant="success"
                      onClick={handleSmartScan}
                      disabled={!scanCode.trim() || isScanning}
                      style={{ minWidth: '120px' }}
                    >
                      {isScanning ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          Buscando...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-search me-1"></i>
                          Buscar
                        </>
                      )}
                    </Button>
                  </div>
                  <Form.Text className="text-muted">
                    Detecta automáticamente el tipo de código y busca los dispositivos relacionados
                  </Form.Text>
                </Form.Group>

                {scanResult && (
                  <Alert variant="info" className="mb-4">
                    <div className="d-flex align-items-center">
                      <i className="bi bi-info-circle-fill me-2"></i>
                      <div>
                        <strong>Resultado del escaneo:</strong>
                        <div className="mt-1">{scanResult.message}</div>
                        <div className="small text-muted mt-1">
                          Tipo: <strong>{scanResult.type}</strong> | Dispositivos encontrados: <strong>{scanResult.count}</strong>
                        </div>
                      </div>
                    </div>
                  </Alert>
                )}

                <hr className="my-4" />

                <Form.Group>
                  <Form.Label>O Cargar desde CSV</Form.Label>
                  <Form.Control type="file" accept=".csv,.txt" onChange={handleCSVUpload} />
                  <Form.Text className="text-muted">
                    El archivo puede contener una columna con IMEI, ICCID o ambos separados por espacio
                  </Form.Text>
                </Form.Group>

                {parsedSerials.length > 0 && (
                  <Alert variant="success" className="mt-4">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    <strong>{parsedSerials.length}</strong> serie(s) parseada(s) correctamente
                  </Alert>
                )}

                {parseErrors.length > 0 && (
                  <Alert variant="danger" className="mt-4">
                    <h6>
                      <i className="bi bi-exclamation-triangle-fill me-2"></i>
                      Errores encontrados ({parseErrors.length})
                    </h6>
                    <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                      {parseErrors.map((err, idx) => (
                        <div key={idx} className="small mt-2">
                          <code>{err.input}</code> - {err.error}
                        </div>
                      ))}
                    </div>
                  </Alert>
                )}
              </Tab.Pane>

              {/* TAB 2: VALIDATE */}
              <Tab.Pane eventKey="validate">
                <h4 className="mb-3">Validar Dispositivos</h4>
                <p className="text-muted">
                  Verificando que los dispositivos existan en la base de datos y no hayan sido notificados previamente.
                </p>

                <div className="mb-4">
                  <Button variant="primary" onClick={handleValidate} disabled={isValidating || parsedSerials.length === 0}>
                    {isValidating ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Validando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-shield-check me-1"></i>
                        Validar {parsedSerials.length} Dispositivo(s)
                      </>
                    )}
                  </Button>
                </div>

                {validationResult && (
                  <>
                    <Row className="g-3 mb-4">
                      <Col md={3}>
                        <Card className="border-primary">
                          <Card.Body className="text-center">
                            <h3 className="mb-1 text-primary">{validationResult.total}</h3>
                            <div className="small text-muted text-uppercase">Total</div>
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col md={3}>
                        <Card className="border-success">
                          <Card.Body className="text-center">
                            <h3 className="mb-1 text-success">{validationResult.valid}</h3>
                            <div className="small text-muted text-uppercase">Válidos</div>
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col md={3}>
                        <Card className="border-warning">
                          <Card.Body className="text-center">
                            <h3 className="mb-1 text-warning">{validationResult.already_notified}</h3>
                            <div className="small text-muted text-uppercase">Ya Notificados</div>
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col md={3}>
                        <Card className="border-danger">
                          <Card.Body className="text-center">
                            <h3 className="mb-1 text-danger">{validationResult.invalid}</h3>
                            <div className="small text-muted text-uppercase">Inválidos</div>
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>

                    <div className="table-responsive">
                      <Table striped bordered hover>
                        <thead className="bg-light">
                          <tr>
                            <th>IMEI</th>
                            <th>ICCID</th>
                            <th>Package No</th>
                            <th>Estado</th>
                          </tr>
                        </thead>
                        <tbody>
                          {validationResult.results.map((result, idx) => (
                            <tr key={idx}>
                              <td>
                                <code>{result.serial.imei || '-'}</code>
                              </td>
                              <td>
                                <code>{result.serial.iccid || '-'}</code>
                              </td>
                              <td>
                                <code>{result.serial.package_no || '-'}</code>
                              </td>
                              <td>
                                {result.valid ? (
                                  <Badge bg="success">Válido</Badge>
                                ) : result.already_notified ? (
                                  <Badge bg="warning">Ya Notificado</Badge>
                                ) : (
                                  <Badge bg="danger">{result.error || 'Inválido'}</Badge>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </div>
                  </>
                )}
              </Tab.Pane>

              {/* TAB 3: CONFIG */}
              <Tab.Pane eventKey="config">
                <h4 className="mb-3">Configurar Notificación</h4>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>
                        Cliente (opcional)
                      </Form.Label>
                      <Form.Select value={selectedCustomer?.id || ''} onChange={(e) => handleCustomerSelect(e.target.value)}>
                        <option value="">Sin cliente / Manual</option>
                        {customers.length > 0 ? (
                          customers.map((customer) => (
                            <option key={customer.id} value={customer.id}>
                              {customer.name} ({customer.code})
                            </option>
                          ))
                        ) : (
                          <option disabled>No hay clientes disponibles</option>
                        )}
                      </Form.Select>
                      <Form.Text className="text-muted">
                        Opcional: selecciona un cliente para asociar los dispositivos
                      </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>
                        Número de LOTE o Albarán <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Control
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="Ej: LOTE-2025-001 o ALB-25-0123"
                      />
                      <Form.Text className="text-muted">Número de lote de producción o albarán de envío</Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>
                        Tipo de Plantilla <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Select value={csvFormat} onChange={(e) => setCsvFormat(e.target.value as any)}>
                        <option value="separated">📋 Estándar - Dos columnas (IMEI | ICCID)</option>
                        <option value="unified">📝 Simplificado - Una columna (IMEI ICCID)</option>
                        <option value="detailed">📊 Detallado - Incluye marca y referencia</option>
                        <option value="compact">🗜️ Compacto - Solo IMEIs</option>
                      </Form.Select>
                      <Form.Text className="text-muted">
                        Selecciona el formato de archivo que recibirá el destinatario
                      </Form.Text>
                    </Form.Group>
                  </Col>

                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>
                        Email Destinatario <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Control type="email" value={emailTo} onChange={(e) => setEmailTo(e.target.value)} />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Email CC (opcional)</Form.Label>
                      <Form.Control
                        type="text"
                        value={emailCC}
                        onChange={(e) => setEmailCC(e.target.value)}
                        placeholder="email1@example.com, email2@example.com"
                      />
                      <Form.Text className="text-muted">Separar múltiples emails con comas</Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Notas (opcional)</Form.Label>
                      <Form.Control as="textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
                    </Form.Group>
                  </Col>
                </Row>

                <div className="d-flex gap-2">
                  <Button variant="primary" onClick={handlePreview} disabled={!location.trim() || !emailTo.trim()}>
                    <i className="bi bi-eye me-1"></i>
                    Previsualizar CSV
                  </Button>
                  <Button variant="outline-secondary" onClick={() => setActiveTab('validate')}>
                    <i className="bi bi-arrow-left me-1"></i>
                    Volver
                  </Button>
                </div>
              </Tab.Pane>

              {/* TAB 4: PREVIEW */}
              <Tab.Pane eventKey="preview">
                <h4 className="mb-3">Previsualización</h4>

                <Alert variant="info">
                  <strong>Cliente:</strong> {selectedCustomer?.name || 'Sin cliente / Manual'}
                  <br />
                  <strong>Número de LOTE/Albarán:</strong> {location}
                  <br />
                  <strong>Email:</strong> {emailTo}
                  <br />
                  <strong>Dispositivos:</strong> {validatedSerials.length}
                  <br />
                  <strong>Formato:</strong> {
                    csvFormat === 'separated' ? '📋 Estándar - Dos columnas (IMEI | ICCID)' :
                    csvFormat === 'unified' ? '📝 Simplificado - Una columna (IMEI ICCID)' :
                    csvFormat === 'detailed' ? '📊 Detallado - Incluye marca y referencia' :
                    '🗜️ Compacto - Solo IMEIs'
                  }
                </Alert>

                <h5 className="mb-3">Contenido del CSV:</h5>
                <pre
                  className="bg-light p-3 border rounded"
                  style={{ maxHeight: '400px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.875rem' }}
                >
                  {csvPreview}
                </pre>

                <div className="d-flex gap-2">
                  <Button variant="success" onClick={handleSend} disabled={isSending}>
                    {isSending ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Enviando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-send-check-fill me-1"></i>
                        Enviar Notificación
                      </>
                    )}
                  </Button>
                  <Button variant="outline-secondary" onClick={() => setActiveTab('config')}>
                    <i className="bi bi-arrow-left me-1"></i>
                    Volver
                  </Button>
                </div>
              </Tab.Pane>

              {/* TAB 5: HISTORY */}
              <Tab.Pane eventKey="history">
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h4>Historial de Notificaciones</h4>
                  <Button variant="outline-primary" size="sm" onClick={loadHistory}>
                    <i className="bi bi-arrow-clockwise me-1"></i>
                    Actualizar
                  </Button>
                </div>

                {historyLoading ? (
                  <div className="text-center py-5">
                    <Spinner animation="border" variant="primary" />
                  </div>
                ) : history.length === 0 ? (
                  <Alert variant="info">No hay historial disponible</Alert>
                ) : (
                  <div className="table-responsive">
                    <Table hover>
                      <thead className="bg-light">
                        <tr>
                          <th>Fecha</th>
                          <th>Cliente</th>
                          <th>Dispositivos</th>
                          <th>Formato</th>
                          <th>Email</th>
                          <th>Operador</th>
                          <th>Archivo</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((item) => (
                          <tr key={item.id}>
                            <td>{format(new Date(item.date), 'dd/MM/yyyy HH:mm', { locale: es })}</td>
                            <td>{item.customer_name}</td>
                            <td>
                              <Badge bg="primary">{item.device_count}</Badge>
                            </td>
                            <td>{item.csv_format === 'separated' ? 'Separado' : 'Unificado'}</td>
                            <td>
                              <small>{item.email_to}</small>
                            </td>
                            <td>{item.operator}</td>
                            <td>
                              <code className="small">{item.csv_filename}</code>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                )}
              </Tab.Pane>
            </Tab.Content>
          </Card.Body>
        </Card>
      </Tab.Container>
    </Container>
  )
}
