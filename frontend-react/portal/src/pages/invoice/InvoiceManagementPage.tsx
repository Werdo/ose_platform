/**
 * App 5: Invoice Management Page
 * Sistema de gestión de facturas desde tickets
 */

import { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Tabs, Tab, Alert, Spinner } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import toast from 'react-hot-toast'
import type { InvoiceStats } from '../../types/invoice'
import TicketTable from '../../components/invoice/TicketTable'
import InvoiceTable from '../../components/invoice/InvoiceTable'
import ConfigurationForm from '../../components/invoice/ConfigurationForm'

export default function InvoiceManagementPage() {
  const [stats, setStats] = useState<InvoiceStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('tickets')

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      const response = await apiService.get('/api/app5/stats')
      setStats(response.stats)
      setError(null)
    } catch (err: any) {
      setError('Error cargando estadísticas')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDataChange = () => {
    loadStatistics()
  }

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">
                <i className="bi bi-receipt-cutoff me-2 text-success"></i>
                App 5: Generación de Facturas
              </h2>
              <p className="text-muted mb-0">
                Gestión de tickets, facturas y configuración de facturación
              </p>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2 text-muted">Cargando estadísticas...</p>
        </div>
      ) : stats ? (
        <Row className="g-3 mb-4">
          <Col xs={12} sm={6} md={3}>
            <Card className="border-0 shadow-sm stat-card border-primary">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="text-muted text-uppercase small mb-1">Tickets Totales</div>
                    <h3 className="mb-0">{stats.total_tickets}</h3>
                  </div>
                  <div className="icon-badge primary">
                    <i className="bi bi-receipt"></i>
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
                    <h3 className="mb-0">{stats.pending_tickets}</h3>
                  </div>
                  <div className="icon-badge warning">
                    <i className="bi bi-hourglass-split"></i>
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
                    <div className="text-muted text-uppercase small mb-1">Facturas Emitidas</div>
                    <h3 className="mb-0">{stats.issued_invoices}</h3>
                  </div>
                  <div className="icon-badge success">
                    <i className="bi bi-check-circle-fill"></i>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} md={3}>
            <Card className="border-0 shadow-sm stat-card border-info">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="text-muted text-uppercase small mb-1">Facturado (Mes)</div>
                    <h3 className="mb-0">{stats.month_amount.toFixed(2)} €</h3>
                  </div>
                  <div className="icon-badge info">
                    <i className="bi bi-currency-euro"></i>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : null}

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k || 'tickets')}
        className="mb-4"
      >
        <Tab
          eventKey="tickets"
          title={
            <>
              <i className="bi bi-receipt me-2"></i>
              Tickets
            </>
          }
        >
          <TicketTable onDataChange={handleDataChange} />
        </Tab>

        <Tab
          eventKey="invoices"
          title={
            <>
              <i className="bi bi-file-earmark-text me-2"></i>
              Facturas
            </>
          }
        >
          <InvoiceTable onDataChange={handleDataChange} />
        </Tab>

        <Tab
          eventKey="config"
          title={
            <>
              <i className="bi bi-gear me-2"></i>
              Configuración
            </>
          }
        >
          <ConfigurationForm />
        </Tab>
      </Tabs>
    </Container>
  )
}
