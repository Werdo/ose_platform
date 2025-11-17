/**
 * Logs Tab - System logs viewer
 */

import { useState, useEffect, useRef } from 'react'
import { Card, Form, Button, Badge, Row, Col, InputGroup } from 'react-bootstrap'

interface LogEntry {
  timestamp: string
  level: string
  message: string
  module: string
}

export default function LogsTab() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filter, setFilter] = useState('')
  const [levelFilter, setLevelFilter] = useState('all')
  const [autoScroll, setAutoScroll] = useState(true)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Simular logs en tiempo real
    const interval = setInterval(() => {
      const newLog: LogEntry = {
        timestamp: new Date().toISOString(),
        level: ['INFO', 'DEBUG', 'WARNING', 'ERROR'][Math.floor(Math.random() * 4)],
        message: generateRandomMessage(),
        module: ['main', 'auth', 'app1', 'database'][Math.floor(Math.random() * 4)]
      }
      setLogs(prev => [...prev, newLog].slice(-100)) // Keep last 100 logs
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  const generateRandomMessage = () => {
    const messages = [
      'Request processed successfully',
      'User authentication completed',
      'Database connection established',
      'API endpoint called',
      'Cache updated',
      'Background task completed',
      'Health check passed',
      'Email sent successfully'
    ]
    return messages[Math.floor(Math.random() * messages.length)]
  }

  const getLevelBadge = (level: string) => {
    const variants: Record<string, string> = {
      INFO: 'info',
      DEBUG: 'secondary',
      WARNING: 'warning',
      ERROR: 'danger'
    }
    return <Badge bg={variants[level] || 'secondary'}>{level}</Badge>
  }

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      INFO: '#0dcaf0',
      DEBUG: '#6c757d',
      WARNING: '#ffc107',
      ERROR: '#dc3545'
    }
    return colors[level] || '#6c757d'
  }

  const filteredLogs = logs.filter(log => {
    const matchesText = !filter ||
      log.message.toLowerCase().includes(filter.toLowerCase()) ||
      log.module.toLowerCase().includes(filter.toLowerCase())

    const matchesLevel = levelFilter === 'all' || log.level === levelFilter

    return matchesText && matchesLevel
  })

  const handleClearLogs = () => {
    if (confirm('¿Estás seguro de limpiar todos los logs?')) {
      setLogs([])
    }
  }

  const handleExportLogs = () => {
    const dataStr = JSON.stringify(logs, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ose-logs-${new Date().toISOString().split('T')[0]}.json`
    link.click()
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">Logs del Sistema</h5>
        <div className="d-flex gap-2">
          <Form.Check
            type="switch"
            id="auto-scroll-switch"
            label="Auto-scroll"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
          />
          <Button variant="outline-secondary" size="sm" onClick={handleExportLogs}>
            <i className="bi bi-download me-2"></i>
            Exportar
          </Button>
          <Button variant="outline-danger" size="sm" onClick={handleClearLogs}>
            <i className="bi bi-trash me-2"></i>
            Limpiar
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Row className="mb-3">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Buscar en logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </InputGroup>
        </Col>
        <Col md={3}>
          <Form.Select value={levelFilter} onChange={(e) => setLevelFilter(e.target.value)}>
            <option value="all">Todos los niveles</option>
            <option value="INFO">INFO</option>
            <option value="DEBUG">DEBUG</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </Form.Select>
        </Col>
        <Col md={3}>
          <div className="text-end">
            <Badge bg="primary">{filteredLogs.length}</Badge>
            <span className="text-muted ms-2">entradas</span>
          </div>
        </Col>
      </Row>

      {/* Logs Console */}
      <Card className="bg-dark text-light" style={{ height: '500px', overflow: 'auto' }}>
        <Card.Body style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
          {filteredLogs.length === 0 ? (
            <div className="text-center text-muted py-5">
              <i className="bi bi-inbox" style={{ fontSize: '3rem' }}></i>
              <p className="mt-3">No hay logs disponibles</p>
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div
                key={index}
                className="mb-2 pb-2 border-bottom border-secondary"
                style={{ borderColor: getLevelColor(log.level) + '!important' }}
              >
                <div className="d-flex align-items-start gap-2">
                  <span className="text-muted" style={{ minWidth: '180px' }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                  <span style={{ minWidth: '80px' }}>
                    {getLevelBadge(log.level)}
                  </span>
                  <span className="text-info" style={{ minWidth: '100px' }}>
                    [{log.module}]
                  </span>
                  <span className="flex-grow-1">{log.message}</span>
                </div>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </Card.Body>
      </Card>

      {/* Legend */}
      <Card className="mt-3">
        <Card.Body>
          <div className="d-flex gap-3 align-items-center">
            <strong className="me-3">Leyenda:</strong>
            <div className="d-flex align-items-center gap-2">
              {getLevelBadge('INFO')}
              <small className="text-muted">Informativo</small>
            </div>
            <div className="d-flex align-items-center gap-2">
              {getLevelBadge('DEBUG')}
              <small className="text-muted">Debug</small>
            </div>
            <div className="d-flex align-items-center gap-2">
              {getLevelBadge('WARNING')}
              <small className="text-muted">Advertencia</small>
            </div>
            <div className="d-flex align-items-center gap-2">
              {getLevelBadge('ERROR')}
              <small className="text-muted">Error</small>
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  )
}
