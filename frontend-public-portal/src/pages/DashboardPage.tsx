/**
 * Public Portal - Dashboard Page
 * Main page for authenticated public users
 */

import { useState, useEffect } from 'react'
import {
  Container, Row, Col, Card, Button, Table, Badge,
  Modal, Form, Alert, Navbar, Nav
} from 'react-bootstrap'
import { apiService } from '../services/api'

interface DashboardPageProps {
  onLogout: () => void
}

interface Ticket {
  id: string
  ticket_number: string
  device_imei: string
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
}

export default function DashboardPage({ onLogout }: DashboardPageProps) {
  const [user, setUser] = useState<any>(null)
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // New ticket modal
  const [showNewTicket, setShowNewTicket] = useState(false)
  const [newTicketData, setNewTicketData] = useState({
    device_imei: '',
    issue_type: 'technical',
    description: '',
    priority: 'medium'
  })

  // Ticket details modal
  const [showDetails, setShowDetails] = useState(false)
  const [selectedTicket, setSelectedTicket] = useState<TicketDetails | null>(null)
  const [newMessage, setNewMessage] = useState('')

  useEffect(() => {
    loadUserData()
    loadTickets()
  }, [])

  const loadUserData = () => {
    const userData = localStorage.getItem('public_user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }

  const loadTickets = async () => {
    setLoading(true)
    try {
      const response = await apiService.getMyTickets()
      setTickets(response.tickets || [])
      setError('')
    } catch (err: any) {
      setError('Error cargando tickets')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTicket = async () => {
    try {
      await apiService.createTicket(newTicketData)
      setShowNewTicket(false)
      setNewTicketData({
        device_imei: '',
        issue_type: 'technical',
        description: '',
        priority: 'medium'
      })
      loadTickets()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creando ticket')
    }
  }

  const handleViewTicket = async (ticketId: string) => {
    try {
      const response = await apiService.getTicket(ticketId)
      setSelectedTicket(response.ticket)
      setShowDetails(true)
    } catch (err: any) {
      setError('Error cargando detalles del ticket')
    }
  }

  const handleSendMessage = async () => {
    if (!selectedTicket || !newMessage.trim()) return

    try {
      await apiService.addMessage(selectedTicket.id, newMessage)
      setNewMessage('')
      // Reload ticket details
      const response = await apiService.getTicket(selectedTicket.id)
      setSelectedTicket(response.ticket)
    } catch (err: any) {
      setError('Error enviando mensaje')
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
    <>
      {/* Navbar */}
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand>
            <i className="bi bi-ticket-perforated me-2"></i>
            Portal OSE
          </Navbar.Brand>
          <Navbar.Toggle />
          <Navbar.Collapse>
            <Nav className="ms-auto">
              <Nav.Link disabled>
                <i className="bi bi-person-circle me-1"></i>
                {user?.nombre || 'Usuario'}
              </Nav.Link>
              <Nav.Link onClick={onLogout}>
                <i className="bi bi-box-arrow-right me-1"></i>
                Salir
              </Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Main Content */}
      <Container>
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 className="mb-1">Mis Tickets de Soporte</h4>
            <p className="text-muted mb-0">Gestiona tus solicitudes de soporte</p>
          </div>
          <Button variant="primary" onClick={() => setShowNewTicket(true)}>
            <i className="bi bi-plus-circle me-2"></i>
            Nuevo Ticket
          </Button>
        </div>

        {error && (
          <Alert variant="danger" dismissible onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Tickets Stats */}
        <Row className="mb-4">
          <Col md={4}>
            <Card className="text-center">
              <Card.Body>
                <h3>{tickets.length}</h3>
                <small className="text-muted">Total Tickets</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="text-center border-primary">
              <Card.Body>
                <h3 className="text-primary">
                  {tickets.filter(t => t.status === 'open' || t.status === 'in_progress').length}
                </h3>
                <small className="text-muted">Abiertos</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="text-center border-success">
              <Card.Body>
                <h3 className="text-success">
                  {tickets.filter(t => t.status === 'closed').length}
                </h3>
                <small className="text-muted">Cerrados</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Tickets Table */}
        <Card>
          <Card.Body className="p-0">
            {loading ? (
              <div className="text-center py-5">
                <div className="spinner-border" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
              </div>
            ) : tickets.length === 0 ? (
              <div className="text-center py-5">
                <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                <p className="text-muted mt-3">No tienes tickets registrados</p>
                <Button variant="primary" onClick={() => setShowNewTicket(true)}>
                  Crear tu primer ticket
                </Button>
              </div>
            ) : (
              <Table hover responsive className="mb-0">
                <thead className="table-light">
                  <tr>
                    <th>Ticket #</th>
                    <th>IMEI</th>
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
      </Container>

      {/* New Ticket Modal */}
      <Modal show={showNewTicket} onHide={() => setShowNewTicket(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Nuevo Ticket de Soporte</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>IMEI del Dispositivo *</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ingrese el IMEI del dispositivo"
                value={newTicketData.device_imei}
                onChange={(e) => setNewTicketData({ ...newTicketData, device_imei: e.target.value })}
              />
            </Form.Group>

            <Row>
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
              <Col md={6}>
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
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Descripción del Problema *</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                placeholder="Describe el problema en detalle..."
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
              <div className="mb-3">
                <strong>Descripción:</strong>
                <p className="mt-2">{selectedTicket.description}</p>
              </div>

              <hr />

              <h6>Conversación</h6>
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
                  <p className="text-muted">No hay mensajes aún</p>
                )}
              </div>

              <Form.Group>
                <Form.Label>Enviar mensaje</Form.Label>
                <div className="d-flex gap-2">
                  <Form.Control
                    as="textarea"
                    rows={2}
                    placeholder="Escribe tu mensaje..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                  />
                  <Button variant="primary" onClick={handleSendMessage}>
                    <i className="bi bi-send"></i>
                  </Button>
                </div>
              </Form.Group>
            </>
          )}
        </Modal.Body>
      </Modal>
    </>
  )
}
