import React, { useState, useEffect } from 'react';
import { Container, Button, Alert, Spinner } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';
import TicketList from '../components/TicketList';
import { getTicketsByEmail } from '../services/api';
import type { Ticket } from '../services/api';

const MyTicketsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const email = searchParams.get('email') || '';

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTickets, setSelectedTickets] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!email) {
      navigate('/');
      return;
    }

    loadTickets();
  }, [email, navigate]);

  const loadTickets = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getTicketsByEmail(email);
      setTickets(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar los tickets. Por favor, intenta de nuevo.');
      console.error('Error loading tickets:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadTicket = () => {
    navigate(`/upload-ticket?email=${encodeURIComponent(email)}`);
  };

  const handleGenerateInvoice = () => {
    if (selectedTickets.length === 0) {
      setError('Por favor, selecciona al menos un ticket');
      return;
    }

    navigate(`/generate-invoice?email=${encodeURIComponent(email)}&tickets=${selectedTickets.join(',')}`);
  };

  const handleBack = () => {
    navigate('/');
  };

  const pendingTicketsCount = tickets.filter(t => t.status === 'pending').length;

  return (
    <div className="min-vh-100 bg-light py-4">
      <Container>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i className="bi bi-list-ul me-2"></i>
              Mis Tickets
            </h2>
            <p className="text-muted mb-0">Email: {email}</p>
          </div>
          <div className="d-flex gap-2">
            <Button variant="outline-secondary" onClick={handleBack}>
              <i className="bi bi-arrow-left me-2"></i>
              Volver
            </Button>
            <Button variant="primary" onClick={handleUploadTicket}>
              <i className="bi bi-plus-circle me-2"></i>
              Nuevo Ticket
            </Button>
          </div>
        </div>

        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </Alert>
        )}

        {isLoading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status" variant="primary">
              <span className="visually-hidden">Cargando...</span>
            </Spinner>
            <p className="text-muted mt-3">Cargando tickets...</p>
          </div>
        ) : (
          <>
            <TicketList
              tickets={tickets}
              selectedTickets={selectedTickets}
              onSelectionChange={setSelectedTickets}
            />

            {pendingTicketsCount > 0 && (
              <div className="mt-4 d-flex justify-content-end">
                <Button
                  variant="success"
                  size="lg"
                  onClick={handleGenerateInvoice}
                  disabled={selectedTickets.length === 0}
                >
                  <i className="bi bi-file-earmark-pdf me-2"></i>
                  Generar Factura
                  {selectedTickets.length > 0 && (
                    <span className="ms-2 badge bg-light text-dark">
                      {selectedTickets.length}
                    </span>
                  )}
                </Button>
              </div>
            )}

            {tickets.length > 0 && pendingTicketsCount === 0 && (
              <Alert variant="info" className="mt-4">
                <i className="bi bi-info-circle me-2"></i>
                No tienes tickets pendientes. Todos tus tickets ya han sido facturados o rechazados.
              </Alert>
            )}
          </>
        )}
      </Container>
    </div>
  );
};

export default MyTicketsPage;
