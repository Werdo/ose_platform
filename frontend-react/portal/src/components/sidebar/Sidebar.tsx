/**
 * OSE Platform - Sidebar Component
 * Lateral menu with applications based on user permissions
 */

import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Nav, Collapse } from 'react-bootstrap'
import { useAuth } from '../../contexts/AuthContext'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

interface AppItem {
  id: number
  name: string
  shortName: string
  route: string
  icon: string
  color: string
  permission: string
}

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const location = useLocation()
  const { user } = useAuth()
  const [applicationsOpen, setApplicationsOpen] = useState(true)

  // Definición de todas las aplicaciones
  const allApps: AppItem[] = [
    {
      id: 1,
      name: 'Notificación de Series',
      shortName: 'Series',
      route: '/app1',
      icon: 'bi-bell-fill',
      color: '#0d6efd',
      permission: 'app1_access'
    },
    {
      id: 2,
      name: 'Importación de Datos',
      shortName: 'Import',
      route: '/app2',
      icon: 'bi-file-earmark-arrow-down-fill',
      color: '#198754',
      permission: 'app2_access'
    },
    {
      id: 3,
      name: 'RMA & Tickets',
      shortName: 'Soporte',
      route: '/app3',
      icon: 'bi-ticket-perforated-fill',
      color: '#ffc107',
      permission: 'app3_access'
    },
    {
      id: 4,
      name: 'Transform Data',
      shortName: 'Transform',
      route: '/app4',
      icon: 'bi-arrow-repeat',
      color: '#0dcaf0',
      permission: 'app4_access'
    },
    {
      id: 5,
      name: 'Facturas',
      shortName: 'Facturas',
      route: '/app5',
      icon: 'bi-receipt-cutoff',
      color: '#dc3545',
      permission: 'app5_access'
    },
    {
      id: 6,
      name: 'Picking Lists',
      shortName: 'Picking',
      route: '/app6',
      icon: 'bi-box-seam-fill',
      color: '#6c757d',
      permission: 'app6_access'
    }
  ]

  // Verificar si el usuario tiene acceso a una app
  const hasAccess = (app: AppItem) => {
    // Super admin tiene acceso a todo
    if (user?.role === 'super_admin') return true
    // Verificar permiso específico de la app
    return user?.permissions?.[app.permission] === true
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <>
      {/* Sidebar */}
      <div
        className={`sidebar bg-dark text-light ${isOpen ? 'open' : 'closed'}`}
        style={{
          width: isOpen ? '280px' : '70px',
          minHeight: '100vh',
          transition: 'width 0.3s ease',
          position: 'fixed',
          top: '56px', // Height of navbar
          left: 0,
          bottom: 0,
          overflowY: 'auto',
          overflowX: 'hidden',
          zIndex: 1000,
          borderRight: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        {/* Toggle Button */}
        <div className="p-3 border-bottom border-secondary">
          <button
            className="btn btn-sm btn-outline-light w-100"
            onClick={onToggle}
            title={isOpen ? 'Cerrar menú' : 'Abrir menú'}
          >
            <i className={`bi ${isOpen ? 'bi-chevron-left' : 'bi-chevron-right'}`}></i>
            {isOpen && <span className="ms-2">Cerrar</span>}
          </button>
        </div>

        <Nav className="flex-column pt-3">
          {/* Dashboard */}
          <Nav.Link
            as={Link}
            to="/dashboard"
            className={`px-3 py-2 mb-1 ${isActive('/dashboard') ? 'bg-primary text-white' : 'text-light'}`}
            title="Dashboard"
          >
            <i className="bi bi-speedometer2 me-3" style={{ fontSize: '1.2rem' }}></i>
            {isOpen && <span>Dashboard</span>}
          </Nav.Link>

          {/* Aplicaciones Section */}
          <div className="px-3 py-2 mt-3">
            <div
              className="d-flex align-items-center justify-content-between text-muted"
              style={{ cursor: 'pointer', userSelect: 'none' }}
              onClick={() => setApplicationsOpen(!applicationsOpen)}
            >
              {isOpen && (
                <>
                  <small className="text-uppercase fw-bold">Aplicaciones</small>
                  <i className={`bi ${applicationsOpen ? 'bi-chevron-down' : 'bi-chevron-right'}`}></i>
                </>
              )}
              {!isOpen && <i className="bi bi-grid-fill"></i>}
            </div>
          </div>

          <Collapse in={applicationsOpen}>
            <div>
              {allApps.map(app => {
                const allowed = hasAccess(app)
                return (
                  <Nav.Link
                    key={app.id}
                    as={allowed ? Link : 'div'}
                    to={allowed ? app.route : undefined}
                    className={`px-3 py-2 mb-1 ${
                      allowed
                        ? (isActive(app.route) ? 'bg-primary text-white' : 'text-light')
                        : 'text-muted disabled'
                    }`}
                    style={{
                      cursor: allowed ? 'pointer' : 'not-allowed',
                      opacity: allowed ? 1 : 0.5,
                      pointerEvents: allowed ? 'auto' : 'none'
                    }}
                    title={allowed ? app.name : `${app.name} (Sin acceso)`}
                  >
                    <i
                      className={`${app.icon} me-3`}
                      style={{
                        fontSize: '1.2rem',
                        color: allowed
                          ? (isActive(app.route) ? 'white' : app.color)
                          : '#6c757d'
                      }}
                    ></i>
                    {isOpen && (
                      <span>
                        {app.shortName}
                        {!allowed && <i className="bi bi-lock-fill ms-2" style={{ fontSize: '0.8rem' }}></i>}
                      </span>
                    )}
                  </Nav.Link>
                )
              })}
            </div>
          </Collapse>

          {/* Admin Section */}
          {(user?.role === 'super_admin' || user?.role === 'admin') && (
            <>
              <hr className="border-secondary my-3" />
              <Nav.Link
                as={Link}
                to="/admin/backend"
                className={`px-3 py-2 mb-1 ${isActive('/admin/backend') ? 'bg-primary text-white' : 'text-light'}`}
                title="Administración"
              >
                <i className="bi bi-server me-3" style={{ fontSize: '1.2rem' }}></i>
                {isOpen && <span>Administración</span>}
              </Nav.Link>
              <Nav.Link
                as={Link}
                to="/admin/logs"
                className={`px-3 py-2 mb-1 ${isActive('/admin/logs') ? 'bg-primary text-white' : 'text-light'}`}
                title="Logs del Sistema"
              >
                <i className="bi bi-journal-text me-3" style={{ fontSize: '1.2rem' }}></i>
                {isOpen && <span>Logs del Sistema</span>}
              </Nav.Link>
              <Nav.Link
                as={Link}
                to="/admin/brand-update"
                className={`px-3 py-2 mb-1 ${isActive('/admin/brand-update') ? 'bg-primary text-white' : 'text-light'}`}
                title="Actualización de Marcas"
              >
                <i className="bi bi-tag-fill me-3" style={{ fontSize: '1.2rem' }}></i>
                {isOpen && <span>Actualizar Marcas</span>}
              </Nav.Link>
            </>
          )}

          {/* Settings */}
          <hr className="border-secondary my-3" />
          <Nav.Link
            as={Link}
            to="/profile"
            className={`px-3 py-2 mb-1 ${isActive('/profile') ? 'bg-primary text-white' : 'text-light'}`}
            title="Mi Perfil"
          >
            <i className="bi bi-person-fill me-3" style={{ fontSize: '1.2rem' }}></i>
            {isOpen && <span>Mi Perfil</span>}
          </Nav.Link>

          <Nav.Link
            as={Link}
            to="/settings"
            className={`px-3 py-2 mb-1 ${isActive('/settings') ? 'bg-primary text-white' : 'text-light'}`}
            title="Configuración"
          >
            <i className="bi bi-gear-fill me-3" style={{ fontSize: '1.2rem' }}></i>
            {isOpen && <span>Configuración</span>}
          </Nav.Link>
        </Nav>

        {/* Footer info (only when open) */}
        {isOpen && (
          <div className="mt-auto p-3 border-top border-secondary" style={{ fontSize: '0.75rem' }}>
            <div className="text-muted">
              <div className="mb-1">
                <i className="bi bi-person-badge me-2"></i>
                {user?.name} {user?.surname}
              </div>
              <div className="mb-1">
                <i className="bi bi-shield-check me-2"></i>
                {user?.role}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="sidebar-backdrop d-lg-none"
          style={{
            position: 'fixed',
            top: '56px',
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 999
          }}
          onClick={onToggle}
        />
      )}
    </>
  )
}
