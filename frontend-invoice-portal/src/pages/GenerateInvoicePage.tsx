import React, { useState, useEffect } from 'react';
import { Container, Button, Alert, Spinner, Card, Form } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';
import InvoicePreview from '../components/InvoicePreview';
import { getTicketsByEmail, createInvoice, downloadInvoicePDF } from '../services/api';
import type { Ticket } from '../services/api';

const GenerateInvoicePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const email = searchParams.get('email') || '';
  const ticketIds = searchParams.get('tickets')?.split(',').map(Number) || [];

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [billingName, setBillingName] = useState('');
  const [billingNif, setBillingNif] = useState('');
  const [billingAddress, setBillingAddress] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!email || ticketIds.length === 0) {
      navigate('/');
      return;
    }

    loadTickets();
  }, [email, navigate]);

  const loadTickets = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const allTickets = await getTicketsByEmail(email);
      const selectedTickets = allTickets.filter(t => ticketIds.includes(t.id));

      if (selectedTickets.length === 0) {
        setError('No se encontraron los tickets seleccionados');
        return;
      }

      setTickets(selectedTickets);

      // Pre-fill billing data from first ticket with billing info
      const ticketWithBilling = selectedTickets.find(
        t => t.billing_name || t.billing_nif || t.billing_address
      );

      if (ticketWithBilling) {
        setBillingName(ticketWithBilling.billing_name || '');
        setBillingNif(ticketWithBilling.billing_nif || '');
        setBillingAddress(ticketWithBilling.billing_address || '');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar los tickets. Por favor, intenta de nuevo.');
      console.error('Error loading tickets:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    if (!billingName.trim()) {
      setError('El nombre o razón social es obligatorio');
      return false;
    }

    if (!billingNif.trim()) {
      setError('El NIF/CIF es obligatorio');
      return false;
    }

    if (!billingAddress.trim()) {
      setError('La dirección es obligatoria');
      return false;
    }

    return true;
  };

  const handleGenerateInvoice = async () => {
    if (!validateForm()) {
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Create invoice
      const invoice = await createInvoice({
        email,
        ticket_ids: ticketIds,
        billing_name: billingName,
        billing_nif: billingNif,
        billing_address: billingAddress,
      });

      // Download PDF
      const pdfBlob = await downloadInvoicePDF(invoice.id);
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `factura-${invoice.invoice_number}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(true);

      // Redirect after 3 seconds
      setTimeout(() => {
        navigate(`/my-tickets?email=${encodeURIComponent(email)}`);
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al generar la factura. Por favor, intenta de nuevo.');
      console.error('Error generating invoice:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBack = () => {
    navigate(`/my-tickets?email=${encodeURIComponent(email)}`);
  };

  const calculateTotal = () => {
    return tickets.reduce((sum, ticket) => sum + ticket.total, 0);
  };

  return (
    <div className="min-vh-100 bg-light py-4">
      <Container>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i className="bi bi-file-earmark-pdf me-2"></i>
              Generar Factura
            </h2>
            <p className="text-muted mb-0">Email: {email}</p>
          </div>
          <Button variant="outline-secondary" onClick={handleBack} disabled={isGenerating}>
            <i className="bi bi-arrow-left me-2"></i>
            Volver
          </Button>
        </div>

        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success">
            <i className="bi bi-check-circle me-2"></i>
            Factura generada exitosamente y descargada. Redirigiendo...
          </Alert>
        )}

        {isLoading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status" variant="primary">
              <span className="visually-hidden">Cargando...</span>
            </Spinner>
            <p className="text-muted mt-3">Cargando datos...</p>
          </div>
        ) : (
          <div className="row">
            <div className="col-lg-8 mb-4">
              <InvoicePreview
                tickets={tickets}
                billingName={billingName}
                billingNif={billingNif}
                billingAddress={billingAddress}
              />
            </div>

            <div className="col-lg-4">
              <Card className="mb-4 sticky-top" style={{ top: '20px' }}>
                <Card.Body>
                  <h5 className="mb-3">Datos de Facturación</h5>

                  <Form>
                    <Form.Group className="mb-3">
                      <Form.Label>Nombre / Razón Social *</Form.Label>
                      <Form.Control
                        type="text"
                        value={billingName}
                        onChange={(e) => setBillingName(e.target.value)}
                        placeholder="Nombre completo o razón social"
                        required
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>NIF / CIF *</Form.Label>
                      <Form.Control
                        type="text"
                        value={billingNif}
                        onChange={(e) => setBillingNif(e.target.value)}
                        placeholder="12345678A o B12345678"
                        required
                      />
                    </Form.Group>

                    <Form.Group className="mb-4">
                      <Form.Label>Dirección Completa *</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        value={billingAddress}
                        onChange={(e) => setBillingAddress(e.target.value)}
                        placeholder="Calle, número, código postal, ciudad"
                        required
                      />
                    </Form.Group>

                    <div className="border-top pt-3 mb-3">
                      <div className="d-flex justify-content-between mb-2">
                        <span className="text-muted">Tickets seleccionados:</span>
                        <strong>{tickets.length}</strong>
                      </div>
                      <div className="d-flex justify-content-between">
                        <span className="text-muted">Total:</span>
                        <strong className="fs-4 text-primary">
                          {calculateTotal().toFixed(2)} €
                        </strong>
                      </div>
                    </div>

                    <div className="d-grid">
                      <Button
                        variant="success"
                        size="lg"
                        onClick={handleGenerateInvoice}
                        disabled={isGenerating || success}
                      >
                        {isGenerating ? (
                          <>
                            <Spinner
                              as="span"
                              animation="border"
                              size="sm"
                              role="status"
                              className="me-2"
                            />
                            Generando...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-file-earmark-pdf me-2"></i>
                            Generar Factura PDF
                          </>
                        )}
                      </Button>
                    </div>
                  </Form>
                </Card.Body>
              </Card>
            </div>
          </div>
        )}
      </Container>
    </div>
  );
};

export default GenerateInvoicePage;
