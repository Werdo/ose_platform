/**
 * OSE Platform - Dashboard Page
 * Design based on Assetflow SimplifiedKPICards + Dashboard
 */

import { Container, Row, Col, Card } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

// KPI Data
const kpiData = [
  {
    title: 'Total Usuarios',
    value: '156',
    icon: 'bi-people-fill',
    color: '#667eea',
    trend: '+12%',
  },
  {
    title: 'Usuarios Activos',
    value: '142',
    icon: 'bi-person-check-fill',
    color: '#28a745',
    trend: '+8%',
  },
  {
    title: 'Total Productos',
    value: '1,234',
    icon: 'bi-box-seam-fill',
    color: '#ffc107',
    trend: '+23%',
  },
  {
    title: 'Ordenes Pendientes',
    value: '45',
    icon: 'bi-hourglass-split',
    color: '#dc3545',
    trend: '-5%',
  },
  {
    title: 'RMA Abiertos',
    value: '12',
    icon: 'bi-ticket-perforated-fill',
    color: '#17a2b8',
    trend: '-3%',
  },
  {
    title: 'Facturas Generadas',
    value: '89',
    icon: 'bi-receipt-cutoff',
    color: '#6610f2',
    trend: '+15%',
  },
  {
    title: 'Notificaciones',
    value: '234',
    icon: 'bi-bell-fill',
    color: '#fd7e14',
    trend: '+10%',
  },
  {
    title: 'Picking Lists',
    value: '67',
    icon: 'bi-list-check',
    color: '#0d6efd',
    trend: '+18%',
  },
]

// Quick Access Apps
const quickAccessApps = [
  {
    title: 'Notificación de Series',
    description: 'Gestión de notificaciones de números de serie',
    icon: 'bi-bell-fill',
    color: '#667eea',
    link: '/app1',
  },
  {
    title: 'Importación de Datos',
    description: 'Importar datos desde archivos Excel',
    icon: 'bi-file-earmark-arrow-down-fill',
    color: '#28a745',
    link: '/app2',
  },
  {
    title: 'RMA & Tickets',
    description: 'Gestión de devoluciones y tickets',
    icon: 'bi-ticket-perforated-fill',
    color: '#ffc107',
    link: '/app3',
  },
  {
    title: 'Transform Data',
    description: 'Transformación y procesamiento de datos',
    icon: 'bi-arrow-repeat',
    color: '#17a2b8',
    link: '/app4',
  },
  {
    title: 'Generación de Facturas',
    description: 'Crear y gestionar facturas',
    icon: 'bi-receipt-cutoff',
    color: '#dc3545',
    link: '/app5',
  },
  {
    title: 'Picking & Etiquetado',
    description: 'Gestión de palets y paquetería con tracking',
    icon: 'bi-box-seam-fill',
    color: '#6610f2',
    link: 'http://localhost:5012',
    external: true,
  },
]

export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <Container fluid className="py-4">
      {/* Welcome Section */}
      <Row className="mb-4">
        <Col>
          <h2 className="mb-1">
            Bienvenido, {user?.name} {user?.surname}
          </h2>
          <p className="text-muted">
            <i className="bi bi-calendar3 me-2"></i>
            {new Date().toLocaleDateString('es-ES', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </Col>
      </Row>

      {/* KPI Cards */}
      <Row className="g-3 mb-4">
        {kpiData.map((kpi, index) => (
          <Col key={index} xs={12} sm={6} md={4} lg={3}>
            <Card className="h-100 border-0 shadow-sm card-hover">
              <Card.Body className="d-flex align-items-center">
                {/* Icon */}
                <div
                  className="icon-badge me-3"
                  style={{
                    backgroundColor: `${kpi.color}20`,
                    color: kpi.color,
                  }}
                >
                  <i className={`bi ${kpi.icon}`}></i>
                </div>

                {/* Text & Value */}
                <div className="flex-grow-1">
                  <div className="text-muted text-uppercase small mb-1" style={{ fontSize: '0.75rem' }}>
                    {kpi.title}
                  </div>
                  <div className="d-flex align-items-center">
                    <h4 className="mb-0 me-2">{kpi.value}</h4>
                    <small className={kpi.trend.startsWith('+') ? 'text-success' : 'text-danger'}>
                      {kpi.trend}
                    </small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Quick Access Section */}
      <Row className="mb-4">
        <Col>
          <h4 className="mb-3">
            <i className="bi bi-grid-3x3-gap-fill me-2"></i>
            Acceso Rápido a Aplicaciones
          </h4>
        </Col>
      </Row>

      <Row className="g-3 mb-4">
        {quickAccessApps.map((app, index) => (
          <Col key={index} xs={12} md={6} lg={4}>
            <Card className="h-100 border-0 shadow-sm card-hover">
              <Card.Body>
                <div className="d-flex align-items-start mb-3">
                  <div
                    className="icon-badge me-3"
                    style={{
                      backgroundColor: `${app.color}20`,
                      color: app.color,
                      width: '56px',
                      height: '56px',
                      fontSize: '1.75rem',
                    }}
                  >
                    <i className={`bi ${app.icon}`}></i>
                  </div>
                  <div>
                    <h5 className="mb-1">{app.title}</h5>
                    <p className="text-muted small mb-0">{app.description}</p>
                  </div>
                </div>
                {app.external ? (
                  <a
                    href={app.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-sm btn-outline-primary w-100"
                  >
                    <i className="bi bi-box-arrow-up-right me-1"></i>
                    Abrir Aplicación
                  </a>
                ) : (
                  <Link to={app.link} className="btn btn-sm btn-outline-primary w-100">
                    <i className="bi bi-arrow-right-circle me-1"></i>
                    Abrir Aplicación
                  </Link>
                )}
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* System Status */}
      <Row>
        <Col lg={6}>
          <Card className="border-0 shadow-sm">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-activity me-2"></i>
              Estado del Sistema
            </Card.Header>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
                <div>
                  <i className="bi bi-server text-primary me-2"></i>
                  API Backend
                </div>
                <span className="badge badge-gradient-success">Operativo</span>
              </div>
              <div className="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
                <div>
                  <i className="bi bi-database text-success me-2"></i>
                  Base de Datos
                </div>
                <span className="badge badge-gradient-success">Conectado</span>
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <i className="bi bi-cloud text-info me-2"></i>
                  Almacenamiento
                </div>
                <span className="badge bg-info text-white">75% Usado</span>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className="mt-3 mt-lg-0">
          <Card className="border-0 shadow-sm">
            <Card.Header className="gradient-primary text-white fw-bold">
              <i className="bi bi-clock-history me-2"></i>
              Actividad Reciente
            </Card.Header>
            <Card.Body>
              <div className="mb-3 pb-3 border-bottom">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <div className="fw-bold mb-1">
                      <i className="bi bi-person-plus text-success me-2"></i>
                      Nuevo usuario registrado
                    </div>
                    <small className="text-muted">Hace 15 minutos</small>
                  </div>
                </div>
              </div>
              <div className="mb-3 pb-3 border-bottom">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <div className="fw-bold mb-1">
                      <i className="bi bi-file-earmark-check text-primary me-2"></i>
                      Importación completada
                    </div>
                    <small className="text-muted">Hace 1 hora</small>
                  </div>
                </div>
              </div>
              <div>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <div className="fw-bold mb-1">
                      <i className="bi bi-ticket text-warning me-2"></i>
                      Nuevo ticket creado
                    </div>
                    <small className="text-muted">Hace 2 horas</small>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}
