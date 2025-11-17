/**
 * OSE Platform - Notifications Page
 * Complete notification management system
 * Design based on Assetflow AlertasPage
 */

import { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Button, Form, Table, Badge, Modal, Spinner, Alert } from 'react-bootstrap'
import toast from 'react-hot-toast'
import notificationService from '../../services/notification.service'
import type { Notification, NotificationFilters, NotificationStats, NotificationType, NotificationPriority, NotificationStatus } from '../../types/notifications'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function NotificationsPage() {
  // State
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [stats, setStats] = useState<NotificationStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [limit] = useState(20)

  // Filters
  const [filters, setFilters] = useState<NotificationFilters>({})
  const [showFilters, setShowFilters] = useState(true)

  // Modals
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showResolveModal, setShowResolveModal] = useState(false)
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)
  const [resolutionNotes, setResolutionNotes] = useState('')

  // Load data
  useEffect(() => {
    loadNotifications()
    loadStatistics()
  }, [currentPage, filters])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const response = await notificationService.getAll(currentPage, limit, filters)
      setNotifications(response.items)
      setTotalPages(response.pages)
      setTotal(response.total)
    } catch (error: any) {
      toast.error('Error al cargar notificaciones')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const data = await notificationService.getStatistics()
      setStats(data)
    } catch (error) {
      console.error('Error loading statistics:', error)
    }
  }

  // Handlers
  const handleSelectAll = () => {
    if (selectedIds.length === notifications.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(notifications.map((n) => n.id))
    }
  }

  const handleSelectOne = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((sid) => sid !== id))
    } else {
      setSelectedIds([...selectedIds, id])
    }
  }

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationService.markAsRead(id)
      toast.success('Notificación marcada como leída')
      loadNotifications()
      loadStatistics()
    } catch (error) {
      toast.error('Error al marcar como leída')
    }
  }

  const handleShowDetail = (notification: Notification) => {
    setSelectedNotification(notification)
    setShowDetailModal(true)
  }

  const handleShowResolve = (notification: Notification) => {
    setSelectedNotification(notification)
    setResolutionNotes('')
    setShowResolveModal(true)
  }

  const handleResolve = async () => {
    if (!selectedNotification) return

    try {
      await notificationService.resolve(selectedNotification.id, { resolution_notes: resolutionNotes })
      toast.success('Notificación resuelta')
      setShowResolveModal(false)
      setSelectedNotification(null)
      setResolutionNotes('')
      loadNotifications()
      loadStatistics()
    } catch (error) {
      toast.error('Error al resolver notificación')
    }
  }

  const handleBatchResolve = async () => {
    if (selectedIds.length === 0) {
      toast.error('Selecciona al menos una notificación')
      return
    }

    try {
      const result = await notificationService.resolveMultiple({ ids: selectedIds })
      toast.success(`${result.resolved} notificación(es) resuelta(s)`)
      setSelectedIds([])
      loadNotifications()
      loadStatistics()
    } catch (error) {
      toast.error('Error al resolver notificaciones')
    }
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('¿Estás seguro de eliminar esta notificación?')) return

    try {
      await notificationService.delete(id)
      toast.success('Notificación eliminada')
      loadNotifications()
      loadStatistics()
    } catch (error) {
      toast.error('Error al eliminar notificación')
    }
  }

  const handleFilterChange = (key: keyof NotificationFilters, value: any) => {
    setFilters({ ...filters, [key]: value })
    setCurrentPage(1)
  }

  const handleResetFilters = () => {
    setFilters({})
    setCurrentPage(1)
  }

  // Helper functions
  const getTypeLabel = (type: NotificationType): string => {
    const labels: Record<NotificationType, string> = {
      new_device_registered: 'Dispositivo Nuevo',
      device_shipped: 'Enviado',
      device_delivered: 'Entregado',
      device_activated: 'Activado',
      device_failure: 'Fallo',
      device_maintenance: 'Mantenimiento',
      batch_registered: 'Lote Registrado',
      custom: 'Personalizada',
    }
    return labels[type]
  }

  const getTypeIcon = (type: NotificationType): string => {
    const icons: Record<NotificationType, string> = {
      new_device_registered: 'bi-plus-circle-fill',
      device_shipped: 'bi-truck',
      device_delivered: 'bi-check-circle-fill',
      device_activated: 'bi-power',
      device_failure: 'bi-exclamation-triangle-fill',
      device_maintenance: 'bi-tools',
      batch_registered: 'bi-boxes',
      custom: 'bi-star-fill',
    }
    return icons[type]
  }

  const getPriorityVariant = (priority: NotificationPriority): string => {
    const variants: Record<NotificationPriority, string> = {
      low: 'secondary',
      medium: 'warning',
      high: 'danger',
      critical: 'dark',
    }
    return variants[priority]
  }

  const getStatusVariant = (status: NotificationStatus): string => {
    const variants: Record<NotificationStatus, string> = {
      pending: 'warning',
      read: 'info',
      resolved: 'success',
      archived: 'secondary',
    }
    return variants[status]
  }

  const getStatusLabel = (status: NotificationStatus): string => {
    const labels: Record<NotificationStatus, string> = {
      pending: 'Pendiente',
      read: 'Leída',
      resolved: 'Resuelta',
      archived: 'Archivada',
    }
    return labels[status]
  }

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">
                <i className="bi bi-bell-fill me-2 text-primary"></i>
                Sistema de Notificaciones
              </h2>
              <p className="text-muted mb-0">Gestión de notificaciones de series de dispositivos</p>
            </div>
            <div>
              {selectedIds.length > 0 && (
                <Button variant="success" onClick={handleBatchResolve} className="me-2">
                  <i className="bi bi-check-all me-1"></i>
                  Resolver Seleccionadas ({selectedIds.length})
                </Button>
              )}
              <Button variant="primary" onClick={() => setShowFilters(!showFilters)}>
                <i className={`bi bi-funnel${showFilters ? '-fill' : ''} me-1`}></i>
                {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Statistics Cards */}
      {stats && (
        <Row className="g-3 mb-4">
          <Col xs={12} sm={6} md={3}>
            <Card className="border-0 shadow-sm stat-card border-primary">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="text-muted text-uppercase small mb-1">Total</div>
                    <h3 className="mb-0">{stats.total}</h3>
                  </div>
                  <div className="icon-badge primary">
                    <i className="bi bi-bell-fill"></i>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} md={3}>
            <Card className="border-0 shadow-sm stat-card border-warning">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="text-muted text-uppercase small mb-1">Pendientes</div>
                    <h3 className="mb-0">{stats.pending}</h3>
                  </div>
                  <div className="icon-badge warning">
                    <i className="bi bi-hourglass-split"></i>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} md={3}>
            <Card className="border-0 shadow-sm stat-card border-danger">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="text-muted text-uppercase small mb-1">Críticas</div>
                    <h3 className="mb-0">{stats.by_priority.critical}</h3>
                  </div>
                  <div className="icon-badge danger">
                    <i className="bi bi-exclamation-triangle-fill"></i>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} md={3}>
            <Card className="border-0 shadow-sm stat-card border-success">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="text-muted text-uppercase small mb-1">Resueltas</div>
                    <h3 className="mb-0">{stats.resolved}</h3>
                  </div>
                  <div className="icon-badge success">
                    <i className="bi bi-check-circle-fill"></i>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      {showFilters && (
        <Card className="border-0 shadow-sm mb-4">
          <Card.Header className="gradient-primary text-white fw-bold">
            <i className="bi bi-funnel-fill me-2"></i>
            Filtros Avanzados
          </Card.Header>
          <Card.Body>
            <Row className="g-3">
              <Col md={3}>
                <Form.Label>Tipo</Form.Label>
                <Form.Select
                  value={filters.type || ''}
                  onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
                >
                  <option value="">Todos</option>
                  <option value="new_device_registered">Dispositivo Nuevo</option>
                  <option value="batch_registered">Lote Registrado</option>
                  <option value="device_shipped">Enviado</option>
                  <option value="device_failure">Fallo</option>
                  <option value="device_maintenance">Mantenimiento</option>
                </Form.Select>
              </Col>
              <Col md={3}>
                <Form.Label>Prioridad</Form.Label>
                <Form.Select
                  value={filters.priority || ''}
                  onChange={(e) => handleFilterChange('priority', e.target.value || undefined)}
                >
                  <option value="">Todas</option>
                  <option value="low">Baja</option>
                  <option value="medium">Media</option>
                  <option value="high">Alta</option>
                  <option value="critical">Crítica</option>
                </Form.Select>
              </Col>
              <Col md={3}>
                <Form.Label>Estado</Form.Label>
                <Form.Select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
                >
                  <option value="">Todos</option>
                  <option value="pending">Pendiente</option>
                  <option value="read">Leída</option>
                  <option value="resolved">Resuelta</option>
                </Form.Select>
              </Col>
              <Col md={3}>
                <Form.Label>Buscar</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="IMEI, serie, mensaje..."
                  value={filters.search || ''}
                  onChange={(e) => handleFilterChange('search', e.target.value || undefined)}
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
        </Card>
      )}

      {/* Notifications Table */}
      <Card className="border-0 shadow-sm">
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 text-muted">Cargando notificaciones...</p>
            </div>
          ) : notifications.length === 0 ? (
            <Alert variant="info" className="m-4">
              <i className="bi bi-info-circle me-2"></i>
              No se encontraron notificaciones
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th style={{ width: '40px' }}>
                      <Form.Check
                        type="checkbox"
                        checked={selectedIds.length === notifications.length && notifications.length > 0}
                        onChange={handleSelectAll}
                      />
                    </th>
                    <th>Tipo</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Mensaje</th>
                    <th>Dispositivo/Serie</th>
                    <th>Fecha</th>
                    <th style={{ width: '150px' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {notifications.map((notification) => (
                    <tr key={notification.id}>
                      <td>
                        <Form.Check
                          type="checkbox"
                          checked={selectedIds.includes(notification.id)}
                          onChange={() => handleSelectOne(notification.id)}
                        />
                      </td>
                      <td>
                        <i className={`${getTypeIcon(notification.type)} me-2`}></i>
                        {getTypeLabel(notification.type)}
                      </td>
                      <td>
                        <Badge bg={getPriorityVariant(notification.priority)}>
                          {notification.priority.toUpperCase()}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg={getStatusVariant(notification.status)}>
                          {getStatusLabel(notification.status)}
                        </Badge>
                      </td>
                      <td>
                        <div className="fw-bold">{notification.title}</div>
                        <small className="text-muted">{notification.message}</small>
                      </td>
                      <td>
                        {notification.device_serial && (
                          <span className="badge bg-secondary">{notification.device_serial}</span>
                        )}
                        {notification.batch_code && (
                          <span className="badge bg-info ms-1">
                            {notification.batch_code} ({notification.affected_count})
                          </span>
                        )}
                      </td>
                      <td>
                        <small>{format(new Date(notification.created_at), 'dd/MM/yyyy HH:mm', { locale: es })}</small>
                      </td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <Button variant="outline-primary" size="sm" onClick={() => handleShowDetail(notification)}>
                            <i className="bi bi-eye"></i>
                          </Button>
                          {notification.status === 'pending' && (
                            <>
                              <Button
                                variant="outline-info"
                                size="sm"
                                onClick={() => handleMarkAsRead(notification.id)}
                              >
                                <i className="bi bi-check"></i>
                              </Button>
                              <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() => handleShowResolve(notification)}
                              >
                                <i className="bi bi-check-circle"></i>
                              </Button>
                            </>
                          )}
                          <Button variant="outline-danger" size="sm" onClick={() => handleDelete(notification.id)}>
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
        {/* Pagination */}
        {!loading && notifications.length > 0 && (
          <Card.Footer className="d-flex justify-content-between align-items-center">
            <div>
              <small className="text-muted">
                Mostrando {(currentPage - 1) * limit + 1} a {Math.min(currentPage * limit, total)} de {total}
              </small>
            </div>
            <div>
              <Button
                variant="outline-primary"
                size="sm"
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="me-2"
              >
                <i className="bi bi-chevron-left"></i> Anterior
              </Button>
              <span className="mx-2">
                Página {currentPage} de {totalPages}
              </span>
              <Button
                variant="outline-primary"
                size="sm"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Siguiente <i className="bi bi-chevron-right"></i>
              </Button>
            </div>
          </Card.Footer>
        )}
      </Card>

      {/* Detail Modal */}
      <Modal show={showDetailModal} onHide={() => setShowDetailModal(false)} size="lg">
        <Modal.Header closeButton className="gradient-primary text-white">
          <Modal.Title>
            <i className="bi bi-info-circle me-2"></i>
            Detalle de Notificación
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedNotification && (
            <div>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Tipo:</Col>
                <Col sm={8}>{getTypeLabel(selectedNotification.type)}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Prioridad:</Col>
                <Col sm={8}>
                  <Badge bg={getPriorityVariant(selectedNotification.priority)}>
                    {selectedNotification.priority.toUpperCase()}
                  </Badge>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Estado:</Col>
                <Col sm={8}>
                  <Badge bg={getStatusVariant(selectedNotification.status)}>
                    {getStatusLabel(selectedNotification.status)}
                  </Badge>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Título:</Col>
                <Col sm={8}>{selectedNotification.title}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Mensaje:</Col>
                <Col sm={8}>{selectedNotification.message}</Col>
              </Row>
              {selectedNotification.device_serial && (
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Serie:</Col>
                  <Col sm={8}>{selectedNotification.device_serial}</Col>
                </Row>
              )}
              {selectedNotification.batch_code && (
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Lote:</Col>
                  <Col sm={8}>
                    {selectedNotification.batch_code} ({selectedNotification.affected_count} dispositivos)
                  </Col>
                </Row>
              )}
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Fecha Creación:</Col>
                <Col sm={8}>
                  {format(new Date(selectedNotification.created_at), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}
                </Col>
              </Row>
              {selectedNotification.read_at && (
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Fecha Lectura:</Col>
                  <Col sm={8}>
                    {format(new Date(selectedNotification.read_at), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}
                  </Col>
                </Row>
              )}
              {selectedNotification.resolved_at && (
                <>
                  <Row className="mb-3">
                    <Col sm={4} className="fw-bold">Fecha Resolución:</Col>
                    <Col sm={8}>
                      {format(new Date(selectedNotification.resolved_at), "dd/MM/yyyy 'a las' HH:mm", {
                        locale: es,
                      })}
                    </Col>
                  </Row>
                  {selectedNotification.resolution_notes && (
                    <Row className="mb-3">
                      <Col sm={4} className="fw-bold">Notas:</Col>
                      <Col sm={8}>{selectedNotification.resolution_notes}</Col>
                    </Row>
                  )}
                </>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Resolve Modal */}
      <Modal show={showResolveModal} onHide={() => setShowResolveModal(false)}>
        <Modal.Header closeButton className="gradient-primary text-white">
          <Modal.Title>
            <i className="bi bi-check-circle me-2"></i>
            Resolver Notificación
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedNotification && (
            <div>
              <p>
                <strong>{selectedNotification.title}</strong>
              </p>
              <p className="text-muted">{selectedNotification.message}</p>
              <Form.Group className="mb-3">
                <Form.Label>Notas de Resolución (opcional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="Describe cómo se resolvió esta notificación..."
                />
              </Form.Group>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowResolveModal(false)}>
            Cancelar
          </Button>
          <Button variant="success" onClick={handleResolve}>
            <i className="bi bi-check-circle me-1"></i>
            Resolver
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}
