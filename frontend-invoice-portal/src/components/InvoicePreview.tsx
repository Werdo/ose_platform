import React from 'react';
import { Card, Table, Alert } from 'react-bootstrap';
import type { Ticket } from '../services/api';

interface InvoicePreviewProps {
  tickets: Ticket[];
  billingName: string;
  billingNif: string;
  billingAddress: string;
}

const InvoicePreview: React.FC<InvoicePreviewProps> = ({
  tickets,
  billingName,
  billingNif,
  billingAddress,
}) => {
  const calculateTotal = () => {
    return tickets.reduce((sum, ticket) => sum + ticket.total, 0);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
  };

  if (tickets.length === 0) {
    return (
      <Alert variant="info">
        <i className="bi bi-info-circle me-2"></i>
        Selecciona tickets para ver la previsualización de la factura
      </Alert>
    );
  }

  return (
    <Card>
      <Card.Body>
        <h5 className="mb-4">Previsualización de Factura</h5>

        <div className="mb-4">
          <h6 className="text-muted mb-2">Datos de Facturación</h6>
          <div className="border rounded p-3 bg-light">
            <p className="mb-1">
              <strong>Nombre:</strong> {billingName || <span className="text-muted">No especificado</span>}
            </p>
            <p className="mb-1">
              <strong>NIF/CIF:</strong> {billingNif || <span className="text-muted">No especificado</span>}
            </p>
            <p className="mb-0">
              <strong>Dirección:</strong> {billingAddress || <span className="text-muted">No especificada</span>}
            </p>
          </div>
        </div>

        <div className="mb-4">
          <h6 className="text-muted mb-2">Tickets Incluidos</h6>
          <div className="table-responsive">
            <Table bordered hover size="sm">
              <thead className="table-light">
                <tr>
                  <th>Número</th>
                  <th>Fecha</th>
                  <th>Productos</th>
                  <th className="text-end">Total</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => (
                  <React.Fragment key={ticket.id}>
                    <tr className="table-light fw-bold">
                      <td>{ticket.ticket_number}</td>
                      <td>{formatDate(ticket.date)}</td>
                      <td>{ticket.items.length} producto(s)</td>
                      <td className="text-end">{ticket.total.toFixed(2)} €</td>
                    </tr>
                    {ticket.items.map((item, idx) => (
                      <tr key={`${ticket.id}-${idx}`}>
                        <td colSpan={2} className="ps-4">
                          <small>{item.description}</small>
                        </td>
                        <td>
                          <small>
                            {item.quantity} x {item.unit_price.toFixed(2)} €
                          </small>
                        </td>
                        <td className="text-end">
                          <small>{item.total.toFixed(2)} €</small>
                        </td>
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
              <tfoot>
                <tr className="table-light fw-bold">
                  <td colSpan={3} className="text-end">TOTAL FACTURA:</td>
                  <td className="text-end fs-5">{calculateTotal().toFixed(2)} €</td>
                </tr>
              </tfoot>
            </Table>
          </div>
        </div>

        <Alert variant="info" className="mb-0">
          <small>
            <i className="bi bi-info-circle me-2"></i>
            Esta es una previsualización. La factura final se generará en formato PDF.
          </small>
        </Alert>
      </Card.Body>
    </Card>
  );
};

export default InvoicePreview;
