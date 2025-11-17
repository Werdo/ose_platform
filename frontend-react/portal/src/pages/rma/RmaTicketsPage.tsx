/**
 * App 3: RMA & Tickets Management Page
 * Sistema de gestión de incidencias y RMA
 */

import { useState, useEffect } from 'react'
import {
  Container, Row, Col, Card, Button, Badge, Table,
  Modal, Form, Tabs, Tab, Alert, InputGroup, Spinner
} from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import PublicUsersTab from './PublicUsersTab'
import RMAManagementTab from './RMAManagementTab'

interface Ticket {
  id: string
  ticket_number: string
  device_imei: string
  customer_name: string
  customer_email: string
  issue_type: string
  description: string
  status: string
  priority: string
  created_at: string
  messages_count: number
}

interface TicketDetails extends Ticket {
  messages: any[]
  resolution?: string
  assigned_to?: string
}

export default function RmaTicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showNewTicket, setShowNewTicket] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [selectedTicket, setSelectedTicket] = useState<TicketDetails | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [stats, setStats] = useState<any>(null)

  const [newTicketData, setNewTicketData] = useState({
    device_imei: '',
    customer_email: '',
    customer_name: '',
    issue_type: 'technical',
    description: '',
    priority: 'medium'
  })

  useEffect(() => {
    loadTickets()
    loadStats()
  }, [])

  const loadTickets = async () => {
    setLoading(true)
    try {
      const response = await apiService.get('/api/app3/tickets?limit=50')
      setTickets(response.tickets || [])
      setError(null)
    } catch (err: any) {
      setError('Error cargando tickets')
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await apiService.get('/api/app3/stats')
      setStats(response.stats)
    } catch (err) {
      console.error('Error cargando estadísticas:', err)
    }
  }

  const handleCreateTicket = async () => {
    try {
      await apiService.post('/api/app3/tickets', newTicketData)
      setShowNewTicket(false)
      setNewTicketData({
        device_imei: '',
        customer_email: '',
        customer_name: '',
        issue_type: 'technical',
        description: '',
        priority: 'medium'
      })
      loadTickets()
      loadStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creando ticket')
    }
  }

  const handleViewTicket = async (ticketId: string) => {
    try {
      const response = await apiService.get(`/api/app3/tickets/${ticketId}`)
      setSelectedTicket(response.ticket)
      setShowDetails(true)
    } catch (err: any) {
      setError('Error cargando detalles del ticket')
    }
  }

  const handleSendMessage = async () => {
    if (!selectedTicket || !newMessage.trim()) return

    try {
      await apiService.post(`/api/app3/tickets/${selectedTicket.id}/messages`, {
        message: newMessage
      })
      setNewMessage('')
      // Recargar detalles
      const response = await apiService.get(`/api/app3/tickets/${selectedTicket.id}`)
      setSelectedTicket(response.ticket)
    } catch (err: any) {
      setError('Error enviando mensaje')
    }
  }

  const handleUpdateStatus = async (status: string) => {
    if (!selectedTicket) return

    try {
      await apiService.patch(`/api/app3/tickets/${selectedTicket.id}`, { status })
      setShowDetails(false)
      loadTickets()
      loadStats()
    } catch (err: any) {
      setError('Error actualizando ticket')
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      open: 'primary',
      in_progress: 'info',
      closed: 'success',
      escalated: 'warning'
    }
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>
  }

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, string> = {
      low: 'secondary',
      medium: 'primary',
      high: 'warning',
      critical: 'danger'
    }
    return <Badge bg={variants[priority] || 'secondary'}>{priority}</Badge>
  }

  return (
    <Container fluid className="p-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-1">
            <i className="bi bi-ticket-perforated-fill me-2 text-warning"></i>
            App 3: RMA & Tickets
          </h4>
          <p className="text-muted mb-0">Gestión de incidencias, devoluciones y usuarios públicos</p>
        </div>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Tabs defaultActiveKey="tickets" className="mb-4">
        <Tab eventKey="tickets" title={<><i className="bi bi-ticket-perforated me-2"></i>Tickets</>}>
          {/* Tickets Tab Content */}
          <div className="d-flex justify-content-end mb-3">
            <Button variant="primary" onClick={() => setShowNewTicket(true)}>
              <i className="bi bi-plus-circle me-2"></i>
              Nuevo Ticket
            </Button>
          </div>

      {/* Stats Cards */}
      {stats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3>{stats.tickets.total}</h3>
                <small className="text-muted">Total Tickets</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-primary">
              <Card.Body>
                <h3 className="text-primary">{stats.tickets.open}</h3>
                <small className="text-muted">Abiertos</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-warning">
              <Card.Body>
                <h3 className="text-warning">{stats.tickets.critical_priority}</h3>
                <small className="text-muted">Críticos</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-success">
              <Card.Body>
                <h3 className="text-success">{stats.tickets.closed}</h3>
                <small className="text-muted">Cerrados</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Tickets Table */}
      <Card>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
            </div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
              <p className="text-muted mt-3">No hay tickets registrados</p>
            </div>
          ) : (
            <Table hover responsive className="mb-0">
              <thead className="table-light">
                <tr>
                  <th>Ticket #</th>
                  <th>IMEI</th>
                  <th>Cliente</th>
                  <th>Problema</th>
                  <th>Estado</th>
                  <th>Prioridad</th>
                  <th>Mensajes</th>
                  <th>Fecha</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td><strong>{ticket.ticket_number}</strong></td>
                    <td><code>{ticket.device_imei}</code></td>
                    <td>
                      {ticket.customer_name}
                      <br />
                      <small className="text-muted">{ticket.customer_email}</small>
                    </td>
                    <td>{ticket.issue_type}</td>
                    <td>{getStatusBadge(ticket.status)}</td>
                    <td>{getPriorityBadge(ticket.priority)}</td>
                    <td>
                      <Badge bg="info">{ticket.messages_count}</Badge>
                    </td>
                    <td>
                      <small className="text-muted">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </small>
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => handleViewTicket(ticket.id)}
                      >
                        <i className="bi bi-eye"></i>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
        </Tab>

        {/* RMA Tab */}
        <Tab eventKey="rma" title={<><i className="bi bi-box-seam me-2"></i>Gestión RMA</>}>
          <RMAManagementTab />
        </Tab>

        {/* Public Users Tab */}
        <Tab eventKey="public-users" title={<><i className="bi bi-people me-2"></i>Usuarios Públicos</>}>
          <PublicUsersTab />
        </Tab>
      </Tabs>

      {/* New Ticket Modal */}
      <Modal show={showNewTicket} onHide={() => setShowNewTicket(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Nuevo Ticket de Soporte</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>IMEI del Dispositivo *</Form.Label>
                  <Form.Control
                    type="text"
                    value={newTicketData.device_imei}
                    onChange={(e) => setNewTicketData({ ...newTicketData, device_imei: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tipo de Problema *</Form.Label>
                  <Form.Select
                    value={newTicketData.issue_type}
                    onChange={(e) => setNewTicketData({ ...newTicketData, issue_type: e.target.value })}
                  >
                    <option value="technical">Técnico</option>
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="connectivity">Conectividad</option>
                    <option value="other">Otro</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Nombre del Cliente</Form.Label>
                  <Form.Control
                    type="text"
                    value={newTicketData.customer_name}
                    onChange={(e) => setNewTicketData({ ...newTicketData, customer_name: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Email del Cliente</Form.Label>
                  <Form.Control
                    type="email"
                    value={newTicketData.customer_email}
                    onChange={(e) => setNewTicketData({ ...newTicketData, customer_email: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Prioridad</Form.Label>
              <Form.Select
                value={newTicketData.priority}
                onChange={(e) => setNewTicketData({ ...newTicketData, priority: e.target.value })}
              >
                <option value="low">Baja</option>
                <option value="medium">Media</option>
                <option value="high">Alta</option>
                <option value="critical">Crítica</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Descripción del Problema *</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={newTicketData.description}
                onChange={(e) => setNewTicketData({ ...newTicketData, description: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNewTicket(false)}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleCreateTicket}>
            Crear Ticket
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Ticket Details Modal */}
      <Modal show={showDetails} onHide={() => setShowDetails(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedTicket?.ticket_number} - {getStatusBadge(selectedTicket?.status || '')}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTicket && (
            <>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>IMEI:</strong> <code>{selectedTicket.device_imei}</code>
                </Col>
                <Col md={6}>
                  <strong>Prioridad:</strong> {getPriorityBadge(selectedTicket.priority)}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Cliente:</strong> {selectedTicket.customer_name}
                </Col>
                <Col md={6}>
                  <strong>Email:</strong> {selectedTicket.customer_email}
                </Col>
              </Row>
              <div className="mb-3">
                <strong>Descripción:</strong>
                <p className="mt-2">{selectedTicket.description}</p>
              </div>

              <hr />

              <h6>Mensajes</h6>
              <div style={{ maxHeight: '300px', overflowY: 'auto' }} className="mb-3">
                {selectedTicket.messages && selectedTicket.messages.length > 0 ? (
                  selectedTicket.messages.map((msg: any, idx: number) => (
                    <Card key={idx} className="mb-2">
                      <Card.Body className="p-2">
                        <small className="text-muted">
                          {msg.from_user} - {new Date(msg.timestamp).toLocaleString()}
                        </small>
                        <p className="mb-0 mt-1">{msg.message}</p>
                      </Card.Body>
                    </Card>
                  ))
                ) : (
                  <p className="text-muted">No hay mensajes</p>
                )}
              </div>

              <InputGroup>
                <Form.Control
                  as="textarea"
                  rows={2}
                  placeholder="Escribe un mensaje..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                />
                <Button variant="primary" onClick={handleSendMessage}>
                  <i className="bi bi-send"></i>
                </Button>
              </InputGroup>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="success" onClick={() => handleUpdateStatus('closed')}>
            Cerrar Ticket
          </Button>
          <Button variant="warning" onClick={() => handleUpdateStatus('escalated')}>
            Escalar a RMA
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}
