/**
 * Invoice Table Component
 * Muestra y gestiona las facturas generadas
 */

import { useState, useEffect } from 'react'
import { Card, Table, Button, Form, Badge, Spinner, Alert, Row, Col } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import toast from 'react-hot-toast'
import type { Invoice, InvoiceFilters } from '../../types/invoice'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import InvoicePreviewModal from './InvoicePreviewModal'

interface InvoiceTableProps {
  onDataChange: () => void
}

export default function InvoiceTable({ onDataChange }: InvoiceTableProps) {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<InvoiceFilters>({})
  const [showFilters, setShowFilters] = useState(false)
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [showPreviewModal, setShowPreviewModal] = useState(false)

  useEffect(() => {
    loadInvoices()
  }, [filters])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.customer) params.append('customer', filters.customer)
      if (filters.date_from) params.append('date_from', filters.date_from)
      if (filters.date_to) params.append('date_to', filters.date_to)
      if (filters.search) params.append('search', filters.search)

      const response = await apiService.get(`/api/app5/invoices?${params.toString()}`)
      setInvoices(response.invoices || [])
    } catch (error: any) {
      toast.error('Error cargando facturas')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleViewPDF = async (invoiceId: string) => {
    try {
      const response = await apiService.get(`/api/app5/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      })
      const blob = new Blob([response], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
    } catch (error: any) {
      toast.error('Error generando PDF')
    }
  }

  const handleRegenerate = async (invoiceId: string) => {
    if (!window.confirm('¿Regenerar esta factura?')) return

    try {
      await apiService.post(`/api/app5/invoices/${invoiceId}/regenerate`)
      toast.success('Factura regenerada')
      loadInvoices()
      onDataChange()
    } catch (error: any) {
      toast.error('Error regenerando factura')
    }
  }

  const handleSendEmail = async (invoiceId: string) => {
    if (!window.confirm('¿Enviar esta factura por email al cliente?')) return

    try {
      await apiService.post(`/api/app5/invoices/${invoiceId}/send-email`)
      toast.success('Factura enviada por email')
      loadInvoices()
      onDataChange()
    } catch (error: any) {
      toast.error('Error enviando email')
    }
  }

  const handleCancel = async (invoiceId: string) => {
    const reason = prompt('Motivo de cancelación:')
    if (!reason) return

    try {
      await apiService.post(`/api/app5/invoices/${invoiceId}/cancel`, { reason })
      toast.success('Factura cancelada')
      loadInvoices()
      onDataChange()
    } catch (error: any) {
      toast.error('Error cancelando factura')
    }
  }

  const handlePreview = (invoice: Invoice) => {
    setSelectedInvoice(invoice)
    setShowPreviewModal(true)
  }

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

  const handleFilterChange = (key: keyof InvoiceFilters, value: string) => {
    setFilters({ ...filters, [key]: value || undefined })
  }

  const handleResetFilters = () => {
    setFilters({})
  }

  return (
    <>
      <Card className="border-0 shadow-sm mb-3">
        <Card.Header className="bg-white border-bottom">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">
              <i className="bi bi-file-earmark-text me-2"></i>
              Facturas Generadas
            </h5>
            <Button
              variant="outline-primary"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <i className={`bi bi-funnel${showFilters ? '-fill' : ''} me-1`}></i>
              Filtros
            </Button>
          </div>
        </Card.Header>

        {showFilters && (
          <Card.Body className="bg-light border-bottom">
            <Row className="g-3">
              <Col md={3}>
                <Form.Label>Estado</Form.Label>
                <Form.Select
                  size="sm"
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <option value="">Todos</option>
                  <option value="draft">Borrador</option>
                  <option value="issued">Emitida</option>
                  <option value="sent">Enviada</option>
                  <option value="paid">Pagada</option>
                  <option value="cancelled">Cancelada</option>
                </Form.Select>
              </Col>
              <Col md={3}>
                <Form.Label>Cliente</Form.Label>
                <Form.Control
                  size="sm"
                  type="text"
                  placeholder="Nombre o email"
                  value={filters.customer || ''}
                  onChange={(e) => handleFilterChange('customer', e.target.value)}
                />
              </Col>
              <Col md={3}>
                <Form.Label>Desde</Form.Label>
                <Form.Control
                  size="sm"
                  type="date"
                  value={filters.date_from || ''}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                />
              </Col>
              <Col md={3}>
                <Form.Label>Hasta</Form.Label>
                <Form.Control
                  size="sm"
                  type="date"
                  value={filters.date_to || ''}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                />
              </Col>
              <Col md={12}>
                <Form.Label>Buscar</Form.Label>
                <Form.Control
                  size="sm"
                  type="text"
                  placeholder="Número de factura..."
                  value={filters.search || ''}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </Col>
              <Col xs={12}>
                <Button variant="outline-secondary" size="sm" onClick={handleResetFilters}>
                  <i className="bi bi-x-circle me-1"></i>
                  Limpiar Filtros
                </Button>
              </Col>
            </Row>
          </Card.Body>
        )}

        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 text-muted">Cargando facturas...</p>
            </div>
          ) : invoices.length === 0 ? (
            <Alert variant="info" className="m-4">
              <i className="bi bi-info-circle me-2"></i>
              No se encontraron facturas
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Número</th>
                    <th>Cliente</th>
                    <th>Fecha</th>
                    <th>Total</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map((invoice) => (
                    <tr key={invoice.id}>
                      <td>
                        <strong>{invoice.invoice_number}</strong>
                      </td>
                      <td>
                        <div>{invoice.customer_name || invoice.customer_email}</div>
                        <small className="text-muted">{invoice.customer_email}</small>
                      </td>
                      <td>
                        <small>
                          {format(new Date(invoice.issue_date), 'dd/MM/yyyy', { locale: es })}
                        </small>
                      </td>
                      <td>
                        <strong>{invoice.total.toFixed(2)} €</strong>
                      </td>
                      <td>{getStatusBadge(invoice.status)}</td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handlePreview(invoice)}
                            title="Ver detalles"
                          >
                            <i className="bi bi-eye"></i>
                          </Button>
                          <Button
                            variant="outline-success"
                            size="sm"
                            onClick={() => handleViewPDF(invoice.id)}
                            title="Ver PDF"
                          >
                            <i className="bi bi-file-pdf"></i>
                          </Button>
                          {invoice.status !== 'cancelled' && (
                            <>
                              <Button
                                variant="outline-info"
                                size="sm"
                                onClick={() => handleRegenerate(invoice.id)}
                                title="Regenerar"
                              >
                                <i className="bi bi-arrow-clockwise"></i>
                              </Button>
                              <Button
                                variant="outline-primary"
                                size="sm"
                                onClick={() => handleSendEmail(invoice.id)}
                                title="Enviar email"
                              >
                                <i className="bi bi-envelope"></i>
                              </Button>
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => handleCancel(invoice.id)}
                                title="Cancelar"
                              >
                                <i className="bi bi-x-circle"></i>
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>

      {selectedInvoice && (
        <InvoicePreviewModal
          show={showPreviewModal}
          invoice={selectedInvoice}
          onHide={() => setShowPreviewModal(false)}
        />
      )}
    </>
  )
}
