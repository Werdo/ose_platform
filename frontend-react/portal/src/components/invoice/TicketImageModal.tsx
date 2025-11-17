/**
 * Ticket Image Modal Component
 * Modal para ver la imagen del ticket
 */

import { Modal, Button } from 'react-bootstrap'
import type { Ticket } from '../../types/invoice'

interface TicketImageModalProps {
  show: boolean
  ticket: Ticket
  onHide: () => void
}

export default function TicketImageModal({ show, ticket, onHide }: TicketImageModalProps) {
  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton className="bg-info text-white">
        <Modal.Title>
          <i className="bi bi-image me-2"></i>
          Imagen del Ticket: {ticket.ticket_number}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body className="text-center">
        {ticket.image_url ? (
          <img
            src={ticket.image_url}
            alt={`Ticket ${ticket.ticket_number}`}
            style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain' }}
          />
        ) : (
          <div className="py-5">
            <i className="bi bi-image" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
            <p className="text-muted mt-3">No hay imagen disponible</p>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cerrar
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
