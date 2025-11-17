/**
 * OSE Platform - 404 Not Found Page
 */

import { Container, Row, Col, Button } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'

export default function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <Container fluid className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <Row>
        <Col className="text-center">
          <div className="mb-4">
            <i className="bi bi-exclamation-triangle text-warning" style={{ fontSize: '6rem' }}></i>
          </div>
          <h1 className="display-1 fw-bold text-primary">404</h1>
          <h2 className="mb-3">Página no encontrada</h2>
          <p className="text-muted mb-4">
            Lo sentimos, la página que estás buscando no existe o ha sido movida.
          </p>
          <Button variant="primary" onClick={() => navigate('/dashboard')}>
            <i className="bi bi-house-door me-2"></i>
            Volver al Dashboard
          </Button>
        </Col>
      </Row>
    </Container>
  )
}
