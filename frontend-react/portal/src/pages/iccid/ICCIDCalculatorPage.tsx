/**
 * OSE Platform - App 8: Calculadora de ICCID
 * Generación de lotes de ICCID con análisis completo
 */

import { useState, useEffect } from 'react';
import {
  Container, Row, Col, Card, Button, Alert, Table,
  Form, Modal, Tabs, Tab, Spinner, Badge
} from 'react-bootstrap';
import { apiService } from '../../services/api.service';
import toast from 'react-hot-toast';

interface ICCIDBatch {
  _id: string;
  batch_name: string;
  description: string;
  iccid_start: string;
  iccid_end: string;
  total_count: number;
  iccids: string[];
  analyses: ICCIDAnalysis[];
  stats: {
    total_count: number;
    valid_count: number;
    invalid_count: number;
    operators: { [key: string]: number };
    countries: { [key: string]: number };
  };
  created_by: string;
  created_at: string;
  csv_download_count: number;
}

interface ICCIDAnalysis {
  iccid: string;
  iccid_raw: string;
  length: number;
  valid_length: boolean;
  mii: string;
  country_code_guess: string;
  country_name_guess: string;
  iin_prefix: string;
  iin_profile: {
    brand: string;
    operator: string;
    country: string;
    region: string;
    use_case: string;
    core_network: string;
  } | null;
  account_number: string;
  checksum: string;
  luhn_valid: boolean;
  warnings: string[];
}

interface GlobalStats {
  total_batches: number;
  total_iccids: number;
  top_operators: Array<{ operator: string; count: number }>;
  top_countries: Array<{ country: string; count: number }>;
}

export default function ICCIDCalculatorPage() {
  const [activeTab, setActiveTab] = useState<string>('generator');

  // Generator State
  const [batchName, setBatchName] = useState('');
  const [description, setDescription] = useState('');
  const [iccidStart, setIccidStart] = useState('');
  const [iccidEnd, setIccidEnd] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedBatch, setGeneratedBatch] = useState<ICCIDBatch | null>(null);

  // Analyze State
  const [singleIccid, setSingleIccid] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ICCIDAnalysis | null>(null);

  // History State
  const [batches, setBatches] = useState<ICCIDBatch[]>([]);
  const [loadingBatches, setLoadingBatches] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<ICCIDBatch | null>(null);

  // Stats State
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    if (activeTab === 'history') {
      loadBatches();
    } else if (activeTab === 'stats') {
      loadGlobalStats();
    }
  }, [activeTab]);

  // ═════════════════════════════════════════════════════════════════
  // GENERATOR FUNCTIONS
  // ═════════════════════════════════════════════════════════════════

  const handleGenerateBatch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!batchName || !iccidStart || !iccidEnd) {
      toast.error('Por favor complete todos los campos obligatorios');
      return;
    }

    // Validar que sean ICCIDs válidos (19-22 dígitos)
    if (!iccidStart.match(/^\d{19,22}$/) || !iccidEnd.match(/^\d{19,22}$/)) {
      toast.error('Los ICCIDs deben tener 19-22 dígitos numéricos');
      return;
    }

    // Validar que tengan la misma longitud
    if (iccidStart.length !== iccidEnd.length) {
      toast.error('Los ICCIDs deben tener la misma longitud');
      return;
    }

    setGenerating(true);
    setGeneratedBatch(null);

    try {
      const response = await apiService.post('/api/v1/app8/iccid-calculator/batches/generate', {
        batch_name: batchName,
        description: description || undefined,
        iccid_start: iccidStart,
        iccid_end: iccidEnd
      });

      setGeneratedBatch(response.batch);
      toast.success(`Lote generado: ${response.total_count} ICCIDs`);

      // Reset form
      setBatchName('');
      setDescription('');
      setIccidStart('');
      setIccidEnd('');
    } catch (error: any) {
      console.error('Error generating batch:', error);
      toast.error(error.response?.data?.detail || 'Error al generar el lote');
    } finally {
      setGenerating(false);
    }
  };

  // ═════════════════════════════════════════════════════════════════
  // ANALYZE FUNCTIONS
  // ═════════════════════════════════════════════════════════════════

  const handleAnalyzeIccid = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!singleIccid) {
      toast.error('Por favor ingrese un ICCID');
      return;
    }

    setAnalyzing(true);
    setAnalysis(null);

    try {
      const response = await apiService.post('/api/v1/app8/iccid-calculator/analyze', {
        iccid: singleIccid
      });

      setAnalysis(response.analysis);
      toast.success('ICCID analizado correctamente');
    } catch (error: any) {
      console.error('Error analyzing ICCID:', error);
      toast.error(error.response?.data?.detail || 'Error al analizar el ICCID');
    } finally {
      setAnalyzing(false);
    }
  };

  // ═════════════════════════════════════════════════════════════════
  // HISTORY FUNCTIONS
  // ═════════════════════════════════════════════════════════════════

  const loadBatches = async () => {
    setLoadingBatches(true);
    try {
      const response = await apiService.get('/api/v1/app8/iccid-calculator/batches');
      setBatches(response.batches || []);
    } catch (error: any) {
      console.error('Error loading batches:', error);
      toast.error('Error al cargar el historial');
    } finally {
      setLoadingBatches(false);
    }
  };

  const handleViewDetails = async (batchId: string) => {
    try {
      const response = await apiService.get(`/api/v1/app8/iccid-calculator/batches/${batchId}`);
      setSelectedBatch(response.batch);
      setShowDetailsModal(true);
    } catch (error: any) {
      console.error('Error loading batch details:', error);
      toast.error('Error al cargar detalles del lote');
    }
  };

  const handleDownloadCSV = async (batchId: string, batchName: string) => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${API_URL}/api/v1/app8/iccid-calculator/batches/${batchId}/csv`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Error al descargar el CSV');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `iccids_${batchName.replace(/ /g, '_')}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('CSV descargado correctamente');
      loadBatches(); // Reload to update download count
    } catch (error: any) {
      console.error('Error downloading CSV:', error);
      toast.error('Error al descargar el CSV');
    }
  };

  const handleDeleteBatch = async (batchId: string) => {
    if (!window.confirm('¿Está seguro de eliminar este lote?')) {
      return;
    }

    try {
      await apiService.delete(`/api/v1/app8/iccid-calculator/batches/${batchId}`);
      toast.success('Lote eliminado correctamente');
      loadBatches();
    } catch (error: any) {
      console.error('Error deleting batch:', error);
      toast.error(error.response?.data?.detail || 'Error al eliminar el lote');
    }
  };

  // ═════════════════════════════════════════════════════════════════
  // STATS FUNCTIONS
  // ═════════════════════════════════════════════════════════════════

  const loadGlobalStats = async () => {
    setLoadingStats(true);
    try {
      const response = await apiService.get('/api/v1/app8/iccid-calculator/stats/global');
      setGlobalStats(response.stats);
    } catch (error: any) {
      console.error('Error loading stats:', error);
      toast.error('Error al cargar estadísticas');
    } finally {
      setLoadingStats(false);
    }
  };

  // ═════════════════════════════════════════════════════════════════
  // RENDER
  // ═════════════════════════════════════════════════════════════════

  return (
    <Container fluid className="p-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex align-items-center gap-3">
            <i className="bi bi-calculator-fill text-primary" style={{ fontSize: '2rem' }}></i>
            <div>
              <h1 className="mb-1">App 8: Calculadora de ICCID</h1>
              <p className="text-muted mb-0">
                Genera lotes de ICCIDs con análisis completo de operador, país y validación
              </p>
            </div>
          </div>
        </Col>
      </Row>

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k || 'generator')}
        className="mb-4"
      >
        {/* ══════════════════════════════════════════════════════════ */}
        {/* TAB 1: GENERATOR */}
        {/* ══════════════════════════════════════════════════════════ */}
        <Tab eventKey="generator" title={<><i className="bi bi-calculator-fill me-2"></i>Generar Lote</>}>
          <Row>
            <Col lg={6}>
              <Card className="mb-4">
                <Card.Header>
                  <i className="bi bi-plus-circle me-2"></i>
                  Nuevo Lote de ICCIDs
                </Card.Header>
                <Card.Body>
                  <Form onSubmit={handleGenerateBatch}>
                    <Form.Group className="mb-3">
                      <Form.Label>Nombre del Lote *</Form.Label>
                      <Form.Control
                        type="text"
                        value={batchName}
                        onChange={(e) => setBatchName(e.target.value)}
                        placeholder="Ej: Lote IoT Enero 2025"
                        required
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Descripción</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={2}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Descripción opcional del lote"
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>ICCID Inicial (completo) *</Form.Label>
                      <Form.Control
                        type="text"
                        value={iccidStart}
                        onChange={(e) => setIccidStart(e.target.value.trim())}
                        placeholder="Ej: 89882390001334701795"
                        required
                      />
                      <Form.Text className="text-muted">
                        ICCID completo de inicio del rango (19-22 dígitos). Se recalculará el checksum.
                      </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>ICCID Final (completo) *</Form.Label>
                      <Form.Control
                        type="text"
                        value={iccidEnd}
                        onChange={(e) => setIccidEnd(e.target.value.trim())}
                        placeholder="Ej: 89882390001334801785"
                        required
                      />
                      <Form.Text className="text-muted">
                        ICCID completo final del rango (19-22 dígitos). Debe tener la misma longitud que el inicial.
                      </Form.Text>
                    </Form.Group>

                    {iccidStart && iccidEnd && iccidStart.length === iccidEnd.length && (
                      <Alert variant="info">
                        <i className="bi bi-info-circle me-2"></i>
                        Se generarán aproximadamente {(() => {
                          try {
                            const startBody = parseInt(iccidStart.slice(0, -1));
                            const endBody = parseInt(iccidEnd.slice(0, -1));
                            return Math.max(0, endBody - startBody + 1).toLocaleString();
                          } catch {
                            return '...';
                          }
                        })()} ICCIDs
                      </Alert>
                    )}

                    <div className="d-grid">
                      <Button
                        type="submit"
                        variant="primary"
                        size="lg"
                        disabled={generating}
                      >
                        {generating ? (
                          <>
                            <Spinner animation="border" size="sm" className="me-2" />
                            Generando...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-play-fill me-2"></i>
                            Generar Lote
                          </>
                        )}
                      </Button>
                    </div>
                  </Form>
                </Card.Body>
              </Card>
            </Col>

            <Col lg={6}>
              {generatedBatch && (
                <Card className="border-success">
                  <Card.Header className="bg-success text-white">
                    <i className="bi bi-check-circle me-2"></i>
                    Lote Generado Correctamente
                  </Card.Header>
                  <Card.Body>
                    <h5>{generatedBatch.batch_name}</h5>
                    {generatedBatch.description && (
                      <p className="text-muted">{generatedBatch.description}</p>
                    )}

                    <Table bordered size="sm" className="mb-3">
                      <tbody>
                        <tr>
                          <th>ICCID Base:</th>
                          <td><code>{generatedBatch.base_iccid}</code></td>
                        </tr>
                        <tr>
                          <th>Rango:</th>
                          <td>{generatedBatch.start_number} - {generatedBatch.end_number}</td>
                        </tr>
                        <tr>
                          <th>Total ICCIDs:</th>
                          <td><Badge bg="primary">{generatedBatch.total_count}</Badge></td>
                        </tr>
                        <tr>
                          <th>Válidos:</th>
                          <td><Badge bg="success">{generatedBatch.stats.valid_count}</Badge></td>
                        </tr>
                        <tr>
                          <th>Inválidos:</th>
                          <td><Badge bg="danger">{generatedBatch.stats.invalid_count}</Badge></td>
                        </tr>
                      </tbody>
                    </Table>

                    {/* Operators */}
                    <h6>Operadores:</h6>
                    <div className="mb-3">
                      {Object.entries(generatedBatch.stats.operators).map(([op, count]) => (
                        <Badge key={op} bg="info" className="me-2 mb-2">
                          {op}: {count}
                        </Badge>
                      ))}
                    </div>

                    {/* Countries */}
                    <h6>Países:</h6>
                    <div className="mb-3">
                      {Object.entries(generatedBatch.stats.countries).map(([country, count]) => (
                        <Badge key={country} bg="secondary" className="me-2 mb-2">
                          {country}: {count}
                        </Badge>
                      ))}
                    </div>

                    <div className="d-grid gap-2">
                      <Button
                        variant="success"
                        onClick={() => handleDownloadCSV(generatedBatch._id, generatedBatch.batch_name)}
                      >
                        <i className="bi bi-download me-2"></i>
                        Descargar CSV
                      </Button>
                      <Button
                        variant="outline-secondary"
                        onClick={() => {
                          setActiveTab('history');
                          setGeneratedBatch(null);
                        }}
                      >
                        <i className="bi bi-clock-history me-2"></i>
                        Ver en Historial
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              )}
            </Col>
          </Row>
        </Tab>

        {/* ══════════════════════════════════════════════════════════ */}
        {/* TAB 2: ANALYZE */}
        {/* ══════════════════════════════════════════════════════════ */}
        <Tab eventKey="analyze" title={<><i className="bi bi-search me-2"></i>Analizar ICCID</>}>
          <Row>
            <Col lg={6}>
              <Card>
                <Card.Header>
                  <i className="bi bi-search me-2"></i>
                  Analizar ICCID Individual
                </Card.Header>
                <Card.Body>
                  <Form onSubmit={handleAnalyzeIccid}>
                    <Form.Group className="mb-3">
                      <Form.Label>ICCID Completo</Form.Label>
                      <Form.Control
                        type="text"
                        value={singleIccid}
                        onChange={(e) => setSingleIccid(e.target.value)}
                        placeholder="Ej: 8988226010000000019"
                        required
                      />
                      <Form.Text className="text-muted">
                        Ingrese el ICCID completo (con checksum)
                      </Form.Text>
                    </Form.Group>

                    <div className="d-grid">
                      <Button
                        type="submit"
                        variant="primary"
                        disabled={analyzing}
                      >
                        {analyzing ? (
                          <>
                            <Spinner animation="border" size="sm" className="me-2" />
                            Analizando...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-search me-2"></i>
                            Analizar
                          </>
                        )}
                      </Button>
                    </div>
                  </Form>
                </Card.Body>
              </Card>
            </Col>

            <Col lg={6}>
              {analysis && (
                <Card className={`border-${analysis.luhn_valid ? 'success' : 'danger'}`}>
                  <Card.Header className={`bg-${analysis.luhn_valid ? 'success' : 'danger'} text-white`}>
                    {analysis.luhn_valid ? (
                      <>
                        <i className="bi bi-check-circle-fill me-2"></i>
                        ICCID Válido
                      </>
                    ) : (
                      <>
                        <i className="bi bi-x-circle-fill me-2"></i>
                        ICCID Inválido
                      </>
                    )}
                  </Card.Header>
                  <Card.Body>
                    <Table bordered size="sm">
                      <tbody>
                        <tr>
                          <th>ICCID:</th>
                          <td><code>{analysis.iccid}</code></td>
                        </tr>
                        <tr>
                          <th>Longitud:</th>
                          <td>{analysis.length} dígitos</td>
                        </tr>
                        <tr>
                          <th>MII:</th>
                          <td><code>{analysis.mii}</code></td>
                        </tr>
                        <tr>
                          <th>País:</th>
                          <td>
                            <Badge bg="secondary">
                              {analysis.country_code_guess}
                            </Badge>
                            {' '}
                            {analysis.country_name_guess}
                          </td>
                        </tr>
                        <tr>
                          <th>IIN Prefix:</th>
                          <td><code>{analysis.iin_prefix}</code></td>
                        </tr>
                        <tr>
                          <th>Account Number:</th>
                          <td><code>{analysis.account_number}</code></td>
                        </tr>
                        <tr>
                          <th>Checksum:</th>
                          <td><code>{analysis.checksum}</code></td>
                        </tr>
                      </tbody>
                    </Table>

                    {analysis.iin_profile && (
                      <>
                        <h6 className="mt-3">Información del Operador:</h6>
                        <Table bordered size="sm">
                          <tbody>
                            <tr>
                              <th>Operador:</th>
                              <td>{analysis.iin_profile.operator}</td>
                            </tr>
                            <tr>
                              <th>Marca:</th>
                              <td>{analysis.iin_profile.brand}</td>
                            </tr>
                            <tr>
                              <th>País:</th>
                              <td>{analysis.iin_profile.country}</td>
                            </tr>
                            <tr>
                              <th>Región:</th>
                              <td>{analysis.iin_profile.region}</td>
                            </tr>
                            <tr>
                              <th>Caso de Uso:</th>
                              <td>{analysis.iin_profile.use_case}</td>
                            </tr>
                            <tr>
                              <th>Red:</th>
                              <td>{analysis.iin_profile.core_network}</td>
                            </tr>
                          </tbody>
                        </Table>
                      </>
                    )}

                    {analysis.warnings && analysis.warnings.length > 0 && (
                      <Alert variant="warning" className="mt-3">
                        <strong>Advertencias:</strong>
                        <ul className="mb-0 mt-2">
                          {analysis.warnings.map((warning, idx) => (
                            <li key={idx}>{warning}</li>
                          ))}
                        </ul>
                      </Alert>
                    )}
                  </Card.Body>
                </Card>
              )}
            </Col>
          </Row>
        </Tab>

        {/* ══════════════════════════════════════════════════════════ */}
        {/* TAB 3: HISTORY */}
        {/* ══════════════════════════════════════════════════════════ */}
        <Tab eventKey="history" title={<><i className="bi bi-clock-history me-2"></i>Historial</>}>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>
                <i className="bi bi-clock-history me-2"></i>
                Historial de Lotes Generados
              </span>
              <Button
                variant="outline-primary"
                size="sm"
                onClick={loadBatches}
                disabled={loadingBatches}
              >
                <i className="bi bi-arrow-clockwise me-2"></i>
                Actualizar
              </Button>
            </Card.Header>
            <Card.Body>
              {loadingBatches ? (
                <div className="text-center py-5">
                  <Spinner animation="border" variant="primary" />
                  <p className="mt-3 text-muted">Cargando historial...</p>
                </div>
              ) : batches.length === 0 ? (
                <Alert variant="info">
                  <i className="bi bi-info-circle me-2"></i>
                  No hay lotes generados todavía. Crea tu primer lote en la pestaña "Generar Lote".
                </Alert>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Nombre</th>
                      <th>Base ICCID</th>
                      <th>Total ICCIDs</th>
                      <th>Válidos</th>
                      <th>Fecha</th>
                      <th>Descargas</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {batches.map((batch) => (
                      <tr key={batch._id}>
                        <td>
                          <strong>{batch.batch_name}</strong>
                          {batch.description && (
                            <div className="small text-muted">{batch.description}</div>
                          )}
                        </td>
                        <td><code>{batch.base_iccid}</code></td>
                        <td>
                          <Badge bg="primary">{batch.total_count}</Badge>
                        </td>
                        <td>
                          <Badge bg="success">
                            <i className="bi bi-check-circle-fill me-1"></i>
                            {batch.stats.valid_count}
                          </Badge>
                        </td>
                        <td className="small">
                          {new Date(batch.created_at).toLocaleString('es-ES')}
                        </td>
                        <td>
                          <Badge bg="secondary">{batch.csv_download_count}</Badge>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => handleViewDetails(batch._id)}
                            >
                              <i className="bi bi-eye"></i>
                            </Button>
                            <Button
                              variant="outline-success"
                              size="sm"
                              onClick={() => handleDownloadCSV(batch._id, batch.batch_name)}
                            >
                              <i className="bi bi-download"></i>
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleDeleteBatch(batch._id)}
                            >
                              <i className="bi bi-trash"></i>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        {/* ══════════════════════════════════════════════════════════ */}
        {/* TAB 4: STATS */}
        {/* ══════════════════════════════════════════════════════════ */}
        <Tab eventKey="stats" title={<><i className="bi bi-bar-chart-fill me-2"></i>Estadísticas</>}>
          {loadingStats ? (
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-3 text-muted">Cargando estadísticas...</p>
            </div>
          ) : globalStats ? (
            <Row>
              <Col md={6} className="mb-4">
                <Card>
                  <Card.Header>
                    <i className="bi bi-graph-up me-2"></i>
                    Estadísticas Globales
                  </Card.Header>
                  <Card.Body>
                    <Table bordered>
                      <tbody>
                        <tr>
                          <th>Total de Lotes Generados:</th>
                          <td>
                            <Badge bg="primary" className="fs-6">
                              {globalStats.total_batches}
                            </Badge>
                          </td>
                        </tr>
                        <tr>
                          <th>Total de ICCIDs Generados:</th>
                          <td>
                            <Badge bg="success" className="fs-6">
                              {globalStats.total_iccids.toLocaleString()}
                            </Badge>
                          </td>
                        </tr>
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              </Col>

              <Col md={6} className="mb-4">
                <Card>
                  <Card.Header>
                    <i className="bi bi-building me-2"></i>
                    Top 10 Operadores
                  </Card.Header>
                  <Card.Body>
                    {globalStats.top_operators.length > 0 ? (
                      <Table striped hover size="sm">
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>Operador</th>
                            <th>ICCIDs</th>
                          </tr>
                        </thead>
                        <tbody>
                          {globalStats.top_operators.map((item, idx) => (
                            <tr key={idx}>
                              <td>{idx + 1}</td>
                              <td>{item.operator}</td>
                              <td>
                                <Badge bg="info">{item.count.toLocaleString()}</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    ) : (
                      <p className="text-muted">No hay datos disponibles</p>
                    )}
                  </Card.Body>
                </Card>
              </Col>

              <Col md={6} className="mb-4">
                <Card>
                  <Card.Header>
                    <i className="bi bi-globe me-2"></i>
                    Top 10 Países
                  </Card.Header>
                  <Card.Body>
                    {globalStats.top_countries.length > 0 ? (
                      <Table striped hover size="sm">
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>País</th>
                            <th>ICCIDs</th>
                          </tr>
                        </thead>
                        <tbody>
                          {globalStats.top_countries.map((item, idx) => (
                            <tr key={idx}>
                              <td>{idx + 1}</td>
                              <td>{item.country}</td>
                              <td>
                                <Badge bg="secondary">{item.count.toLocaleString()}</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    ) : (
                      <p className="text-muted">No hay datos disponibles</p>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          ) : (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              No hay estadísticas disponibles. Genera algunos lotes primero.
            </Alert>
          )}
        </Tab>
      </Tabs>

      {/* ═════════════════════════════════════════════════════════════════ */}
      {/* BATCH DETAILS MODAL */}
      {/* ═════════════════════════════════════════════════════════════════ */}
      <Modal
        show={showDetailsModal}
        onHide={() => setShowDetailsModal(false)}
        size="xl"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-info-circle me-2"></i>
            Detalles del Lote
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedBatch && (
            <>
              <h5>{selectedBatch.batch_name}</h5>
              {selectedBatch.description && (
                <p className="text-muted">{selectedBatch.description}</p>
              )}

              <Table bordered size="sm" className="mb-4">
                <tbody>
                  <tr>
                    <th>ICCID Inicial:</th>
                    <td><code>{selectedBatch.iccid_start}</code></td>
                  </tr>
                  <tr>
                    <th>ICCID Final:</th>
                    <td><code>{selectedBatch.iccid_end}</code></td>
                  </tr>
                  <tr>
                    <th>Total ICCIDs:</th>
                    <td><Badge bg="primary">{selectedBatch.total_count}</Badge></td>
                  </tr>
                  <tr>
                    <th>Creado por:</th>
                    <td>{selectedBatch.created_by}</td>
                  </tr>
                  <tr>
                    <th>Fecha de creación:</th>
                    <td>{new Date(selectedBatch.created_at).toLocaleString('es-ES')}</td>
                  </tr>
                </tbody>
              </Table>

              <h6>Vista Previa de ICCIDs (primeros 10):</h6>
              <div className="border rounded p-3 mb-3" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {selectedBatch.iccids.slice(0, 10).map((iccid, idx) => (
                  <div key={idx} className="font-monospace mb-1">
                    {iccid}
                    {selectedBatch.analyses[idx]?.luhn_valid ? (
                      <Badge bg="success" className="ms-2">Válido</Badge>
                    ) : (
                      <Badge bg="danger" className="ms-2">Inválido</Badge>
                    )}
                  </div>
                ))}
                {selectedBatch.iccids.length > 10 && (
                  <div className="text-muted mt-2">
                    ... y {selectedBatch.iccids.length - 10} más
                  </div>
                )}
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          {selectedBatch && (
            <Button
              variant="success"
              onClick={() => {
                handleDownloadCSV(selectedBatch._id, selectedBatch.batch_name);
                setShowDetailsModal(false);
              }}
            >
              <i className="bi bi-download me-2"></i>
              Descargar CSV Completo
            </Button>
          )}
          <Button variant="secondary" onClick={() => setShowDetailsModal(false)}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}
