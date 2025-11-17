import React, { useState } from 'react';
import { Container, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleViewTickets = () => {
    if (!email.trim()) {
      setError('Por favor, ingresa tu email');
      return;
    }

    if (!validateEmail(email)) {
      setError('Por favor, ingresa un email válido');
      return;
    }

    setError('');
    navigate(`/my-tickets?email=${encodeURIComponent(email)}`);
  };

  const handleUploadTicket = () => {
    if (!email.trim()) {
      setError('Por favor, ingresa tu email');
      return;
    }

    if (!validateEmail(email)) {
      setError('Por favor, ingresa un email válido');
      return;
    }

    setError('');
    navigate(`/upload-ticket?email=${encodeURIComponent(email)}`);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleViewTickets();
    }
  };

  return (
    <div className="min-vh-100 bg-light d-flex align-items-center">
      <Container>
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            <div className="text-center mb-5">
              <div className="mb-4">
                <i className="bi bi-receipt-cutoff" style={{ fontSize: '4rem', color: '#0d6efd' }}></i>
              </div>
              <h1 className="display-5 fw-bold mb-3">Portal de Facturación</h1>
              <p className="lead text-muted">
                Gestiona tus tickets y genera facturas de manera sencilla
              </p>
            </div>

            <Card className="shadow-sm">
              <Card.Body className="p-4">
                <h5 className="mb-4">Acceso al Portal</h5>

                <Form>
                  <Form.Group className="mb-3">
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      placeholder="tu@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onKeyPress={handleKeyPress}
                      size="lg"
                      autoFocus
                    />
                    <Form.Text className="text-muted">
                      No necesitas registrarte, solo tu email para acceder
                    </Form.Text>
                  </Form.Group>

                  {error && (
                    <Alert variant="danger" className="mb-3">
                      <i className="bi bi-exclamation-triangle me-2"></i>
                      {error}
                    </Alert>
                  )}

                  <div className="d-grid gap-2">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={handleViewTickets}
                    >
                      <i className="bi bi-list-ul me-2"></i>
                      Ver Mis Tickets
                    </Button>

                    <Button
                      variant="outline-primary"
                      size="lg"
                      onClick={handleUploadTicket}
                    >
                      <i className="bi bi-cloud-upload me-2"></i>
                      Subir Nuevo Ticket
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>

            <div className="text-center mt-4">
              <div className="row g-3">
                <div className="col-md-4">
                  <div className="p-3">
                    <i className="bi bi-cloud-upload fs-2 text-primary d-block mb-2"></i>
                    <h6>Sube Tickets</h6>
                    <small className="text-muted">Escaneo automático con OCR</small>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="p-3">
                    <i className="bi bi-receipt fs-2 text-primary d-block mb-2"></i>
                    <h6>Gestiona</h6>
                    <small className="text-muted">Organiza tus tickets</small>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="p-3">
                    <i className="bi bi-file-earmark-pdf fs-2 text-primary d-block mb-2"></i>
                    <h6>Genera Facturas</h6>
                    <small className="text-muted">Descarga en PDF</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default HomePage;
