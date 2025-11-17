/**
 * Invoice Preview Modal Component
 * Modal para ver detalles de una factura
 */

import { Modal, Button, Table, Row, Col, Badge } from 'react-bootstrap'
import type { Invoice } from '../../types/invoice'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface InvoicePreviewModalProps {
  show: boolean
  invoice: Invoice
  onHide: () => void
}

export default function InvoicePreviewModal({ show, invoice, onHide }: InvoicePreviewModalProps) {
  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      draft: 'secondary',
      issued: 'primary',
      sent: 'info',
      paid: 'success',
      cancelled: 'danger'
    }
    const labels: Record<string, string> = {
      draft: 'Borrador',
      issued: 'Emitida',
      sent: 'Enviada',
      paid: 'Pagada',
      cancelled: 'Cancelada'
    }
    return <Badge bg={variants[status] || 'secondary'}>{labels[status] || status}</Badge>
  }

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton className="bg-success text-white">
        <Modal.Title>
          <i className="bi bi-file-earmark-text me-2"></i>
          Factura: {invoice.invoice_number}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {/* Header Info */}
        <Row className="mb-4">
          <Col md={6}>
            <h6 className="text-muted mb-2">DATOS DEL CLIENTE</h6>
            <div className="mb-2">
              <strong>{invoice.customer_name || 'Sin nombre'}</strong>
            </div>
            <div className="mb-1">
              <small className="text-muted">Email:</small>{' '}
              {invoice.customer_email}
            </div>
            {invoice.customer_nif && (
              <div className="mb-1">
                <small className="text-muted">NIF:</small>{' '}
                {invoice.customer_nif}
              </div>
            )}
            {invoice.customer_address && (
              <div className="mb-1">
                <small className="text-muted">Dirección:</small>{' '}
                {invoice.customer_address}
              </div>
            )}
          </Col>
          <Col md={6}>
            <h6 className="text-muted mb-2">DATOS DE LA FACTURA</h6>
            <div className="mb-1">
              <small className="text-muted">Número:</small>{' '}
              <strong>{invoice.invoice_number}</strong>
            </div>
            <div className="mb-1">
              <small className="text-muted">Fecha Emisión:</small>{' '}
              {format(new Date(invoice.issue_date), 'dd/MM/yyyy', { locale: es })}
            </div>
            {invoice.due_date && (
              <div className="mb-1">
                <small className="text-muted">Fecha Vencimiento:</small>{' '}
                {format(new Date(invoice.due_date), 'dd/MM/yyyy', { locale: es })}
              </div>
            )}
            <div className="mb-1">
              <small className="text-muted">Estado:</small>{' '}
              {getStatusBadge(invoice.status)}
            </div>
          </Col>
        </Row>

        {/* Items Table */}
        <h6 className="text-muted mb-2">CONCEPTOS</h6>
        <Table bordered size="sm" className="mb-3">
          <thead className="bg-light">
            <tr>
              <th>Descripción</th>
              <th className="text-center">Cantidad</th>
              <th className="text-end">Precio Unit.</th>
              <th className="text-end">Total</th>
            </tr>
          </thead>
          <tbody>
            {invoice.items.map((item, index) => (
              <tr key={index}>
                <td>{item.description}</td>
                <td className="text-center">{item.quantity}</td>
                <td className="text-end">{item.unit_price.toFixed(2)} €</td>
                <td className="text-end"><strong>{item.total.toFixed(2)} €</strong></td>
              </tr>
            ))}
          </tbody>
        </Table>

        {/* Totals */}
        <Row className="mb-3">
          <Col md={{ span: 6, offset: 6 }}>
            <Table size="sm" className="mb-0">
              <tbody>
                <tr>
                  <td className="text-end">Subtotal:</td>
                  <td className="text-end"><strong>{invoice.subtotal.toFixed(2)} €</strong></td>
                </tr>
                <tr>
                  <td className="text-end">IVA ({(invoice.tax_rate * 100).toFixed(0)}%):</td>
                  <td className="text-end"><strong>{invoice.tax_amount.toFixed(2)} €</strong></td>
                </tr>
                <tr className="table-primary">
                  <td className="text-end"><strong>TOTAL:</strong></td>
                  <td className="text-end"><h5 className="mb-0">{invoice.total.toFixed(2)} €</h5></td>
                </tr>
              </tbody>
            </Table>
          </Col>
        </Row>

        {/* Notes */}
        {invoice.notes && (
          <div className="mb-3">
            <h6 className="text-muted mb-2">NOTAS</h6>
            <div className="bg-light p-3 rounded">
              {invoice.notes}
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div className="border-top pt-3 mt-3">
          <Row>
            <Col md={6}>
              <small className="text-muted">
                <strong>Creada:</strong>{' '}
                {format(new Date(invoice.created_at), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}
              </small>
            </Col>
            {invoice.sent_at && (
              <Col md={6}>
                <small className="text-muted">
                  <strong>Enviada:</strong>{' '}
                  {format(new Date(invoice.sent_at), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}
                </small>
              </Col>
            )}
          </Row>
          {invoice.paid_at && (
            <Row className="mt-2">
              <Col md={6}>
                <small className="text-muted">
                  <strong>Pagada:</strong>{' '}
                  {format(new Date(invoice.paid_at), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}
                </small>
              </Col>
            </Row>
          )}
          {invoice.cancelled_at && (
            <Row className="mt-2">
              <Col md={12}>
                <small className="text-danger">
                  <strong>Cancelada:</strong>{' '}
                  {format(new Date(invoice.cancelled_at), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}
                </small>
              </Col>
            </Row>
          )}
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cerrar
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
