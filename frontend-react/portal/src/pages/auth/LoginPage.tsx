/**
 * OSE Platform - Login Page
 * Design based on Assetflow 3.0
 */

import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap'
import { Formik } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../../contexts/AuthContext'

// Validation schema
const LoginSchema = Yup.object().shape({
  identifier: Yup.string()
    .required('El email o ID de empleado es requerido')
    .min(3, 'Debe tener al menos 3 caracteres'),
  password: Yup.string()
    .required('La contraseña es requerida')
    .min(6, 'La contraseña debe tener al menos 6 caracteres'),
})

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')

  const from = (location.state as any)?.from?.pathname || '/dashboard'

  const handleSubmit = async (values: { identifier: string; password: string }) => {
    setError('')
    try {
      await login(values)
      navigate(from, { replace: true })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.')
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center' }}>
      <Container>
        <Row className="justify-content-center">
          <Col xs={12} md={6} lg={5} xl={4}>
            <Card className="shadow-sm">
              <Card.Body className="p-4">
                {/* Header */}
                <div className="text-center mb-4">
                  <h3 className="mb-2">OSE Platform 1.0</h3>
                  <p className="text-muted mb-0">Sistema de Gestión de Producción</p>
                </div>

                {/* Error Alert */}
                {error && (
                  <Alert variant="danger" dismissible onClose={() => setError('')}>
                    {error}
                  </Alert>
                )}

                {/* Login Form */}
                <Formik
                  initialValues={{ identifier: '', password: '' }}
                  validationSchema={LoginSchema}
                  onSubmit={handleSubmit}
                >
                  {({ values, errors, touched, handleChange, handleBlur, handleSubmit, isSubmitting }) => (
                    <Form onSubmit={handleSubmit}>
                      {/* Email / Employee ID */}
                      <Form.Group className="mb-3" controlId="identifier">
                        <Form.Label>Email o ID de Empleado</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder="Ingresa tu email o ID"
                          name="identifier"
                          value={values.identifier}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          isInvalid={touched.identifier && !!errors.identifier}
                          disabled={isSubmitting}
                        />
                        <Form.Control.Feedback type="invalid">
                          {errors.identifier}
                        </Form.Control.Feedback>
                      </Form.Group>

                      {/* Password */}
                      <Form.Group className="mb-3" controlId="password">
                        <Form.Label>Contraseña</Form.Label>
                        <div className="position-relative">
                          <Form.Control
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Ingresa tu contraseña"
                            name="password"
                            value={values.password}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            isInvalid={touched.password && !!errors.password}
                            disabled={isSubmitting}
                          />
                          <Button
                            variant="link"
                            className="position-absolute end-0 top-0 text-muted"
                            style={{ zIndex: 10 }}
                            onClick={() => setShowPassword(!showPassword)}
                            tabIndex={-1}
                            type="button"
                          >
                            <i className={`bi bi-eye${showPassword ? '-slash' : ''}`}></i>
                          </Button>
                          <Form.Control.Feedback type="invalid">
                            {errors.password}
                          </Form.Control.Feedback>
                        </div>
                      </Form.Group>

                      {/* Remember Me */}
                      <Form.Group className="mb-3" controlId="rememberMe">
                        <Form.Check
                          type="checkbox"
                          label="Recordar sesión"
                          disabled={isSubmitting}
                        />
                      </Form.Group>

                      {/* Submit Button */}
                      <Button
                        variant="primary"
                        type="submit"
                        className="w-100"
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? (
                          <>
                            <Spinner
                              as="span"
                              animation="border"
                              size="sm"
                              role="status"
                              aria-hidden="true"
                              className="me-2"
                            />
                            Iniciando sesión...
                          </>
                        ) : (
                          'Iniciar sesión'
                        )}
                      </Button>
                    </Form>
                  )}
                </Formik>

                {/* Footer */}
                <div className="text-center mt-4">
                  <small className="text-muted">
                    © 2024 OSE Platform 1.0 - Oversun Energy
                  </small>
                </div>

                {/* Dev Credentials Info */}
                {import.meta.env.DEV && (
                  <div className="mt-3 p-2 bg-light border rounded">
                    <small className="text-muted d-block mb-1"><strong>Credenciales de prueba:</strong></small>
                    <small className="text-muted d-block">Email: ppelaez@oversunenergy.com</small>
                    <small className="text-muted d-block">Password: bb474edf</small>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  )
}
