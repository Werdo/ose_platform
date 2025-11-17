/**
 * OSE Platform - Settings Page
 */

import { Container, Row, Col, Card, Form, Button } from 'react-bootstrap'

export default function SettingsPage() {
  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <h2>Configuración</h2>
          <p className="text-muted">Personaliza tu experiencia</p>
        </Col>
      </Row>

      <Row>
        <Col lg={6}>
          <Card className="border-0 shadow-sm mb-3">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-palette me-2"></i>
              Apariencia
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Tema</Form.Label>
                  <Form.Select>
                    <option>Claro</option>
                    <option>Oscuro</option>
                    <option>Automático</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Tamaño de fuente</Form.Label>
                  <Form.Select>
                    <option>Pequeño</option>
                    <option selected>Mediano</option>
                    <option>Grande</option>
                  </Form.Select>
                </Form.Group>

                <Button variant="primary">
                  <i className="bi bi-check-lg me-1"></i>
                  Guardar Cambios
                </Button>
              </Form>
            </Card.Body>
          </Card>

          <Card className="border-0 shadow-sm">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-bell me-2"></i>
              Notificaciones
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Check
                  type="switch"
                  id="email-notifications"
                  label="Notificaciones por email"
                  className="mb-3"
                  defaultChecked
                />
                <Form.Check
                  type="switch"
                  id="push-notifications"
                  label="Notificaciones push"
                  className="mb-3"
                  defaultChecked
                />
                <Form.Check
                  type="switch"
                  id="sound-notifications"
                  label="Sonidos de notificación"
                  className="mb-3"
                />

                <Button variant="primary">
                  <i className="bi bi-check-lg me-1"></i>
                  Guardar Cambios
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className="mt-3 mt-lg-0">
          <Card className="border-0 shadow-sm mb-3">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-globe me-2"></i>
              Regional
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Idioma</Form.Label>
                  <Form.Select>
                    <option selected>Español</option>
                    <option>English</option>
                    <option>Français</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Zona horaria</Form.Label>
                  <Form.Select>
                    <option selected>Europe/Madrid (UTC+1)</option>
                    <option>America/New_York (UTC-5)</option>
                    <option>Asia/Tokyo (UTC+9)</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Formato de fecha</Form.Label>
                  <Form.Select>
                    <option selected>DD/MM/YYYY</option>
                    <option>MM/DD/YYYY</option>
                    <option>YYYY-MM-DD</option>
                  </Form.Select>
                </Form.Group>

                <Button variant="primary">
                  <i className="bi bi-check-lg me-1"></i>
                  Guardar Cambios
                </Button>
              </Form>
            </Card.Body>
          </Card>

          <Card className="border-0 shadow-sm">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-shield-lock me-2"></i>
              Seguridad
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <Button variant="outline-primary" className="w-100 mb-2">
                  <i className="bi bi-key me-2"></i>
                  Cambiar Contraseña
                </Button>
                <Button variant="outline-secondary" className="w-100">
                  <i className="bi bi-shield-check me-2"></i>
                  Autenticación de dos factores
                </Button>
              </div>

              <hr />

              <div>
                <h6 className="text-danger mb-3">Zona de Peligro</h6>
                <Button variant="outline-danger" className="w-100">
                  <i className="bi bi-trash me-2"></i>
                  Eliminar Cuenta
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}
