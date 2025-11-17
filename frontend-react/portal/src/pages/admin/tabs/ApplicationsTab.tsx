/**
 * Applications Tab - Enable/Disable Apps 1-6
 */

import { useState } from 'react'
import { Row, Col, Card, Form, Badge, Button, Alert, ListGroup } from 'react-bootstrap'

interface App {
  id: number
  name: string
  description: string
  icon: string
  color: string
  enabled: boolean
  route: string
}

export default function ApplicationsTab() {
  const [apps, setApps] = useState<App[]>([
    {
      id: 1,
      name: 'Notificación de Series',
      description: 'Notificar dispositivos a clientes específicos',
      icon: 'bi-bell-fill',
      color: 'primary',
      enabled: true,
      route: '/app1'
    },
    {
      id: 2,
      name: 'Importación de Datos',
      description: 'Importar datos desde Excel/CSV',
      icon: 'bi-file-earmark-arrow-down-fill',
      color: 'success',
      enabled: false,
      route: '/app2'
    },
    {
      id: 3,
      name: 'RMA & Tickets',
      description: 'Gestión de tickets de soporte y casos RMA',
      icon: 'bi-ticket-perforated-fill',
      color: 'warning',
      enabled: false,
      route: '/app3'
    },
    {
      id: 4,
      name: 'Transform Data',
      description: 'Transformación y procesamiento de datos',
      icon: 'bi-arrow-repeat',
      color: 'info',
      enabled: false,
      route: '/app4'
    },
    {
      id: 5,
      name: 'Generación de Facturas',
      description: 'Generación automática de facturas',
      icon: 'bi-receipt-cutoff',
      color: 'danger',
      enabled: false,
      route: '/app5'
    },
    {
      id: 6,
      name: 'Picking Lists',
      description: 'Generación de listas de picking para almacén',
      icon: 'bi-box-seam-fill',
      color: 'secondary',
      enabled: false,
      route: '/app6'
    }
  ])

  const [showSuccess, setShowSuccess] = useState(false)

  const toggleApp = (appId: number) => {
    setApps(apps.map(app =>
      app.id === appId ? { ...app, enabled: !app.enabled } : app
    ))
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 3000)
  }

  const enabledCount = apps.filter(app => app.enabled).length

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h5 className="mb-1">Configuración de Aplicaciones</h5>
          <small className="text-muted">
            {enabledCount} de {apps.length} aplicaciones habilitadas
          </small>
        </div>
        <Button variant="outline-primary" size="sm">
          <i className="bi bi-arrow-clockwise me-2"></i>
          Guardar Cambios
        </Button>
      </div>

      {showSuccess && (
        <Alert variant="success" dismissible onClose={() => setShowSuccess(false)}>
          <i className="bi bi-check-circle me-2"></i>
          Configuración actualizada correctamente
        </Alert>
      )}

      <Alert variant="info">
        <i className="bi bi-info-circle me-2"></i>
        Las aplicaciones deshabilitadas no aparecerán en el menú y sus rutas estarán inaccesibles.
      </Alert>

      <Row className="g-3">
        {apps.map(app => (
          <Col md={6} key={app.id}>
            <Card className={app.enabled ? 'border-primary' : ''}>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start mb-3">
                  <div className="d-flex align-items-center">
                    <div
                      className={`rounded-circle d-flex align-items-center justify-content-center me-3`}
                      style={{
                        width: '50px',
                        height: '50px',
                        backgroundColor: `var(--bs-${app.color})`,
                        color: 'white'
                      }}
                    >
                      <i className={app.icon} style={{ fontSize: '1.5rem' }}></i>
                    </div>
                    <div>
                      <h6 className="mb-1">
                        App {app.id}: {app.name}
                      </h6>
                      <small className="text-muted">{app.description}</small>
                    </div>
                  </div>
                  <Form.Check
                    type="switch"
                    id={`app-${app.id}-switch`}
                    checked={app.enabled}
                    onChange={() => toggleApp(app.id)}
                    className="ms-2"
                  />
                </div>

                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    {app.enabled ? (
                      <Badge bg="success">Habilitada</Badge>
                    ) : (
                      <Badge bg="secondary">Deshabilitada</Badge>
                    )}
                  </div>
                  <div>
                    <small className="text-muted">
                      <i className="bi bi-link-45deg me-1"></i>
                      {app.route}
                    </small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Environment Variables */}
      <Card className="mt-4">
        <Card.Header>
          <i className="bi bi-gear me-2"></i>
          Variables de Entorno
        </Card.Header>
        <ListGroup variant="flush">
          {apps.map(app => (
            <ListGroup.Item key={app.id} className="d-flex justify-content-between align-items-center">
              <div>
                <code>FEATURE_APP{app.id}_ENABLED</code>
              </div>
              <Badge bg={app.enabled ? 'success' : 'secondary'}>
                {app.enabled ? 'true' : 'false'}
              </Badge>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Card>

      {/* Configuration Note */}
      <Alert variant="warning" className="mt-3">
        <strong><i className="bi bi-exclamation-triangle me-2"></i>Nota:</strong>
        Los cambios en la configuración de aplicaciones requieren reiniciar el backend para tener efecto.
        Puedes reiniciar el backend desde el tab "Estado del Sistema".
      </Alert>
    </div>
  )
}
