/**
 * OSE Platform - Profile Page
 */

import { Container, Row, Col, Card, Button } from 'react-bootstrap'
import { useAuth } from '../contexts/AuthContext'

export default function ProfilePage() {
  const { user } = useAuth()

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <h2>Mi Perfil</h2>
          <p className="text-muted">Información de tu cuenta</p>
        </Col>
      </Row>

      <Row>
        <Col lg={4}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body className="py-5">
              <div className="mb-3">
                <i className="bi bi-person-circle text-primary" style={{ fontSize: '5rem' }}></i>
              </div>
              <h4 className="mb-1">{user?.name} {user?.surname}</h4>
              <p className="text-muted mb-3">{user?.email}</p>
              <span className="badge bg-primary">{user?.role}</span>
              <span className={`badge ms-2 ${user?.status === 'active' ? 'badge-gradient-success' : 'badge-gradient-inactive'}`}>
                {user?.status}
              </span>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8} className="mt-3 mt-lg-0">
          <Card className="border-0 shadow-sm">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-info-circle me-2"></i>
              Información Personal
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">ID de Empleado:</Col>
                <Col sm={8}>{user?.employee_id}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">Nombre:</Col>
                <Col sm={8}>{user?.name}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">Apellido:</Col>
                <Col sm={8}>{user?.surname}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">Email:</Col>
                <Col sm={8}>{user?.email}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">Rol:</Col>
                <Col sm={8}>
                  <span className="badge bg-primary">{user?.role}</span>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">Estado:</Col>
                <Col sm={8}>
                  <span className={`badge ${user?.status === 'active' ? 'badge-gradient-success' : 'badge-gradient-inactive'}`}>
                    {user?.status}
                  </span>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold text-muted">Último acceso:</Col>
                <Col sm={8}>
                  {user?.last_login
                    ? new Date(user.last_login).toLocaleString('es-ES')
                    : 'Primera vez'}
                </Col>
              </Row>

              <div className="mt-4">
                <Button variant="primary" className="me-2">
                  <i className="bi bi-pencil-square me-1"></i>
                  Editar Perfil
                </Button>
                <Button variant="outline-secondary">
                  <i className="bi bi-key me-1"></i>
                  Cambiar Contraseña
                </Button>
              </div>
            </Card.Body>
          </Card>

          <Card className="border-0 shadow-sm mt-3">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-shield-check me-2"></i>
              Permisos
            </Card.Header>
            <Card.Body>
              <Row>
                {user?.permissions && Object.entries(user.permissions).map(([key, value]) => (
                  <Col sm={6} key={key} className="mb-2">
                    <i className={`bi ${value ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'} me-2`}></i>
                    <span className="text-capitalize">{key.replace(/_/g, ' ')}</span>
                  </Col>
                ))}
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}
