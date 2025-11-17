/**
 * OSE Platform - Route Configuration
 * Protected routes with role-based access control
 */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Spinner } from 'react-bootstrap'

// Layouts
import MainLayout from '../components/layout/MainLayout'

// Pages
import LoginPage from '../pages/auth/LoginPage'
import DashboardPage from '../pages/dashboard/DashboardPage'
import ProfilePage from '../pages/ProfilePage'
import SettingsPage from '../pages/SettingsPage'
import NotFoundPage from '../pages/NotFoundPage'
import SeriesNotificationPage from '../pages/notifications/SeriesNotificationPage'
import DataImportPage from '../pages/import/DataImportPage'
import RmaTicketsPage from '../pages/rma/RmaTicketsPage'
import TransformImportPage from '../pages/transform/TransformImportPage'
import BackendConfigPage from '../pages/admin/BackendConfigPage'
import SystemLogsPage from '../pages/admin/SystemLogsPage'
import BrandUpdatePage from '../pages/admin/BrandUpdatePage'
import InvoiceManagementPage from '../pages/invoice/InvoiceManagementPage'
import PickingPortalPage from '../pages/picking/PickingPortalPage'
import ICCIDCalculatorPage from '../pages/iccid/ICCIDCalculatorPage'

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode
  requiresAuth?: boolean
  requiresAdmin?: boolean
}

function ProtectedRoute({
  children,
  requiresAuth = true,
  requiresAdmin = false
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth()

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
      </div>
    )
  }

  // Check authentication
  if (requiresAuth && !isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Check admin role
  if (requiresAdmin && user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

// Main App Routes
export default function AppRoutes() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      {/* Public Route - Login */}
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
        }
      />

      {/* Protected Routes - Main Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        {/* Redirect root to dashboard */}
        <Route index element={<Navigate to="/dashboard" replace />} />

        {/* Dashboard */}
        <Route path="dashboard" element={<DashboardPage />} />

        {/* Profile */}
        <Route path="profile" element={<ProfilePage />} />

        {/* Settings */}
        <Route path="settings" element={<SettingsPage />} />

        {/* App 1: Notificación de Series */}
        <Route path="app1" element={<SeriesNotificationPage />} />
        <Route path="notifications" element={<SeriesNotificationPage />} />

        {/* App 2: Importación de Datos */}
        <Route path="app2" element={<DataImportPage />} />
        <Route path="import" element={<DataImportPage />} />

        {/* App 3: RMA & Tickets */}
        <Route path="app3" element={<RmaTicketsPage />} />
        <Route path="rma" element={<RmaTicketsPage />} />

        {/* App 4: Transform Data */}
        <Route path="app4" element={<TransformImportPage />} />
        <Route path="transform" element={<TransformImportPage />} />

        {/* App 5: Generación de Facturas */}
        <Route path="app5" element={<InvoiceManagementPage />} />
        <Route path="invoice" element={<InvoiceManagementPage />} />

        {/* App 6: Picking Lists */}
        <Route path="app6" element={<PickingPortalPage />} />
        <Route path="picking" element={<PickingPortalPage />} />

        {/* App 8: Calculadora ICCID */}
        <Route path="app8" element={<ICCIDCalculatorPage />} />
        <Route path="iccid-calculator" element={<ICCIDCalculatorPage />} />

        {/* Admin - Backend Configuration */}
        <Route
          path="admin/backend"
          element={
            <ProtectedRoute requiresAdmin={true}>
              <BackendConfigPage />
            </ProtectedRoute>
          }
        />

        {/* Admin - System Logs */}
        <Route
          path="admin/logs"
          element={
            <ProtectedRoute requiresAdmin={true}>
              <SystemLogsPage />
            </ProtectedRoute>
          }
        />

        {/* Admin - Brand Update */}
        <Route
          path="admin/brand-update"
          element={
            <ProtectedRoute requiresAdmin={true}>
              <BrandUpdatePage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* 404 Not Found */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
