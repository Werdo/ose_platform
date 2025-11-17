/**
 * OSE Platform - Backend Configuration Page
 * Portal de administración y configuración del backend
 */

import { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Nav, Tab, Badge, Alert, Button, Spinner } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import SystemStatusTab from './tabs/SystemStatusTab'
import UsersManagementTab from './tabs/UsersManagementTab'
import DatabaseTab from './tabs/DatabaseTab'
import ApplicationsTab from './tabs/ApplicationsTab'
import LogsTab from './tabs/LogsTab'

interface HealthStatus {
  status: string
  api: string
  database: string
  version: string
}

export default function BackendConfigPage() {
  const [activeTab, setActiveTab] = useState('system')
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadHealth()
    const interval = setInterval(loadHealth, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadHealth = async () => {
    try {
      const response = await fetch('http://localhost:8001/health')
      const data = await response.json()
      setHealth(data)
      setError(null)
    } catch (err) {
      setError('Error conectando con el backend')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = () => {
    if (!health) return <Badge bg="secondary">Desconocido</Badge>
    if (health.status === 'healthy') return <Badge bg="success">Online</Badge>
    return <Badge bg="danger">Offline</Badge>
  }

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2>
                <i className="bi bi-server me-2"></i>
                Configuración del Backend
              </h2>
              <p className="text-muted mb-0">
                Panel de administración y monitoreo del backend API
              </p>
            </div>
            <div className="text-end">
              {loading ? (
                <Spinner animation="border" size="sm" />
              ) : (
                <>
                  <div className="mb-2">
                    <strong>Estado:</strong> {getStatusBadge()}
                  </div>
                  {health && (
                    <div className="small text-muted">
                      Versión: {health.version}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k || 'system')}>
        <Card>
          <Card.Header>
            <Nav variant="tabs" className="card-header-tabs">
              <Nav.Item>
                <Nav.Link eventKey="system">
                  <i className="bi bi-speedometer2 me-2"></i>
                  Estado del Sistema
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="users">
                  <i className="bi bi-people-fill me-2"></i>
                  Usuarios
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="database">
                  <i className="bi bi-database-fill me-2"></i>
                  Base de Datos
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="apps">
                  <i className="bi bi-grid-fill me-2"></i>
                  Aplicaciones
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="logs">
                  <i className="bi bi-file-earmark-text-fill me-2"></i>
                  Logs
                </Nav.Link>
              </Nav.Item>
            </Nav>
          </Card.Header>

          <Card.Body>
            <Tab.Content>
              <Tab.Pane eventKey="system">
                <SystemStatusTab health={health} onRefresh={loadHealth} />
              </Tab.Pane>

              <Tab.Pane eventKey="users">
                <UsersManagementTab />
              </Tab.Pane>

              <Tab.Pane eventKey="database">
                <DatabaseTab />
              </Tab.Pane>

              <Tab.Pane eventKey="apps">
                <ApplicationsTab />
              </Tab.Pane>

              <Tab.Pane eventKey="logs">
                <LogsTab />
              </Tab.Pane>
            </Tab.Content>
          </Card.Body>
        </Card>
      </Tab.Container>
    </Container>
  )
}
