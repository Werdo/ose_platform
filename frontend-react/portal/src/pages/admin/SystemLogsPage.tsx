/**
 * OSE Platform - System Logs Page
 * Página para visualizar y filtrar logs del sistema
 */

import { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Form, Table, Badge, Button, Spinner, Alert, InputGroup } from 'react-bootstrap'
import apiService from '@/services/api.service'
import toast from 'react-hot-toast'

interface SystemLog {
  _id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  category: string
  message: string
  module?: string
  function?: string
  user_email?: string
  endpoint?: string
  method?: string
  ip_address?: string
  duration_ms?: number
  error_type?: string
  error_message?: string
  data?: any
}

interface LogStats {
  total_logs: number
  logs_by_level: Record<string, number>
  logs_by_category: Record<string, number>
  recent_errors: SystemLog[]
}

const SystemLogsPage = () => {
  const [logs, setLogs] = useState<SystemLog[]>([])
  const [stats, setStats] = useState<LogStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)

  // Filtros
  const [filters, setFilters] = useState({
    level: '',
    category: '',
    search: '',
    user_email: '',
    endpoint: '',
    limit: 100,
    skip: 0
  })

  // Estados de UI
  const [showFilters, setShowFilters] = useState(true)
  const [selectedLog, setSelectedLog] = useState<SystemLog | null>(null)

  // Cargar logs
  const fetchLogs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()

      if (filters.level) params.append('level', filters.level)
      if (filters.category) params.append('category', filters.category)
      if (filters.search) params.append('search', filters.search)
      if (filters.user_email) params.append('user_email', filters.user_email)
      if (filters.endpoint) params.append('endpoint', filters.endpoint)
      params.append('limit', filters.limit.toString())
      params.append('skip', filters.skip.toString())

      const data = await apiService.get<any>(`/api/v1/logs?${params.toString()}`)

      setLogs(data.logs)
      setTotal(data.total)
    } catch (error: any) {
      toast.error('Error cargando logs: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // Cargar estadísticas
  const fetchStats = async () => {
    try {
      const data = await apiService.get<LogStats>('/api/v1/logs/stats?hours=24')
      setStats(data)
    } catch (error: any) {
      console.error('Error cargando estadísticas:', error)
    }
  }

  // Exportar logs a CSV
  const exportLogs = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.level) params.append('level', filters.level)
      if (filters.category) params.append('category', filters.category)
      params.append('limit', '1000')

      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
      const response = await fetch(`${API_BASE_URL}/api/v1/logs/export/csv?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (!response.ok) throw new Error('Error exportando logs')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `system_logs_${new Date().toISOString()}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success('Logs exportados exitosamente')
    } catch (error: any) {
      toast.error('Error exportando logs')
    }
  }

  useEffect(() => {
    fetchLogs()
    fetchStats()
  }, [filters.level, filters.category, filters.limit, filters.skip])

  // Función para obtener el color del badge según el nivel
  const getLevelBadge = (level: string) => {
    const colors: Record<string, string> = {
      DEBUG: 'secondary',
      INFO: 'info',
      WARNING: 'warning',
      ERROR: 'danger',
      CRITICAL: 'dark'
    }
    return <Badge bg={colors[level] || 'secondary'}>{level}</Badge>
  }

  // Función para obtener el color del badge según la categoría
  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      system: 'secondary',
      auth: 'primary',
      api: 'info',
      database: 'success',
      import: 'warning',
      error: 'danger'
    }
    return <Badge bg={colors[category] || 'secondary'}>{category}</Badge>
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return '-'
    if (ms < 1000) return `${ms.toFixed(0)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <h2 className="mb-3">
            <i className="bi bi-journal-text me-2"></i>
            Logs del Sistema
          </h2>
          <p className="text-muted">
            Monitoreo y auditoría de eventos del sistema
          </p>
        </Col>
      </Row>

      {/* Estadísticas */}
      {stats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="mb-0">{stats.total_logs}</h3>
                <small className="text-muted">Logs (últimas 24h)</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-danger">
              <Card.Body>
                <h3 className="mb-0 text-danger">{stats.logs_by_level.ERROR || 0}</h3>
                <small className="text-muted">Errores</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-warning">
              <Card.Body>
                <h3 className="mb-0 text-warning">{stats.logs_by_level.WARNING || 0}</h3>
                <small className="text-muted">Advertencias</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-info">
              <Card.Body>
                <h3 className="mb-0 text-info">{stats.logs_by_level.INFO || 0}</h3>
                <small className="text-muted">Informativos</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Filtros */}
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <span>
            <i className="bi bi-funnel me-2"></i>
            Filtros
          </span>
          <Button
            variant="link"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? 'Ocultar' : 'Mostrar'}
          </Button>
        </Card.Header>
        {showFilters && (
          <Card.Body>
            <Row>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Nivel</Form.Label>
                  <Form.Select
                    value={filters.level}
                    onChange={(e) => setFilters({ ...filters, level: e.target.value, skip: 0 })}
                  >
                    <option value="">Todos</option>
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Categoría</Form.Label>
                  <Form.Select
                    value={filters.category}
                    onChange={(e) => setFilters({ ...filters, category: e.target.value, skip: 0 })}
                  >
                    <option value="">Todas</option>
                    <option value="system">System</option>
                    <option value="auth">Auth</option>
                    <option value="api">API</option>
                    <option value="database">Database</option>
                    <option value="import">Import</option>
                    <option value="export">Export</option>
                    <option value="email">Email</option>
                    <option value="error">Error</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Usuario</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Email del usuario"
                    value={filters.user_email}
                    onChange={(e) => setFilters({ ...filters, user_email: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Buscar en mensaje</Form.Label>
                  <InputGroup>
                    <InputGroup.Text><i className="bi bi-search"></i></InputGroup.Text>
                    <Form.Control
                      type="text"
                      placeholder="Buscar..."
                      value={filters.search}
                      onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                    />
                  </InputGroup>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col className="d-flex gap-2">
                <Button variant="primary" onClick={fetchLogs} disabled={loading}>
                  <i className="bi bi-arrow-clockwise me-1"></i>
                  Actualizar
                </Button>
                <Button variant="success" onClick={exportLogs}>
                  <i className="bi bi-download me-1"></i>
                  Exportar CSV
                </Button>
                <Button
                  variant="outline-secondary"
                  onClick={() => {
                    setFilters({
                      level: '',
                      category: '',
                      search: '',
                      user_email: '',
                      endpoint: '',
                      limit: 100,
                      skip: 0
                    })
                  }}
                >
                  Limpiar Filtros
                </Button>
              </Col>
            </Row>
          </Card.Body>
        )}
      </Card>

      {/* Tabla de logs */}
      <Card>
        <Card.Header className="d-flex justify-content-between align-items-center">
          <span>
            <i className="bi bi-list-ul me-2"></i>
            Logs ({total} total)
          </span>
          <div className="d-flex gap-2 align-items-center">
            <Form.Select
              size="sm"
              style={{ width: 'auto' }}
              value={filters.limit}
              onChange={(e) => setFilters({ ...filters, limit: Number(e.target.value), skip: 0 })}
            >
              <option value={50}>50 por página</option>
              <option value={100}>100 por página</option>
              <option value={200}>200 por página</option>
              <option value={500}>500 por página</option>
            </Form.Select>
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-3 text-muted">Cargando logs...</p>
            </div>
          ) : logs.length === 0 ? (
            <Alert variant="info" className="m-3">
              No se encontraron logs con los filtros seleccionados
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table hover className="mb-0">
                <thead className="table-light">
                  <tr>
                    <th style={{ width: '140px' }}>Timestamp</th>
                    <th style={{ width: '80px' }}>Nivel</th>
                    <th style={{ width: '100px' }}>Categoría</th>
                    <th>Mensaje</th>
                    <th style={{ width: '150px' }}>Usuario</th>
                    <th style={{ width: '200px' }}>Endpoint</th>
                    <th style={{ width: '80px' }}>Duración</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr
                      key={log._id}
                      onClick={() => setSelectedLog(log)}
                      style={{ cursor: 'pointer' }}
                      className={log.level === 'ERROR' || log.level === 'CRITICAL' ? 'table-danger' : ''}
                    >
                      <td>
                        <small>{new Date(log.timestamp).toLocaleString()}</small>
                      </td>
                      <td>{getLevelBadge(log.level)}</td>
                      <td>{getCategoryBadge(log.category)}</td>
                      <td>
                        <div className="text-truncate" style={{ maxWidth: '400px' }}>
                          {log.message}
                        </div>
                        {log.error_message && (
                          <small className="text-danger d-block">
                            {log.error_message}
                          </small>
                        )}
                      </td>
                      <td>
                        <small className="text-muted">{log.user_email || '-'}</small>
                      </td>
                      <td>
                        <small className="font-monospace">
                          {log.method && <Badge bg="secondary" className="me-1">{log.method}</Badge>}
                          {log.endpoint || '-'}
                        </small>
                      </td>
                      <td>
                        <small className="text-muted">{formatDuration(log.duration_ms)}</small>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
        {total > filters.limit && (
          <Card.Footer className="d-flex justify-content-between align-items-center">
            <span className="text-muted">
              Mostrando {filters.skip + 1} - {Math.min(filters.skip + filters.limit, total)} de {total}
            </span>
            <div className="d-flex gap-2">
              <Button
                variant="outline-primary"
                size="sm"
                disabled={filters.skip === 0}
                onClick={() => setFilters({ ...filters, skip: Math.max(0, filters.skip - filters.limit) })}
              >
                ← Anterior
              </Button>
              <Button
                variant="outline-primary"
                size="sm"
                disabled={filters.skip + filters.limit >= total}
                onClick={() => setFilters({ ...filters, skip: filters.skip + filters.limit })}
              >
                Siguiente →
              </Button>
            </div>
          </Card.Footer>
        )}
      </Card>

      {/* Modal de detalles del log (simplificado, puedes expandir) */}
      {selectedLog && (
        <div
          className="modal fade show d-block"
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSelectedLog(null)}
        >
          <div className="modal-dialog modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Detalles del Log</h5>
                <button type="button" className="btn-close" onClick={() => setSelectedLog(null)}></button>
              </div>
              <div className="modal-body">
                <Table bordered size="sm">
                  <tbody>
                    <tr>
                      <th style={{ width: '200px' }}>Timestamp</th>
                      <td>{new Date(selectedLog.timestamp).toLocaleString()}</td>
                    </tr>
                    <tr>
                      <th>Nivel</th>
                      <td>{getLevelBadge(selectedLog.level)}</td>
                    </tr>
                    <tr>
                      <th>Categoría</th>
                      <td>{getCategoryBadge(selectedLog.category)}</td>
                    </tr>
                    <tr>
                      <th>Mensaje</th>
                      <td>{selectedLog.message}</td>
                    </tr>
                    {selectedLog.user_email && (
                      <tr>
                        <th>Usuario</th>
                        <td>{selectedLog.user_email}</td>
                      </tr>
                    )}
                    {selectedLog.endpoint && (
                      <tr>
                        <th>Endpoint</th>
                        <td>
                          {selectedLog.method && <Badge bg="secondary" className="me-2">{selectedLog.method}</Badge>}
                          <code>{selectedLog.endpoint}</code>
                        </td>
                      </tr>
                    )}
                    {selectedLog.module && (
                      <tr>
                        <th>Módulo</th>
                        <td><code>{selectedLog.module}.{selectedLog.function}</code></td>
                      </tr>
                    )}
                    {selectedLog.duration_ms && (
                      <tr>
                        <th>Duración</th>
                        <td>{formatDuration(selectedLog.duration_ms)}</td>
                      </tr>
                    )}
                    {selectedLog.error_message && (
                      <tr>
                        <th>Error</th>
                        <td className="text-danger">{selectedLog.error_message}</td>
                      </tr>
                    )}
                    {selectedLog.data && (
                      <tr>
                        <th>Datos Adicionales</th>
                        <td>
                          <pre className="mb-0" style={{ fontSize: '12px' }}>
                            {JSON.stringify(selectedLog.data, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </Table>
              </div>
              <div className="modal-footer">
                <Button variant="secondary" onClick={() => setSelectedLog(null)}>
                  Cerrar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </Container>
  )
}

export default SystemLogsPage
