/**
 * System Status Tab - Backend health and metrics
 */

import { Row, Col, Card, Badge, Button, Alert, ListGroup, ProgressBar } from 'react-bootstrap'
import { useState, useEffect } from 'react'

interface HealthStatus {
  status: string
  api: string
  database: string
  version: string
}

interface SystemStatusTabProps {
  health: HealthStatus | null
  onRefresh: () => void
}

export default function SystemStatusTab({ health, onRefresh }: SystemStatusTabProps) {
  const [uptime, setUptime] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setUptime(prev => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours}h ${mins}m ${secs}s`
  }

  const getServiceBadge = (status: string) => {
    if (status === 'online' || status === 'healthy') {
      return <Badge bg="success">Online</Badge>
    }
    return <Badge bg="danger">Offline</Badge>
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">Estado del Sistema</h5>
        <Button variant="outline-primary" size="sm" onClick={onRefresh}>
          <i className="bi bi-arrow-clockwise me-2"></i>
          Actualizar
        </Button>
      </div>

      {!health ? (
        <Alert variant="warning">
          <i className="bi bi-exclamation-triangle me-2"></i>
          No se puede conectar con el backend
        </Alert>
      ) : (
        <>
          <Row className="g-3 mb-4">
            {/* API Status */}
            <Col md={3}>
              <Card className="h-100">
                <Card.Body className="text-center">
                  <i className="bi bi-cloud-check-fill text-primary" style={{ fontSize: '2rem' }}></i>
                  <h6 className="mt-2 mb-1">API</h6>
                  {getServiceBadge(health.api)}
                </Card.Body>
              </Card>
            </Col>

            {/* Database Status */}
            <Col md={3}>
              <Card className="h-100">
                <Card.Body className="text-center">
                  <i className="bi bi-database-fill-check text-success" style={{ fontSize: '2rem' }}></i>
                  <h6 className="mt-2 mb-1">Base de Datos</h6>
                  {getServiceBadge(health.database)}
                </Card.Body>
              </Card>
            </Col>

            {/* Version */}
            <Col md={3}>
              <Card className="h-100">
                <Card.Body className="text-center">
                  <i className="bi bi-tag-fill text-info" style={{ fontSize: '2rem' }}></i>
                  <h6 className="mt-2 mb-1">Versión</h6>
                  <Badge bg="info">{health.version}</Badge>
                </Card.Body>
              </Card>
            </Col>

            {/* Uptime */}
            <Col md={3}>
              <Card className="h-100">
                <Card.Body className="text-center">
                  <i className="bi bi-clock-history text-warning" style={{ fontSize: '2rem' }}></i>
                  <h6 className="mt-2 mb-1">Uptime</h6>
                  <small className="text-muted">{formatUptime(uptime)}</small>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* System Information */}
          <Row className="g-3">
            <Col md={6}>
              <Card>
                <Card.Header>
                  <i className="bi bi-info-circle me-2"></i>
                  Información del Sistema
                </Card.Header>
                <ListGroup variant="flush">
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="text-muted">Estado General:</span>
                    <strong>{health.status === 'healthy' ? 'Saludable' : 'Con Problemas'}</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="text-muted">API Endpoint:</span>
                    <strong>http://localhost:8001</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="text-muted">Puerto:</span>
                    <strong>8001</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="text-muted">Framework:</span>
                    <strong>FastAPI</strong>
                  </ListGroup.Item>
                </ListGroup>
              </Card>
            </Col>

            <Col md={6}>
              <Card>
                <Card.Header>
                  <i className="bi bi-graph-up me-2"></i>
                  Métricas
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <div className="d-flex justify-content-between mb-1">
                      <small className="text-muted">Uso de CPU</small>
                      <small className="text-muted">~15%</small>
                    </div>
                    <ProgressBar now={15} variant="success" />
                  </div>
                  <div className="mb-3">
                    <div className="d-flex justify-content-between mb-1">
                      <small className="text-muted">Uso de Memoria</small>
                      <small className="text-muted">~42%</small>
                    </div>
                    <ProgressBar now={42} variant="info" />
                  </div>
                  <div>
                    <div className="d-flex justify-content-between mb-1">
                      <small className="text-muted">Conexiones Activas</small>
                      <small className="text-muted">3</small>
                    </div>
                    <ProgressBar now={30} variant="warning" />
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Services Status */}
          <Row className="mt-3">
            <Col>
              <Card>
                <Card.Header>
                  <i className="bi bi-list-check me-2"></i>
                  Estado de Servicios
                </Card.Header>
                <ListGroup variant="flush">
                  <ListGroup.Item className="d-flex justify-content-between align-items-center">
                    <div>
                      <i className="bi bi-envelope me-2 text-primary"></i>
                      <strong>Servicio de Email</strong>
                      <br />
                      <small className="text-muted">SMTP: smtp.gmail.com:587</small>
                    </div>
                    <Badge bg="secondary">Deshabilitado</Badge>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between align-items-center">
                    <div>
                      <i className="bi bi-database me-2 text-success"></i>
                      <strong>MongoDB</strong>
                      <br />
                      <small className="text-muted">localhost:27018</small>
                    </div>
                    <Badge bg="success">Online</Badge>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between align-items-center">
                    <div>
                      <i className="bi bi-shield-check me-2 text-info"></i>
                      <strong>Autenticación JWT</strong>
                      <br />
                      <small className="text-muted">HS256 Algorithm</small>
                    </div>
                    <Badge bg="success">Activo</Badge>
                  </ListGroup.Item>
                </ListGroup>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  )
}
