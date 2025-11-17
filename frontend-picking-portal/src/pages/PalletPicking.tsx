import { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Alert, Badge, Modal } from 'react-bootstrap';
import { createPallet, getPallets } from '../services/api';
import type { Pallet } from '../types/index';
import QRCode from 'qrcode';

const PalletPicking = () => {
  const [pallets, setPallets] = useState<Pallet[]>([]);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'danger'; message: string } | null>(null);
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [selectedPallet, setSelectedPallet] = useState<Pallet | null>(null);

  const [formData, setFormData] = useState({
    pallet_number: '',
    tipo_contenido: '',
    contenido_ids: '',
    pedido_id: '',
    peso_kg: '',
    notas: '',
  });

  useEffect(() => {
    loadPallets();
  }, []);

  const loadPallets = async () => {
    try {
      const data = await getPallets(50);
      setPallets(data);
    } catch (error) {
      console.error('Error loading pallets:', error);
      showAlert('danger', 'Error al cargar los palets');
    }
  };

  const showAlert = (type: 'success' | 'danger', message: string) => {
    setAlert({ type, message });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.pallet_number.trim() || !formData.tipo_contenido.trim()) {
      showAlert('danger', 'Por favor, completa los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        pallet_number: formData.pallet_number.trim(),
        tipo_contenido: formData.tipo_contenido.trim(),
        contenido_ids: formData.contenido_ids.trim(),
        pedido_id: formData.pedido_id.trim() || undefined,
        peso_kg: formData.peso_kg ? parseFloat(formData.peso_kg) : undefined,
        notas: formData.notas.trim() || undefined,
        creado_por: 'operario@ose.com',
      };

      await createPallet(payload);
      showAlert('success', `Palet ${formData.pallet_number} creado exitosamente`);

      // Reset form
      setFormData({
        pallet_number: '',
        tipo_contenido: '',
        contenido_ids: '',
        pedido_id: '',
        peso_kg: '',
        notas: '',
      });

      // Reload pallets
      await loadPallets();
    } catch (error: any) {
      console.error('Error creating pallet:', error);
      const errorMsg = error.response?.data?.detail || 'Error al crear el palet';
      showAlert('danger', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const generateQRCode = async (pallet: Pallet) => {
    try {
      const qrData = JSON.stringify({
        type: 'pallet',
        id: pallet.id,
        pallet_number: pallet.pallet_number,
        tipo_contenido: pallet.tipo_contenido,
        pedido_id: pallet.pedido_id,
      });

      const url = await QRCode.toDataURL(qrData, {
        width: 400,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#ffffff',
        },
      });

      setQrCodeUrl(url);
      setSelectedPallet(pallet);
      setShowQRModal(true);
    } catch (error) {
      console.error('Error generating QR code:', error);
      showAlert('danger', 'Error al generar el código QR');
    }
  };

  const printQRCode = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow && selectedPallet) {
      printWindow.document.write(`
        <html>
          <head>
            <title>QR Code - ${selectedPallet.pallet_number}</title>
            <style>
              body {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
              }
              h1 { font-size: 24px; margin-bottom: 10px; }
              p { margin: 5px 0; }
              img { margin: 20px 0; }
              .info { text-align: center; }
            </style>
          </head>
          <body>
            <div class="info">
              <h1>OSE - Palet</h1>
              <p><strong>${selectedPallet.pallet_number}</strong></p>
              <p>${selectedPallet.tipo_contenido}</p>
              ${selectedPallet.pedido_id ? `<p>Pedido: ${selectedPallet.pedido_id}</p>` : ''}
            </div>
            <img src="${qrCodeUrl}" alt="QR Code" />
            <script>
              window.onload = () => {
                setTimeout(() => {
                  window.print();
                  window.close();
                }, 500);
              };
            </script>
          </body>
        </html>
      `);
      printWindow.document.close();
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: { [key: string]: string } = {
      pendiente: 'warning',
      picking: 'info',
      completado: 'success',
      enviado: 'primary',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status.toUpperCase()}</Badge>;
  };

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="display-6 fw-bold text-primary">
          <i className="bi bi-stack me-2"></i>
          Picking Palets
        </h1>
      </div>

      {alert && (
        <Alert variant={alert.type} dismissible onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <Row>
        <Col lg={4}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">
                <i className="bi bi-plus-circle me-2"></i>
                Crear Nuevo Palet
              </h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Número de Palet <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="pallet_number"
                    value={formData.pallet_number}
                    onChange={handleInputChange}
                    placeholder="Ej: PAL-2024-001"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    Tipo de Contenido <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="tipo_contenido"
                    value={formData.tipo_contenido}
                    onChange={handleInputChange}
                    placeholder="Ej: Dispositivos electrónicos"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Contenido IDs</Form.Label>
                  <Form.Control
                    type="text"
                    name="contenido_ids"
                    value={formData.contenido_ids}
                    onChange={handleInputChange}
                    placeholder="Ej: DEV001, DEV002, DEV003"
                  />
                  <Form.Text className="text-muted">
                    IDs separados por comas
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>ID de Pedido</Form.Label>
                  <Form.Control
                    type="text"
                    name="pedido_id"
                    value={formData.pedido_id}
                    onChange={handleInputChange}
                    placeholder="Ej: ORD-2024-001"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Peso (kg)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    name="peso_kg"
                    value={formData.peso_kg}
                    onChange={handleInputChange}
                    placeholder="Ej: 125.50"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Notas</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="notas"
                    value={formData.notas}
                    onChange={handleInputChange}
                    placeholder="Notas adicionales..."
                  />
                </Form.Group>

                <Button
                  variant="primary"
                  type="submit"
                  className="w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Creando...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle me-2"></i>
                      Crear Palet
                    </>
                  )}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8}>
          <Card className="shadow-sm">
            <Card.Header className="bg-light">
              <h5 className="mb-0">
                <i className="bi bi-list-ul me-2"></i>
                Palets Recientes
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              <div className="table-responsive">
                <Table hover className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Número</th>
                      <th>Tipo Contenido</th>
                      <th>Pedido</th>
                      <th>Peso (kg)</th>
                      <th>Estado</th>
                      <th>Fecha</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pallets.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="text-center text-muted py-4">
                          No hay palets registrados
                        </td>
                      </tr>
                    ) : (
                      pallets.map((pallet) => (
                        <tr key={pallet.id}>
                          <td className="fw-bold">{pallet.pallet_number}</td>
                          <td>{pallet.tipo_contenido}</td>
                          <td>{pallet.pedido_id || '-'}</td>
                          <td>{pallet.peso_kg ? `${pallet.peso_kg} kg` : '-'}</td>
                          <td>{getStatusBadge(pallet.status)}</td>
                          <td>{new Date(pallet.fecha_creacion).toLocaleDateString()}</td>
                          <td>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => generateQRCode(pallet)}
                              title="Generar código QR"
                            >
                              <i className="bi bi-qr-code"></i>
                            </Button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Modal show={showQRModal} onHide={() => setShowQRModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Código QR - {selectedPallet?.pallet_number}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center">
          {qrCodeUrl && (
            <>
              <img src={qrCodeUrl} alt="QR Code" className="img-fluid mb-3" />
              <div className="text-muted">
                <p className="mb-1"><strong>Tipo:</strong> {selectedPallet?.tipo_contenido}</p>
                {selectedPallet?.pedido_id && (
                  <p className="mb-1"><strong>Pedido:</strong> {selectedPallet.pedido_id}</p>
                )}
                {selectedPallet?.peso_kg && (
                  <p className="mb-1"><strong>Peso:</strong> {selectedPallet.peso_kg} kg</p>
                )}
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowQRModal(false)}>
            Cerrar
          </Button>
          <Button variant="primary" onClick={printQRCode}>
            <i className="bi bi-printer me-2"></i>
            Imprimir Etiqueta
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default PalletPicking;
