/**
 * Database Tab - MongoDB information and statistics
 */

import { useState, useEffect } from 'react'
import { Row, Col, Card, ListGroup, Badge, Button, Alert, Table } from 'react-bootstrap'

export default function DatabaseTab() {
  const [stats, setStats] = useState({
    collections: 12,
    totalDocuments: 1,
    totalSize: '1.2 MB',
    avgObjSize: '512 bytes'
  })

  const collections = [
    { name: 'devices', documents: 0, size: '0 KB', indexes: 5 },
    { name: 'device_events', documents: 0, size: '0 KB', indexes: 3 },
    { name: 'movimientos', documents: 0, size: '0 KB', indexes: 4 },
    { name: 'employees', documents: 1, size: '1 KB', indexes: 3 },
    { name: 'customers', documents: 0, size: '0 KB', indexes: 2 },
    { name: 'production_orders', documents: 0, size: '0 KB', indexes: 3 },
    { name: 'quality_controls', documents: 0, size: '0 KB', indexes: 2 },
    { name: 'service_tickets', documents: 0, size: '0 KB', indexes: 2 },
    { name: 'rma_cases', documents: 0, size: '0 KB', indexes: 2 },
    { name: 'inventory_items', documents: 0, size: '0 KB', indexes: 2 },
    { name: 'metrics', documents: 0, size: '0 KB', indexes: 2 },
    { name: 'settings', documents: 0, size: '0 KB', indexes: 1 }
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">Base de Datos MongoDB</h5>
        <Button variant="outline-primary" size="sm">
          <i className="bi bi-arrow-clockwise me-2"></i>
          Actualizar
        </Button>
      </div>

      {/* Database Info */}
      <Row className="g-3 mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="bi bi-collection-fill text-primary" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2 mb-0">{stats.collections}</h3>
              <small className="text-muted">Colecciones</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="bi bi-file-earmark-text-fill text-success" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2 mb-0">{stats.totalDocuments}</h3>
              <small className="text-muted">Documentos</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="bi bi-hdd-fill text-info" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2 mb-0">{stats.totalSize}</h3>
              <small className="text-muted">Tamaño Total</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="bi bi-file-binary-fill text-warning" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2 mb-0">{stats.avgObjSize}</h3>
              <small className="text-muted">Tamaño Promedio</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Connection Info */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <i className="bi bi-plug me-2"></i>
              Información de Conexión
            </Card.Header>
            <ListGroup variant="flush">
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Host:</span>
                <strong>localhost</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Puerto:</span>
                <strong>27018</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Base de Datos:</span>
                <strong>ose_platform</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Versión:</span>
                <strong>MongoDB 7.0</strong>
              </ListGroup.Item>
            </ListGroup>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>
              <i className="bi bi-gear me-2"></i>
              Configuración
            </Card.Header>
            <ListGroup variant="flush">
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Min Pool Size:</span>
                <strong>10</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Max Pool Size:</span>
                <strong>50</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">Timeout:</span>
                <strong>5000 ms</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between">
                <span className="text-muted">ODM:</span>
                <strong>Beanie</strong>
              </ListGroup.Item>
            </ListGroup>
          </Card>
        </Col>
      </Row>

      {/* Collections Table */}
      <Card>
        <Card.Header>
          <i className="bi bi-folder2-open me-2"></i>
          Colecciones
        </Card.Header>
        <Card.Body className="p-0">
          <Table hover responsive className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Nombre</th>
                <th className="text-end">Documentos</th>
                <th className="text-end">Tamaño</th>
                <th className="text-end">Índices</th>
                <th className="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {collections.map(col => (
                <tr key={col.name}>
                  <td>
                    <i className="bi bi-collection me-2 text-primary"></i>
                    <strong>{col.name}</strong>
                  </td>
                  <td className="text-end">
                    {col.documents === 0 ? (
                      <span className="text-muted">{col.documents}</span>
                    ) : (
                      <Badge bg="primary">{col.documents}</Badge>
                    )}
                  </td>
                  <td className="text-end">
                    <small className="text-muted">{col.size}</small>
                  </td>
                  <td className="text-end">
                    <Badge bg="info">{col.indexes}</Badge>
                  </td>
                  <td className="text-end">
                    <Button variant="outline-secondary" size="sm">
                      <i className="bi bi-eye"></i>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {/* Backup Section */}
      <Card className="mt-3">
        <Card.Header>
          <i className="bi bi-cloud-download me-2"></i>
          Respaldos
        </Card.Header>
        <Card.Body>
          <Alert variant="info" className="mb-3">
            <i className="bi bi-info-circle me-2"></i>
            Los respaldos automáticos están configurados para ejecutarse diariamente a las 02:00 AM.
          </Alert>
          <div className="d-flex gap-2">
            <Button variant="primary">
              <i className="bi bi-download me-2"></i>
              Crear Respaldo Ahora
            </Button>
            <Button variant="outline-secondary">
              <i className="bi bi-clock-history me-2"></i>
              Ver Historial
            </Button>
          </div>
        </Card.Body>
      </Card>
    </div>
  )
}
