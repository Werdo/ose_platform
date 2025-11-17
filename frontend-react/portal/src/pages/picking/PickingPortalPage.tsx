/**
 * OSE Platform - App 6: Picking Portal Integration Page
 * Provides access to the external picking portal
 */

import { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Button, Alert, Badge } from 'react-bootstrap'
import apiService from '../../services/api.service'

interface PickingStats {
  palets?: {
    total: number
    preparados: number
    en_transito: number
    entregados: number
  }
  paquetes?: {
    total: number
    preparados: number
    enviados: number
    entregados: number
    emails_pendientes: number
  }
}

export default function PickingPortalPage() {
  const [stats, setStats] = useState<PickingStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const PICKING_PORTAL_URL = 'http://localhost:5006'

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.get('/app6/stats')
      setStats(response.data)
    } catch (err: any) {
      console.error('Error loading picking stats:', err)
      setError('No se pudieron cargar las estadísticas del portal de picking')
    } finally {
      setLoading(false)
    }
  }

  const openPickingPortal = (path: string = '') => {
    window.open(`${PICKING_PORTAL_URL}${path}`, '_blank', 'noopener,noreferrer')
  }

  return (
    <Container fluid className="p-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">
            <i className="bi bi-box-seam-fill text-secondary me-2"></i>
            App 6: Picking & Etiquetado
          </h2>
          <p className="text-muted mb-0">
            Portal de gestión de palets y paquetería con tracking
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={() => openPickingPortal()}
          className="d-flex align-items-center"
        >
          <i className="bi bi-box-arrow-up-right me-2"></i>
          Abrir Portal de Picking
        </Button>
      </div>

      {/* Alert Info */}
      <Alert variant="info" className="mb-4">
        <Alert.Heading>
          <i className="bi bi-info-circle me-2"></i>
          Portal Externo
        </Alert.Heading>
        <p className="mb-0">
          El Portal de Picking es una aplicación independiente optimizada para operaciones de almacén.
          Haz clic en los botones de abajo para acceder directamente a cada módulo.
        </p>
      </Alert>

      {/* Statistics */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
        </div>
      )}

      {error && (
        <Alert variant="warning" className="mb-4">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </Alert>
      )}

      {stats && !loading && (
        <Row className="mb-4">
          {/* Palets Stats */}
          <Col lg={6} className="mb-4">
            <Card className="h-100 shadow-sm">
              <Card.Header className="bg-dark text-white">
                <h5 className="mb-0">
                  <i className="bi bi-boxes me-2"></i>
                  Estadísticas de Palets
                </h5>
              </Card.Header>
              <Card.Body>
                <Row className="g-3">
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-primary">{stats.palets?.total || 0}</div>
                      <small className="text-muted">Total Palets</small>
                    </div>
                  </Col>
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-warning">{stats.palets?.preparados || 0}</div>
                      <small className="text-muted">Preparados</small>
                    </div>
                  </Col>
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-info">{stats.palets?.en_transito || 0}</div>
                      <small className="text-muted">En Tránsito</small>
                    </div>
                  </Col>
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-success">{stats.palets?.entregados || 0}</div>
                      <small className="text-muted">Entregados</small>
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>

          {/* Paquetes Stats */}
          <Col lg={6} className="mb-4">
            <Card className="h-100 shadow-sm">
              <Card.Header className="bg-dark text-white">
                <h5 className="mb-0">
                  <i className="bi bi-box-seam me-2"></i>
                  Estadísticas de Paquetería
                </h5>
              </Card.Header>
              <Card.Body>
                <Row className="g-3">
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-primary">{stats.paquetes?.total || 0}</div>
                      <small className="text-muted">Total Paquetes</small>
                    </div>
                  </Col>
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-warning">{stats.paquetes?.preparados || 0}</div>
                      <small className="text-muted">Preparados</small>
                    </div>
                  </Col>
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-info">{stats.paquetes?.enviados || 0}</div>
                      <small className="text-muted">Enviados</small>
                    </div>
                  </Col>
                  <Col xs={6}>
                    <div className="text-center p-3 bg-light rounded">
                      <div className="display-6 fw-bold text-success">{stats.paquetes?.entregados || 0}</div>
                      <small className="text-muted">Entregados</small>
                    </div>
                  </Col>
                </Row>
                {stats.paquetes?.emails_pendientes ? (
                  <Alert variant="warning" className="mt-3 mb-0">
                    <i className="bi bi-envelope-exclamation me-2"></i>
                    <strong>{stats.paquetes.emails_pendientes}</strong> emails de notificación pendientes
                  </Alert>
                ) : null}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Quick Access Modules */}
      <h4 className="mb-3">Módulos del Portal de Picking</h4>
      <Row className="g-4">
        {/* Dashboard */}
        <Col md={6} lg={4}>
          <Card className="h-100 shadow-sm hover-card">
            <Card.Body className="text-center p-4">
              <div className="mb-3">
                <i className="bi bi-speedometer2 text-primary" style={{ fontSize: '3rem' }}></i>
              </div>
              <h5>Dashboard</h5>
              <p className="text-muted mb-3">
                Vista general con estadísticas en tiempo real
              </p>
              <Button
                variant="outline-primary"
                onClick={() => openPickingPortal('/')}
                className="w-100"
              >
                <i className="bi bi-box-arrow-up-right me-2"></i>
                Abrir Dashboard
              </Button>
            </Card.Body>
          </Card>
        </Col>

        {/* Picking de Palets */}
        <Col md={6} lg={4}>
          <Card className="h-100 shadow-sm hover-card">
            <Card.Body className="text-center p-4">
              <div className="mb-3">
                <i className="bi bi-boxes text-dark" style={{ fontSize: '3rem' }}></i>
              </div>
              <h5>Picking de Palets</h5>
              <p className="text-muted mb-3">
                Crear palets, generar QR y gestionar envíos grandes
              </p>
              <Button
                variant="outline-dark"
                onClick={() => openPickingPortal('/palets')}
                className="w-100"
              >
                <i className="bi bi-box-arrow-up-right me-2"></i>
                Abrir Palets
              </Button>
            </Card.Body>
          </Card>
        </Col>

        {/* Picking de Paquetes */}
        <Col md={6} lg={4}>
          <Card className="h-100 shadow-sm hover-card">
            <Card.Body className="text-center p-4">
              <div className="mb-3">
                <i className="bi bi-box-seam text-success" style={{ fontSize: '3rem' }}></i>
              </div>
              <h5>Picking de Paquetería</h5>
              <p className="text-muted mb-3">
                Gestionar paquetes con tracking y notificaciones
              </p>
              <Button
                variant="outline-success"
                onClick={() => openPickingPortal('/paquetes')}
                className="w-100"
              >
                <i className="bi bi-box-arrow-up-right me-2"></i>
                Abrir Paquetes
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Features */}
      <Row className="mt-5">
        <Col lg={6} className="mb-4">
          <Card className="h-100">
            <Card.Header className="bg-light">
              <h5 className="mb-0">
                <i className="bi bi-boxes me-2"></i>
                Funcionalidades de Palets
              </h5>
            </Card.Header>
            <Card.Body>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Crear palets con contenido escaneado
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Generar códigos QR únicos
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Imprimir etiquetas A4
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Tracking de estados (preparado, en_transito, entregado)
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Asociación con pedidos
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Gestión de ubicación en almacén
                </li>
              </ul>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className="mb-4">
          <Card className="h-100">
            <Card.Header className="bg-light">
              <h5 className="mb-0">
                <i className="bi bi-box-seam me-2"></i>
                Funcionalidades de Paquetería
              </h5>
            </Card.Header>
            <Card.Body>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Crear paquetes con tracking de transportista
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Soporte para múltiples transportistas (Seur, Correos, DHL, UPS, FedEx)
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Validación automática de formatos de tracking
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Asociar dispositivos por IMEI
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Envío de notificaciones por email
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle-fill text-success me-2"></i>
                  Generar etiquetas con QR
                </li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Transporters Supported */}
      <Card className="mt-4">
        <Card.Header className="bg-light">
          <h5 className="mb-0">
            <i className="bi bi-truck me-2"></i>
            Transportistas Soportados
          </h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col xs={6} md={4} lg={2} className="text-center mb-3">
              <Badge bg="primary" className="p-3 w-100">
                <i className="bi bi-truck me-2"></i>
                Seur
              </Badge>
            </Col>
            <Col xs={6} md={4} lg={2} className="text-center mb-3">
              <Badge bg="warning" className="p-3 w-100">
                <i className="bi bi-envelope me-2"></i>
                Correos
              </Badge>
            </Col>
            <Col xs={6} md={4} lg={2} className="text-center mb-3">
              <Badge bg="danger" className="p-3 w-100">
                <i className="bi bi-box me-2"></i>
                DHL
              </Badge>
            </Col>
            <Col xs={6} md={4} lg={2} className="text-center mb-3">
              <Badge bg="success" className="p-3 w-100">
                <i className="bi bi-shield-check me-2"></i>
                UPS
              </Badge>
            </Col>
            <Col xs={6} md={4} lg={2} className="text-center mb-3">
              <Badge bg="info" className="p-3 w-100">
                <i className="bi bi-airplane me-2"></i>
                FedEx
              </Badge>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <style>{`
        .hover-card {
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .hover-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
        }
      `}</style>
    </Container>
  )
}
