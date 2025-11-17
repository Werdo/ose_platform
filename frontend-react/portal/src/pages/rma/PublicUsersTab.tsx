/**
 * Public Users Management Tab
 * Gestión de usuarios del portal público desde el panel de administración
 */

import { useState, useEffect } from 'react'
import {
  Row, Col, Card, Button, Badge, Table, Modal, Form, Alert, InputGroup
} from 'react-bootstrap'
import { apiService } from '../../services/api.service'

interface PublicUser {
  id: string
  email: string
  nombre: string
  apellidos: string
  telefono: string
  empresa: string
  status: string
  is_verified: boolean
  created_at: string
  last_login: string | null
  notes: string
}

export default function PublicUsersTab() {
  const [users, setUsers] = useState<PublicUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  // New user modal
  const [showNewUser, setShowNewUser] = useState(false)
  const [newUserData, setNewUserData] = useState({
    email: '',
    password: '',
    nombre: '',
    apellidos: '',
    telefono: '',
    empresa: '',
    notes: ''
  })

  // User details modal
  const [showDetails, setShowDetails] = useState(false)
  const [selectedUser, setSelectedUser] = useState<PublicUser | null>(null)
  const [userTickets, setUserTickets] = useState<any[]>([])

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const response = await apiService.get('/api/app3/public-users?limit=100')
      setUsers(response.users || [])
      setError(null)
    } catch (err: any) {
      setError('Error cargando usuarios públicos')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async () => {
    try {
      await apiService.post('/api/app3/public-users', newUserData)
      setShowNewUser(false)
      setNewUserData({
        email: '',
        password: '',
        nombre: '',
        apellidos: '',
        telefono: '',
        empresa: '',
        notes: ''
      })
      loadUsers()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creando usuario')
    }
  }

  const handleViewUser = async (user: PublicUser) => {
    try {
      // Load user tickets
      const response = await apiService.get(`/api/app3/public-users/${user.id}/tickets`)
      setUserTickets(response.tickets || [])
      setSelectedUser(user)
      setShowDetails(true)
    } catch (err: any) {
      setError('Error cargando tickets del usuario')
    }
  }

  const handleUpdateStatus = async (userId: string, newStatus: string) => {
    try {
      await apiService.patch(`/api/app3/public-users/${userId}`, { status: newStatus })
      loadUsers()
      setShowDetails(false)
    } catch (err: any) {
      setError('Error actualizando usuario')
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      active: 'success',
      inactive: 'secondary',
      blocked: 'danger'
    }
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>
  }

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (user.empresa && user.empresa.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <>
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h5 className="mb-1">
            <i className="bi bi-people me-2 text-primary"></i>
            Usuarios del Portal Público
          </h5>
          <p className="text-muted mb-0 small">
            Gestión de usuarios externos con acceso al portal público
          </p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setShowNewUser(true)}>
          <i className="bi bi-person-plus me-2"></i>
          Nuevo Usuario
        </Button>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Stats */}
      <Row className="mb-4">
        <Col md={4}>
          <Card className="text-center border-success">
            <Card.Body className="py-3">
              <h4 className="mb-0 text-success">
                {users.filter(u => u.status === 'active').length}
              </h4>
              <small className="text-muted">Activos</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center border-secondary">
            <Card.Body className="py-3">
              <h4 className="mb-0 text-secondary">
                {users.filter(u => u.status === 'inactive').length}
              </h4>
              <small className="text-muted">Inactivos</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center border-danger">
            <Card.Body className="py-3">
              <h4 className="mb-0 text-danger">
                {users.filter(u => u.status === 'blocked').length}
              </h4>
              <small className="text-muted">Bloqueados</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Search */}
      <InputGroup className="mb-3">
        <InputGroup.Text>
          <i className="bi bi-search"></i>
        </InputGroup.Text>
        <Form.Control
          placeholder="Buscar por email, nombre o empresa..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </InputGroup>

      {/* Users Table */}
      <Card>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Cargando...</span>
              </div>
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
              <p className="text-muted mt-3">No hay usuarios públicos registrados</p>
            </div>
          ) : (
            <Table hover responsive className="mb-0">
              <thead className="table-light">
                <tr>
                  <th>Email</th>
                  <th>Nombre</th>
                  <th>Empresa</th>
                  <th>Estado</th>
                  <th>Verificado</th>
                  <th>Registro</th>
                  <th>Último Login</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <i className="bi bi-envelope me-1 text-muted"></i>
                      {user.email}
                    </td>
                    <td>
                      {user.nombre} {user.apellidos}
                    </td>
                    <td>
                      {user.empresa || <span className="text-muted">-</span>}
                    </td>
                    <td>{getStatusBadge(user.status)}</td>
                    <td>
                      {user.is_verified ? (
                        <i className="bi bi-check-circle-fill text-success"></i>
                      ) : (
                        <i className="bi bi-x-circle text-secondary"></i>
                      )}
                    </td>
                    <td>
                      <small className="text-muted">
                        {new Date(user.created_at).toLocaleDateString()}
                      </small>
                    </td>
                    <td>
                      <small className="text-muted">
                        {user.last_login
                          ? new Date(user.last_login).toLocaleDateString()
                          : 'Nunca'}
                      </small>
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => handleViewUser(user)}
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

      {/* New User Modal */}
      <Modal show={showNewUser} onHide={() => setShowNewUser(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Crear Usuario del Portal Público</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Nombre *</Form.Label>
                  <Form.Control
                    type="text"
                    value={newUserData.nombre}
                    onChange={(e) => setNewUserData({ ...newUserData, nombre: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Apellidos</Form.Label>
                  <Form.Control
                    type="text"
                    value={newUserData.apellidos}
                    onChange={(e) => setNewUserData({ ...newUserData, apellidos: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Email *</Form.Label>
              <Form.Control
                type="email"
                value={newUserData.email}
                onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Contraseña *</Form.Label>
              <Form.Control
                type="password"
                placeholder="Mínimo 8 caracteres"
                value={newUserData.password}
                onChange={(e) => setNewUserData({ ...newUserData, password: e.target.value })}
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Teléfono</Form.Label>
                  <Form.Control
                    type="tel"
                    value={newUserData.telefono}
                    onChange={(e) => setNewUserData({ ...newUserData, telefono: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Empresa</Form.Label>
                  <Form.Control
                    type="text"
                    value={newUserData.empresa}
                    onChange={(e) => setNewUserData({ ...newUserData, empresa: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Notas Administrativas</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={newUserData.notes}
                onChange={(e) => setNewUserData({ ...newUserData, notes: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNewUser(false)}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleCreateUser}>
            Crear Usuario
          </Button>
        </Modal.Footer>
      </Modal>

      {/* User Details Modal */}
      <Modal show={showDetails} onHide={() => setShowDetails(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            Detalles de Usuario - {getStatusBadge(selectedUser?.status || '')}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedUser && (
            <>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Email:</strong> {selectedUser.email}
                </Col>
                <Col md={6}>
                  <strong>Nombre:</strong> {selectedUser.nombre} {selectedUser.apellidos}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Teléfono:</strong> {selectedUser.telefono || '-'}
                </Col>
                <Col md={6}>
                  <strong>Empresa:</strong> {selectedUser.empresa || '-'}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={6}>
                  <strong>Verificado:</strong>{' '}
                  {selectedUser.is_verified ? (
                    <Badge bg="success">Sí</Badge>
                  ) : (
                    <Badge bg="secondary">No</Badge>
                  )}
                </Col>
                <Col md={6}>
                  <strong>Último Login:</strong>{' '}
                  {selectedUser.last_login
                    ? new Date(selectedUser.last_login).toLocaleString()
                    : 'Nunca'}
                </Col>
              </Row>

              {selectedUser.notes && (
                <div className="mb-3">
                  <strong>Notas:</strong>
                  <p className="mt-1 text-muted">{selectedUser.notes}</p>
                </div>
              )}

              <hr />

              <h6>Tickets ({userTickets.length})</h6>
              {userTickets.length === 0 ? (
                <p className="text-muted">No tiene tickets registrados</p>
              ) : (
                <Table size="sm" className="mt-2">
                  <thead>
                    <tr>
                      <th>Ticket #</th>
                      <th>IMEI</th>
                      <th>Estado</th>
                      <th>Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {userTickets.map((ticket: any) => (
                      <tr key={ticket.id}>
                        <td>{ticket.ticket_number}</td>
                        <td><code>{ticket.device_imei}</code></td>
                        <td>
                          <Badge bg={
                            ticket.status === 'closed' ? 'success' :
                            ticket.status === 'open' ? 'primary' : 'info'
                          }>
                            {ticket.status}
                          </Badge>
                        </td>
                        <td>
                          <small>{new Date(ticket.created_at).toLocaleDateString()}</small>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          {selectedUser && (
            <>
              {selectedUser.status === 'active' && (
                <Button
                  variant="warning"
                  onClick={() => handleUpdateStatus(selectedUser.id, 'blocked')}
                >
                  Bloquear Usuario
                </Button>
              )}
              {selectedUser.status === 'blocked' && (
                <Button
                  variant="success"
                  onClick={() => handleUpdateStatus(selectedUser.id, 'active')}
                >
                  Desbloquear Usuario
                </Button>
              )}
              <Button variant="secondary" onClick={() => setShowDetails(false)}>
                Cerrar
              </Button>
            </>
          )}
        </Modal.Footer>
      </Modal>
    </>
  )
}
