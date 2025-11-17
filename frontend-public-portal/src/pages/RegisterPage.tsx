/**
 * Public Portal - Register Page
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap'
import { apiService } from '../services/api'

interface RegisterPageProps {
  onRegister: () => void
}

export default function RegisterPage({ onRegister }: RegisterPageProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    nombre: '',
    apellidos: '',
    telefono: '',
    empresa: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate
    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden')
      return
    }

    if (formData.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      return
    }

    setLoading(true)

    try {
      const response = await apiService.register({
        email: formData.email,
        password: formData.password,
        nombre: formData.nombre,
        apellidos: formData.apellidos || undefined,
        telefono: formData.telefono || undefined,
        empresa: formData.empresa || undefined
      })

      if (response.success) {
        // Save token and user
        localStorage.setItem('public_token', response.access_token)
        localStorage.setItem('public_user', JSON.stringify(response.user))

        onRegister()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrar usuario')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      paddingTop: '2rem',
      paddingBottom: '2rem'
    }}>
      <Container>
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
            <Card className="shadow-lg">
              <Card.Body className="p-5">
                <div className="text-center mb-4">
                  <i className="bi bi-person-plus" style={{ fontSize: '3rem', color: '#667eea' }}></i>
                  <h3 className="mt-3">Crear Cuenta</h3>
                  <p className="text-muted">Portal Público OSE</p>
                </div>

                {error && (
                  <Alert variant="danger" dismissible onClose={() => setError('')}>
                    {error}
                  </Alert>
                )}

                <Form onSubmit={handleSubmit}>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Nombre *</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder="Juan"
                          value={formData.nombre}
                          onChange={(e) => handleChange('nombre', e.target.value)}
                          required
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Apellidos</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder="García"
                          value={formData.apellidos}
                          onChange={(e) => handleChange('apellidos', e.target.value)}
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <Form.Group className="mb-3">
                    <Form.Label>Email *</Form.Label>
                    <Form.Control
                      type="email"
                      placeholder="tu@email.com"
                      value={formData.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      required
                    />
                  </Form.Group>

                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Contraseña *</Form.Label>
                        <Form.Control
                          type="password"
                          placeholder="Mínimo 8 caracteres"
                          value={formData.password}
                          onChange={(e) => handleChange('password', e.target.value)}
                          required
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Confirmar Contraseña *</Form.Label>
                        <Form.Control
                          type="password"
                          placeholder="Repite tu contraseña"
                          value={formData.confirmPassword}
                          onChange={(e) => handleChange('confirmPassword', e.target.value)}
                          required
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Teléfono</Form.Label>
                        <Form.Control
                          type="tel"
                          placeholder="+34 600 000 000"
                          value={formData.telefono}
                          onChange={(e) => handleChange('telefono', e.target.value)}
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Empresa</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder="Nombre de empresa"
                          value={formData.empresa}
                          onChange={(e) => handleChange('empresa', e.target.value)}
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <Button
                    variant="primary"
                    type="submit"
                    className="w-100 mb-3"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" />
                        Registrando...
                      </>
                    ) : (
                      'Crear Cuenta'
                    )}
                  </Button>

                  <div className="text-center">
                    <small className="text-muted">
                      ¿Ya tienes cuenta?{' '}
                      <Link to="/login" className="text-decoration-none">
                        Inicia sesión aquí
                      </Link>
                    </small>
                  </div>
                </Form>
              </Card.Body>
            </Card>

            <div className="text-center mt-3">
              <small className="text-white">
                <i className="bi bi-shield-check me-1"></i>
                Plataforma segura OSE Platform v2.0
              </small>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  )
}
