/**
 * Users Management Tab - CRUD for employees
 */

import { useState, useEffect } from 'react'
import {
  Row, Col, Card, Table, Button, Badge, Form, Modal,
  InputGroup, Alert, Spinner
} from 'react-bootstrap'
import { apiService } from '../../../services/api.service'

interface User {
  id: string
  employee_id: string
  name: string
  surname: string
  email: string
  role: string
  status?: string
  last_login?: string
  permissions?: Record<string, boolean>
}

export default function UsersManagementTab() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    surname: '',
    email: '',
    password: '',
    role: 'operator',
    status: 'active',
    app_permissions: {
      app1_access: false,
      app2_access: false,
      app3_access: false,
      app4_access: false,
      app5_access: false,
      app6_access: false
    }
  })

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const response = await apiService.get('/api/v1/employees')
      setUsers(response.data.map((emp: any) => ({
        id: emp._id || emp.id,
        employee_id: emp.employee_id,
        name: emp.name,
        surname: emp.surname,
        email: emp.email || '',
        role: emp.role,
        status: emp.status || 'active',
        last_login: emp.last_login,
        permissions: emp.permissions || {}
      })))
      setError(null)
    } catch (err: any) {
      console.error('Error loading users:', err)
      setError(err.response?.data?.detail || 'Error cargando usuarios')
    } finally {
      setLoading(false)
    }
  }

  const getRoleBadge = (role: string) => {
    const variants: Record<string, string> = {
      super_admin: 'danger',
      admin: 'warning',
      supervisor: 'info',
      operator: 'primary',
      viewer: 'secondary'
    }
    return <Badge bg={variants[role] || 'secondary'}>{role.replace('_', ' ')}</Badge>
  }

  const getStatusBadge = (status?: string) => {
    if (status === 'active') return <Badge bg="success">Activo</Badge>
    if (status === 'inactive') return <Badge bg="secondary">Inactivo</Badge>
    return <Badge bg="warning">Suspendido</Badge>
  }

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user)
      setFormData({
        employee_id: user.employee_id,
        name: user.name,
        surname: user.surname,
        email: user.email,
        password: '',
        role: user.role,
        status: user.status || 'active',
        app_permissions: {
          app1_access: user.permissions?.app1_access || false,
          app2_access: user.permissions?.app2_access || false,
          app3_access: user.permissions?.app3_access || false,
          app4_access: user.permissions?.app4_access || false,
          app5_access: user.permissions?.app5_access || false,
          app6_access: user.permissions?.app6_access || false
        }
      })
    } else {
      setEditingUser(null)
      setFormData({
        employee_id: '',
        name: '',
        surname: '',
        email: '',
        password: '',
        role: 'operator',
        status: 'active',
        app_permissions: {
          app1_access: false,
          app2_access: false,
          app3_access: false,
          app4_access: false,
          app5_access: false,
          app6_access: false
        }
      })
    }
    setShowModal(true)
  }

  const handleSaveUser = async () => {
    try {
      const payload = {
        employee_id: formData.employee_id,
        name: formData.name,
        surname: formData.surname,
        email: formData.email,
        role: formData.role,
        status: formData.status,
        permissions: {
          ...formData.app_permissions,
          // Mantener otros permisos si existen
          quality_control: false,
          admin_access: formData.role === 'super_admin' || formData.role === 'admin',
          manage_users: formData.role === 'super_admin' || formData.role === 'admin',
          manage_settings: formData.role === 'super_admin' || formData.role === 'admin',
          view_reports: true
        },
        ...(formData.password && { password: formData.password })
      }

      if (editingUser) {
        // Actualizar usuario existente
        await apiService.put(`/api/v1/employees/${editingUser.employee_id}`, payload)
      } else {
        // Crear nuevo usuario
        if (!formData.password) {
          setError('La contraseña es requerida para crear un nuevo usuario')
          return
        }
        await apiService.post('/api/v1/employees', payload)
      }

      setShowModal(false)
      setError(null)
      loadUsers()
    } catch (err: any) {
      console.error('Error saving user:', err)
      setError(err.response?.data?.detail || 'Error guardando usuario')
    }
  }

  const handleDeleteUser = async (employeeId: string) => {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) return

    try {
      await apiService.delete(`/api/v1/employees/${employeeId}`)
      setError(null)
      loadUsers()
    } catch (err: any) {
      console.error('Error deleting user:', err)
      setError(err.response?.data?.detail || 'Error eliminando usuario')
    }
  }

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.surname.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.employee_id.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">Gestión de Usuarios</h5>
        <Button variant="primary" onClick={() => handleOpenModal()}>
          <i className="bi bi-person-plus me-2"></i>
          Nuevo Usuario
        </Button>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search */}
      <Row className="mb-3">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Buscar usuarios..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
      </Row>

      {/* Users Table */}
      <Card>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
            </div>
          ) : (
            <Table hover responsive className="mb-0">
              <thead className="table-light">
                <tr>
                  <th>Employee ID</th>
                  <th>Nombre</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Último Login</th>
                  <th className="text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(user => (
                  <tr key={user.id}>
                    <td>
                      <strong>{user.employee_id}</strong>
                    </td>
                    <td>{user.name} {user.surname}</td>
                    <td>{user.email}</td>
                    <td>{getRoleBadge(user.role)}</td>
                    <td>{getStatusBadge(user.status)}</td>
                    <td>
                      <small className="text-muted">
                        {user.last_login ? new Date(user.last_login).toLocaleString() : 'Nunca'}
                      </small>
                    </td>
                    <td className="text-end">
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        onClick={() => handleOpenModal(user)}
                      >
                        <i className="bi bi-pencil"></i>
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDeleteUser(user.employee_id)}
                        disabled={user.role === 'super_admin'}
                      >
                        <i className="bi bi-trash"></i>
                      </Button>
                    </td>
                  </tr>
                ))}
                {filteredUsers.length === 0 && (
                  <tr>
                    <td colSpan={7} className="text-center py-4 text-muted">
                      No se encontraron usuarios
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* User Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Employee ID *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.employee_id}
                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                    disabled={!!editingUser}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Email *</Form.Label>
                  <Form.Control
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Nombre *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Apellidos *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.surname}
                    onChange={(e) => setFormData({ ...formData, surname: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contraseña {!editingUser && '*'}</Form.Label>
                  <Form.Control
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder={editingUser ? 'Dejar vacío para no cambiar' : ''}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Rol *</Form.Label>
                  <Form.Select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  >
                    <option value="operator">Operator</option>
                    <option value="supervisor">Supervisor</option>
                    <option value="admin">Admin</option>
                    <option value="super_admin">Super Admin</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Estado</Form.Label>
              <Form.Select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="active">Activo</option>
                <option value="inactive">Inactivo</option>
                <option value="suspended">Suspendido</option>
              </Form.Select>
            </Form.Group>

            {/* Permisos de Aplicaciones */}
            <hr />
            <h6 className="mb-3">
              <i className="bi bi-grid-fill me-2"></i>
              Permisos de Aplicaciones
            </h6>
            <p className="text-muted small mb-3">
              Selecciona las aplicaciones a las que este usuario tendrá acceso.
              <strong> Como Super Admin, puedes modificar todos los permisos de cualquier usuario.</strong>
            </p>

            <Row>
              <Col md={6}>
                <Form.Check
                  type="switch"
                  id="app1-switch"
                  label="App 1: Notificación de Series"
                  checked={formData.app_permissions.app1_access}
                  onChange={(e) => setFormData({
                    ...formData,
                    app_permissions: { ...formData.app_permissions, app1_access: e.target.checked }
                  })}
                  className="mb-2"
                />
                <Form.Check
                  type="switch"
                  id="app2-switch"
                  label="App 2: Importación de Datos"
                  checked={formData.app_permissions.app2_access}
                  onChange={(e) => setFormData({
                    ...formData,
                    app_permissions: { ...formData.app_permissions, app2_access: e.target.checked }
                  })}
                  className="mb-2"
                />
                <Form.Check
                  type="switch"
                  id="app3-switch"
                  label="App 3: RMA & Tickets"
                  checked={formData.app_permissions.app3_access}
                  onChange={(e) => setFormData({
                    ...formData,
                    app_permissions: { ...formData.app_permissions, app3_access: e.target.checked }
                  })}
                  className="mb-2"
                />
              </Col>
              <Col md={6}>
                <Form.Check
                  type="switch"
                  id="app4-switch"
                  label="App 4: Transform Data"
                  checked={formData.app_permissions.app4_access}
                  onChange={(e) => setFormData({
                    ...formData,
                    app_permissions: { ...formData.app_permissions, app4_access: e.target.checked }
                  })}
                  className="mb-2"
                />
                <Form.Check
                  type="switch"
                  id="app5-switch"
                  label="App 5: Generación de Facturas"
                  checked={formData.app_permissions.app5_access}
                  onChange={(e) => setFormData({
                    ...formData,
                    app_permissions: { ...formData.app_permissions, app5_access: e.target.checked }
                  })}
                  className="mb-2"
                />
                <Form.Check
                  type="switch"
                  id="app6-switch"
                  label="App 6: Picking & Etiquetado"
                  checked={formData.app_permissions.app6_access}
                  onChange={(e) => setFormData({
                    ...formData,
                    app_permissions: { ...formData.app_permissions, app6_access: e.target.checked }
                  })}
                  className="mb-2"
                />
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleSaveUser}>
            <i className="bi bi-save me-2"></i>
            Guardar
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  )
}
