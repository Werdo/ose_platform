import React from 'react';
import { Card, Table, Badge, Form } from 'react-bootstrap';
import type { Ticket } from '../services/api';

interface TicketListProps {
  tickets: Ticket[];
  selectedTickets: number[];
  onSelectionChange: (ticketIds: number[]) => void;
}

const TicketList: React.FC<TicketListProps> = ({
  tickets,
  selectedTickets,
  onSelectionChange,
}) => {
  const handleToggleTicket = (ticketId: number) => {
    if (selectedTickets.includes(ticketId)) {
      onSelectionChange(selectedTickets.filter((id) => id !== ticketId));
    } else {
      onSelectionChange([...selectedTickets, ticketId]);
    }
  };

  const handleToggleAll = () => {
    const pendingTickets = tickets
      .filter((t) => t.status === 'pending')
      .map((t) => t.id);

    if (selectedTickets.length === pendingTickets.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(pendingTickets);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge bg="warning" text="dark">Pendiente</Badge>;
      case 'invoiced':
        return <Badge bg="success">Facturado</Badge>;
      case 'rejected':
        return <Badge bg="danger">Rechazado</Badge>;
      default:
        return <Badge bg="secondary">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
  };

  const pendingTickets = tickets.filter((t) => t.status === 'pending');
  const allPendingSelected =
    pendingTickets.length > 0 &&
    selectedTickets.length === pendingTickets.length;

  return (
    <Card>
      <Card.Body>
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 className="mb-0">Mis Tickets</h5>
          <Badge bg="secondary">{tickets.length} tickets</Badge>
        </div>

        {tickets.length === 0 ? (
          <div className="text-center py-5 text-muted">
            <i className="bi bi-inbox fs-1 d-block mb-3"></i>
            <p>No tienes tickets registrados</p>
          </div>
        ) : (
          <div className="table-responsive">
            <Table hover>
              <thead className="table-light">
                <tr>
                  <th style={{ width: '50px' }}>
                    {pendingTickets.length > 0 && (
                      <Form.Check
                        type="checkbox"
                        checked={allPendingSelected}
                        onChange={handleToggleAll}
                      />
                    )}
                  </th>
                  <th>Número</th>
                  <th>Fecha</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Productos</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>
                      {ticket.status === 'pending' && (
                        <Form.Check
                          type="checkbox"
                          checked={selectedTickets.includes(ticket.id)}
                          onChange={() => handleToggleTicket(ticket.id)}
                        />
                      )}
                    </td>
                    <td>
                      <strong>{ticket.ticket_number}</strong>
                      {ticket.image_url && (
                        <i className="bi bi-image ms-2 text-muted" title="Con imagen"></i>
                      )}
                    </td>
                    <td>{formatDate(ticket.date)}</td>
                    <td>
                      <strong>{ticket.total.toFixed(2)} €</strong>
                    </td>
                    <td>{getStatusBadge(ticket.status)}</td>
                    <td>
                      <small className="text-muted">
                        {ticket.items.length} producto(s)
                      </small>
                    </td>
                  </tr>
                ))}
              </tbody>
              {selectedTickets.length > 0 && (
                <tfoot className="table-light fw-bold">
                  <tr>
                    <td colSpan={3} className="text-end">
                      Total Seleccionados ({selectedTickets.length}):
                    </td>
                    <td colSpan={3}>
                      {tickets
                        .filter((t) => selectedTickets.includes(t.id))
                        .reduce((sum, t) => sum + t.total, 0)
                        .toFixed(2)}{' '}
                      €
                    </td>
                  </tr>
                </tfoot>
              )}
            </Table>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default TicketList;
