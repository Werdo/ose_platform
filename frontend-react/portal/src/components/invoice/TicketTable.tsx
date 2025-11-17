/**
 * Ticket Table Component
 * Muestra y gestiona los tickets subidos
 */

import { useState, useEffect } from 'react'
import { Card, Table, Button, Form, Badge, Spinner, Alert, Row, Col } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import toast from 'react-hot-toast'
import type { Ticket, TicketFilters } from '../../types/invoice'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import TicketEditModal from './TicketEditModal'
import TicketImageModal from './TicketImageModal'

interface TicketTableProps {
  onDataChange: () => void
}

export default function TicketTable({ onDataChange }: TicketTableProps) {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<TicketFilters>({})
  const [showFilters, setShowFilters] = useState(false)
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showImageModal, setShowImageModal] = useState(false)
  const [processing, setProcessing] = useState<string | null>(null)

  useEffect(() => {
    loadTickets()
  }, [filters])

  const loadTickets = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.email) params.append('email', filters.email)
      if (filters.date_from) params.append('date_from', filters.date_from)
      if (filters.date_to) params.append('date_to', filters.date_to)
      if (filters.search) params.append('search', filters.search)

      const response = await apiService.get(`/api/app5/tickets?${params.toString()}`)
      setTickets(response.tickets || [])
    } catch (error: any) {
      toast.error('Error cargando tickets')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleProcessOCR = async (ticketId: string) => {
    try {
      setProcessing(ticketId)
      await apiService.post(`/api/app5/tickets/${ticketId}/process-ocr`)
      toast.success('OCR procesado correctamente')
      loadTickets()
      onDataChange()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error procesando OCR')
    } finally {
      setProcessing(null)
    }
  }

  const handleDelete = async (ticketId: string) => {
    if (!window.confirm('¿Estás seguro de eliminar este ticket?')) return

    try {
      await apiService.delete(`/api/app5/tickets/${ticketId}`)
      toast.success('Ticket eliminado')
      loadTickets()
      onDataChange()
    } catch (error: any) {
      toast.error('Error eliminando ticket')
    }
  }

  const handleEdit = (ticket: Ticket) => {
    setSelectedTicket(ticket)
    setShowEditModal(true)
  }

  const handleViewImage = (ticket: Ticket) => {
    setSelectedTicket(ticket)
    setShowImageModal(true)
  }

  const handleEditComplete = () => {
    setShowEditModal(false)
    setSelectedTicket(null)
    loadTickets()
    onDataChange()
  }

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const email = prompt('Email del cliente:')
    if (!email) return

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('customer_email', email)

      await apiService.upload('/api/app5/tickets/upload', formData)
      toast.success('Ticket subido correctamente')
      loadTickets()
      onDataChange()
      event.target.value = ''
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error subiendo ticket')
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: 'warning',
      processed: 'info',
      invoiced: 'success',
      error: 'danger'
    }
    const labels: Record<string, string> = {
      pending: 'Pendiente',
      processed: 'Procesado',
      invoiced: 'Facturado',
      error: 'Error'
    }
    return <Badge bg={variants[status] || 'secondary'}>{labels[status] || status}</Badge>
  }

  const handleFilterChange = (key: keyof TicketFilters, value: string) => {
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
              <i className="bi bi-receipt me-2"></i>
              Tickets Subidos
            </h5>
            <div>
              <Button
                variant="outline-primary"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="me-2"
              >
                <i className={`bi bi-funnel${showFilters ? '-fill' : ''} me-1`}></i>
                Filtros
              </Button>
              <Button variant="primary" size="sm" as="label" htmlFor="ticket-upload">
                <i className="bi bi-cloud-upload me-1"></i>
                Subir Ticket
                <input
                  id="ticket-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleUpload}
                  style={{ display: 'none' }}
                />
              </Button>
            </div>
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
                  <option value="pending">Pendiente</option>
                  <option value="processed">Procesado</option>
                  <option value="invoiced">Facturado</option>
                  <option value="error">Error</option>
                </Form.Select>
              </Col>
              <Col md={3}>
                <Form.Label>Email</Form.Label>
                <Form.Control
                  size="sm"
                  type="text"
                  placeholder="Email del cliente"
                  value={filters.email || ''}
                  onChange={(e) => handleFilterChange('email', e.target.value)}
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
                  placeholder="Número de ticket..."
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
              <p className="mt-2 text-muted">Cargando tickets...</p>
            </div>
          ) : tickets.length === 0 ? (
            <Alert variant="info" className="m-4">
              <i className="bi bi-info-circle me-2"></i>
              No se encontraron tickets. Sube un ticket para comenzar.
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Número</th>
                    <th>Cliente</th>
                    <th>Fecha Subida</th>
                    <th>Estado</th>
                    <th>Total</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((ticket) => (
                    <tr key={ticket.id}>
                      <td>
                        <strong>{ticket.ticket_number}</strong>
                      </td>
                      <td>{ticket.customer_email}</td>
                      <td>
                        <small>
                          {format(new Date(ticket.upload_date), 'dd/MM/yyyy HH:mm', { locale: es })}
                        </small>
                      </td>
                      <td>{getStatusBadge(ticket.status)}</td>
                      <td>
                        {ticket.ocr_data?.total ? (
                          <strong>{ticket.ocr_data.total.toFixed(2)} €</strong>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          {ticket.image_url && (
                            <Button
                              variant="outline-info"
                              size="sm"
                              onClick={() => handleViewImage(ticket)}
                              title="Ver imagen"
                            >
                              <i className="bi bi-image"></i>
                            </Button>
                          )}
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleEdit(ticket)}
                            title="Editar"
                          >
                            <i className="bi bi-pencil"></i>
                          </Button>
                          {ticket.status === 'pending' && (
                            <Button
                              variant="outline-success"
                              size="sm"
                              onClick={() => handleProcessOCR(ticket.id)}
                              disabled={processing === ticket.id}
                              title="Procesar OCR"
                            >
                              {processing === ticket.id ? (
                                <Spinner animation="border" size="sm" />
                              ) : (
                                <i className="bi bi-cpu"></i>
                              )}
                            </Button>
                          )}
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleDelete(ticket.id)}
                            title="Eliminar"
                          >
                            <i className="bi bi-trash"></i>
                          </Button>
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

      {selectedTicket && (
        <>
          <TicketEditModal
            show={showEditModal}
            ticket={selectedTicket}
            onHide={() => setShowEditModal(false)}
            onComplete={handleEditComplete}
          />
          <TicketImageModal
            show={showImageModal}
            ticket={selectedTicket}
            onHide={() => setShowImageModal(false)}
          />
        </>
      )}
    </>
  )
}
