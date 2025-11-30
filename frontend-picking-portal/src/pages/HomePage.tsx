import { Link } from 'react-router-dom';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import { getStats } from '../services/api';
import type { Stats } from '../types/index';

const HomePage = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <div className="text-center mb-5">
        <h1 className="display-4 fw-bold text-primary mb-3">
          <i className="bi bi-box-seam me-3"></i>
          OSE Picking Portal
        </h1>
        <p className="lead text-muted">
          Sistema de gestión de picking para palets y paquetes
        </p>
      </div>

      {!loading && stats && (
        <Row className="mb-5">
          <Col md={3}>
            <Card className="text-center border-primary">
              <Card.Body>
                <h3 className="text-primary">{stats.palets.total}</h3>
                <p className="text-muted mb-0">Total Palets</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-warning">
              <Card.Body>
                <h3 className="text-warning">{stats.palets.preparados}</h3>
                <p className="text-muted mb-0">Palets Preparados</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-info">
              <Card.Body>
                <h3 className="text-info">{stats.paquetes.total}</h3>
                <p className="text-muted mb-0">Total Paquetes</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center border-success">
              <Card.Body>
                <h3 className="text-success">{stats.paquetes.enviados}</h3>
                <p className="text-muted mb-0">Paquetes Enviados</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      <Row className="g-4">
        <Col md={4}>
          <Link to="/palets" className="text-decoration-none">
            <Card className="h-100 hover-shadow border-0 shadow-sm picking-card">
              <Card.Body className="d-flex flex-column align-items-center justify-content-center p-4 text-center">
                <div className="mb-3">
                  <i className="bi bi-stack text-primary" style={{ fontSize: '4rem' }}></i>
                </div>
                <h3 className="fw-bold text-primary mb-2">Picking Palets</h3>
                <p className="text-muted mb-0">
                  Envíos grandes y consolidados
                </p>
                <div className="mt-3">
                  <span className="badge bg-primary px-3 py-2">
                    Acceder <i className="bi bi-arrow-right ms-2"></i>
                  </span>
                </div>
              </Card.Body>
            </Card>
          </Link>
        </Col>

        <Col md={4}>
          <Link to="/paquetes" className="text-decoration-none">
            <Card className="h-100 hover-shadow border-0 shadow-sm picking-card">
              <Card.Body className="d-flex flex-column align-items-center justify-content-center p-4 text-center">
                <div className="mb-3">
                  <i className="bi bi-box-seam text-success" style={{ fontSize: '4rem' }}></i>
                </div>
                <h3 className="fw-bold text-success mb-2">Picking Paquetes</h3>
                <p className="text-muted mb-0">
                  Paquetes individuales y envíos directos
                </p>
                <div className="mt-3">
                  <span className="badge bg-success px-3 py-2">
                    Acceder <i className="bi bi-arrow-right ms-2"></i>
                  </span>
                </div>
              </Card.Body>
            </Card>
          </Link>
        </Col>

        <Col md={4}>
          <Link to="/etiquetas" className="text-decoration-none">
            <Card className="h-100 hover-shadow border-0 shadow-sm picking-card">
              <Card.Body className="d-flex flex-column align-items-center justify-content-center p-4 text-center">
                <div className="mb-3">
                  <i className="bi bi-upc-scan text-warning" style={{ fontSize: '4rem' }}></i>
                </div>
                <h3 className="fw-bold text-warning mb-2">Albaranes y Etiquetas</h3>
                <p className="text-muted mb-0">
                  Códigos EST912 y generación de etiquetas
                </p>
                <div className="mt-3">
                  <span className="badge bg-warning text-dark px-3 py-2">
                    Acceder <i className="bi bi-arrow-right ms-2"></i>
                  </span>
                </div>
              </Card.Body>
            </Card>
          </Link>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
