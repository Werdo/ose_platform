import React, { useState, useEffect } from 'react';
import { Container, Button, Alert, Spinner } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';
import TicketUpload from '../components/TicketUpload';
import TicketForm from '../components/TicketForm';
import BillingForm from '../components/BillingForm';
import { createTicket, uploadTicketImage } from '../services/api';
import type { OCRResult, TicketItem } from '../services/api';

const UploadTicketPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const email = searchParams.get('email') || '';

  const [scannedFile, setScannedFile] = useState<File | null>(null);
  const [ticketNumber, setTicketNumber] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [items, setItems] = useState<TicketItem[]>([]);
  const [total, setTotal] = useState(0);
  const [billingName, setBillingName] = useState('');
  const [billingNif, setBillingNif] = useState('');
  const [billingAddress, setBillingAddress] = useState('');

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!email) {
      navigate('/');
    }
  }, [email, navigate]);

  const handleScanComplete = (result: OCRResult, file: File) => {
    setScannedFile(file);

    if (result.ticket_number) {
      setTicketNumber(result.ticket_number);
    }

    if (result.date) {
      setDate(result.date);
    }

    if (result.items && result.items.length > 0) {
      setItems(result.items);
      setTotal(result.total || result.items.reduce((sum, item) => sum + item.total, 0));
    }

    setError(null);
  };

  const handleTicketFormChange = (data: {
    ticketNumber: string;
    date: string;
    items: TicketItem[];
    total: number;
  }) => {
    setTicketNumber(data.ticketNumber);
    setDate(data.date);
    setItems(data.items);
    setTotal(data.total);
  };

  const handleBillingFormChange = (data: {
    billingName: string;
    billingNif: string;
    billingAddress: string;
  }) => {
    setBillingName(data.billingName);
    setBillingNif(data.billingNif);
    setBillingAddress(data.billingAddress);
  };

  const validateForm = () => {
    if (!ticketNumber.trim()) {
      setError('El número de ticket es obligatorio');
      return false;
    }

    if (!date) {
      setError('La fecha es obligatoria');
      return false;
    }

    if (items.length === 0 || items.every(item => !item.description.trim())) {
      setError('Debes agregar al menos un producto');
      return false;
    }

    if (total <= 0) {
      setError('El total debe ser mayor a 0');
      return false;
    }

    return true;
  };

  const handleSaveTicket = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      // Create ticket
      const newTicket = await createTicket({
        email,
        ticket_number: ticketNumber,
        date,
        total,
        items: items.filter(item => item.description.trim()),
        billing_name: billingName || undefined,
        billing_nif: billingNif || undefined,
        billing_address: billingAddress || undefined,
      });

      // Upload image if available
      if (scannedFile) {
        await uploadTicketImage(newTicket.id, scannedFile);
      }

      setSuccess(true);

      // Redirect after 2 seconds
      setTimeout(() => {
        navigate(`/my-tickets?email=${encodeURIComponent(email)}`);
      }, 2000);
    } catch (err: any) {
      // Handle validation errors (422)
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const validationErrors = err.response.data.detail
          .map((error: any) => error.msg || JSON.stringify(error))
          .join(', ');
        setError(`Error de validación: ${validationErrors}`);
      } else {
        setError(err.response?.data?.detail || 'Error al guardar el ticket. Por favor, intenta de nuevo.');
      }
      console.error('Error saving ticket:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    navigate(`/my-tickets?email=${encodeURIComponent(email)}`);
  };

  return (
    <div className="min-vh-100 bg-light py-4">
      <Container>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i className="bi bi-cloud-upload me-2"></i>
              Subir Nuevo Ticket
            </h2>
            <p className="text-muted mb-0">Email: {email}</p>
          </div>
          <Button variant="outline-secondary" onClick={handleCancel}>
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
            Ticket guardado exitosamente. Redirigiendo...
          </Alert>
        )}

        <TicketUpload onScanComplete={handleScanComplete} />

        <TicketForm
          ticketNumber={ticketNumber}
          date={date}
          items={items}
          total={total}
          onChange={handleTicketFormChange}
        />

        <BillingForm
          billingName={billingName}
          billingNif={billingNif}
          billingAddress={billingAddress}
          onChange={handleBillingFormChange}
        />

        <div className="d-flex gap-2 justify-content-end">
          <Button variant="outline-secondary" onClick={handleCancel} disabled={isSaving}>
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleSaveTicket}
            disabled={isSaving || success}
          >
            {isSaving ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  className="me-2"
                />
                Guardando...
              </>
            ) : (
              <>
                <i className="bi bi-check-circle me-2"></i>
                Guardar Ticket
              </>
            )}
          </Button>
        </div>
      </Container>
    </div>
  );
};

export default UploadTicketPage;
