/**
 * OSE Platform - Main Layout with Sidebar
 * Design based on modern admin panels with lateral menu
 */

import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Navbar, Nav, Container, NavDropdown, Badge } from 'react-bootstrap'
import { useAuth } from '../../contexts/AuthContext'
import Sidebar from '../sidebar/Sidebar'

export default function MainLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  // Get role badge variant
  const getRoleBadge = (role: string) => {
    const variants: Record<string, string> = {
      super_admin: 'danger',
      admin: 'warning',
      supervisor: 'info',
      operator: 'primary',
      viewer: 'secondary',
    }
    return variants[role] || 'secondary'
  }

  return (
    <div className="d-flex flex-column" style={{ minHeight: '100vh' }}>
      {/* Top Navbar */}
      <Navbar bg="dark" variant="dark" expand="lg" sticky="top" className="shadow-sm" style={{ zIndex: 1030 }}>
        <Container fluid>
          {/* Brand */}
          <Navbar.Brand className="fw-bold">
            <i className="bi bi-grid-3x3-gap-fill me-2"></i>
            OSE Platform
          </Navbar.Brand>

          {/* Toggle for mobile */}
          <Navbar.Toggle aria-controls="main-navbar-nav" />

          {/* Navigation Links */}
          <Navbar.Collapse id="main-navbar-nav">
            <Nav className="me-auto">
              {/* Sidebar toggle button */}
              <button
                className="btn btn-sm btn-outline-light d-none d-lg-block"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                title="Toggle Sidebar"
              >
                <i className="bi bi-list"></i>
              </button>
            </Nav>

            {/* Right side - User Menu */}
            <Nav>
              {/* Notifications */}
              <Nav.Link className="position-relative">
                <i className="bi bi-bell fs-5"></i>
                <Badge
                  bg="danger"
                  pill
                  className="position-absolute top-0 start-100 translate-middle"
                  style={{ fontSize: '0.6rem' }}
                >
                  3
                </Badge>
              </Nav.Link>

              {/* User Dropdown */}
              <NavDropdown
                title={
                  <span>
                    <i className="bi bi-person-circle me-1"></i>
                    {user?.name} {user?.surname}
                    {user?.role && (
                      <Badge bg={getRoleBadge(user.role)} className="ms-2">
                        {user.role.replace('_', ' ')}
                      </Badge>
                    )}
                  </span>
                }
                id="user-dropdown"
                align="end"
              >
                <NavDropdown.Item disabled className="small text-muted">
                  {user?.email}
                </NavDropdown.Item>
                <NavDropdown.Divider />
                <NavDropdown.Item onClick={handleLogout}>
                  <i className="bi bi-box-arrow-right me-2 text-danger"></i>
                  Cerrar Sesión
                </NavDropdown.Item>
              </NavDropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Main Content with Sidebar */}
      <div className="d-flex flex-grow-1">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

        {/* Main Content Area */}
        <main
          className="flex-grow-1"
          style={{
            marginLeft: sidebarOpen ? '280px' : '70px',
            transition: 'margin-left 0.3s ease',
            backgroundColor: '#f8f9fa',
            minHeight: 'calc(100vh - 56px)',
            paddingTop: '0'
          }}
        >
          <Outlet />
        </main>
      </div>

      {/* Footer */}
      <footer
        className="bg-dark text-light py-3 text-center"
        style={{
          marginLeft: sidebarOpen ? '280px' : '70px',
          transition: 'margin-left 0.3s ease'
        }}
      >
        <Container>
          <small>© 2025 OSE Platform 2.0 - Oversun Energy | Todos los derechos reservados</small>
        </Container>
      </footer>
    </div>
  )
}
