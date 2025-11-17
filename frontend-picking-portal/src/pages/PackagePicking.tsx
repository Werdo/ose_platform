import { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Alert, Badge, Modal } from 'react-bootstrap';
import { createPackage, getPackages, markAsSent, sendNotification } from '../services/api';
import type { Package, TransportistType } from '../types/index';
import QRCode from 'qrcode';

const TRANSPORTISTAS: TransportistType[] = ['Seur', 'Correos', 'DHL', 'UPS', 'FedEx'];

const PackagePicking = () => {
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'danger'; message: string } | null>(null);
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [selectedPackage, setSelectedPackage] = useState<Package | null>(null);
  const [actionLoading, setActionLoading] = useState<{ [key: number]: boolean }>({});

  const [formData, setFormData] = useState({
    tracking_number: '',
    transportista: 'Seur' as TransportistType,
    order_code: '',
    cliente_email: '',
    cliente_nombre: '',
    dispositivos_info: '',
    peso_kg: '',
    notas: '',
  });

  useEffect(() => {
    loadPackages();
  }, []);

  const loadPackages = async () => {
    try {
      const data = await getPackages(50);
      setPackages(data);
    } catch (error) {
      console.error('Error loading packages:', error);
      showAlert('danger', 'Error al cargar los paquetes');
    }
  };

  const showAlert = (type: 'success' | 'danger', message: string) => {
    setAlert({ type, message });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.tracking_number.trim() || !formData.transportista) {
      showAlert('danger', 'Por favor, completa los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        tracking_number: formData.tracking_number.trim(),
        transportista: formData.transportista,
        order_code: formData.order_code.trim() || undefined,
        cliente_email: formData.cliente_email.trim() || undefined,
        cliente_nombre: formData.cliente_nombre.trim() || undefined,
        dispositivos_info: formData.dispositivos_info.trim() || undefined,
        peso_kg: formData.peso_kg ? parseFloat(formData.peso_kg) : undefined,
        notas: formData.notas.trim() || undefined,
        creado_por: 'operario@ose.com',
      };

      await createPackage(payload);
      showAlert('success', `Paquete ${formData.tracking_number} creado exitosamente`);

      // Reset form
      setFormData({
        tracking_number: '',
        transportista: 'Seur',
        order_code: '',
        cliente_email: '',
        cliente_nombre: '',
        dispositivos_info: '',
        peso_kg: '',
        notas: '',
      });

      // Reload packages
      await loadPackages();
    } catch (error: any) {
      console.error('Error creating package:', error);
      const errorMsg = error.response?.data?.detail || 'Error al crear el paquete';
      showAlert('danger', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsSent = async (pkg: Package) => {
    if (window.confirm(`¿Marcar el paquete ${pkg.tracking_number} como enviado?`)) {
      setActionLoading((prev) => ({ ...prev, [pkg.id]: true }));
      try {
        await markAsSent(pkg.id);
        showAlert('success', `Paquete ${pkg.tracking_number} marcado como enviado`);
        await loadPackages();
      } catch (error: any) {
        console.error('Error marking as sent:', error);
        const errorMsg = error.response?.data?.detail || 'Error al marcar como enviado';
        showAlert('danger', errorMsg);
      } finally {
        setActionLoading((prev) => ({ ...prev, [pkg.id]: false }));
      }
    }
  };

  const handleSendNotification = async (pkg: Package) => {
    if (!pkg.cliente_email) {
      showAlert('danger', 'El paquete no tiene email de cliente registrado');
      return;
    }

    if (window.confirm(`¿Enviar notificación al cliente ${pkg.cliente_email}?`)) {
      setActionLoading((prev) => ({ ...prev, [pkg.id]: true }));
      try {
        await sendNotification(pkg.id);
        showAlert('success', `Notificación enviada a ${pkg.cliente_email}`);
        await loadPackages();
      } catch (error: any) {
        console.error('Error sending notification:', error);
        const errorMsg = error.response?.data?.detail || 'Error al enviar la notificación';
        showAlert('danger', errorMsg);
      } finally {
        setActionLoading((prev) => ({ ...prev, [pkg.id]: false }));
      }
    }
  };

  const generateQRCode = async (pkg: Package) => {
    try {
      const qrData = JSON.stringify({
        type: 'package',
        id: pkg.id,
        tracking_number: pkg.tracking_number,
        transportista: pkg.transportista,
        order_code: pkg.order_code,
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
      setSelectedPackage(pkg);
      setShowQRModal(true);
    } catch (error) {
      console.error('Error generating QR code:', error);
      showAlert('danger', 'Error al generar el código QR');
    }
  };

  const printQRCode = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow && selectedPackage) {
      printWindow.document.write(`
        <html>
          <head>
            <title>QR Code - ${selectedPackage.tracking_number}</title>
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
              <h1>OSE - Paquete</h1>
              <p><strong>${selectedPackage.tracking_number}</strong></p>
              <p>${selectedPackage.transportista}</p>
              ${selectedPackage.order_code ? `<p>Pedido: ${selectedPackage.order_code}</p>` : ''}
              ${selectedPackage.cliente_nombre ? `<p>Cliente: ${selectedPackage.cliente_nombre}</p>` : ''}
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
      preparado: 'info',
      enviado: 'success',
      entregado: 'primary',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status.toUpperCase()}</Badge>;
  };

  const getTransportistaIcon = (transportista: string) => {
    const icons: { [key: string]: string } = {
      Seur: 'truck',
      Correos: 'envelope',
      DHL: 'airplane',
      UPS: 'box-seam',
      FedEx: 'lightning',
    };
    return icons[transportista] || 'truck';
  };

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="display-6 fw-bold text-success">
          <i className="bi bi-box-seam me-2"></i>
          Picking Paquetes
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
            <Card.Header className="bg-success text-white">
              <h5 className="mb-0">
                <i className="bi bi-plus-circle me-2"></i>
                Crear Nuevo Paquete
              </h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Número de Seguimiento <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="tracking_number"
                    value={formData.tracking_number}
                    onChange={handleInputChange}
                    placeholder="Ej: SEUR123456789"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    Transportista <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Select
                    name="transportista"
                    value={formData.transportista}
                    onChange={handleInputChange}
                    required
                  >
                    {TRANSPORTISTAS.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Código de Pedido</Form.Label>
                  <Form.Control
                    type="text"
                    name="order_code"
                    value={formData.order_code}
                    onChange={handleInputChange}
                    placeholder="Ej: ORD-2024-001"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Email del Cliente</Form.Label>
                  <Form.Control
                    type="email"
                    name="cliente_email"
                    value={formData.cliente_email}
                    onChange={handleInputChange}
                    placeholder="cliente@ejemplo.com"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Nombre del Cliente</Form.Label>
                  <Form.Control
                    type="text"
                    name="cliente_nombre"
                    value={formData.cliente_nombre}
                    onChange={handleInputChange}
                    placeholder="Juan Pérez"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Información de Dispositivos</Form.Label>
                  <Form.Control
                    type="text"
                    name="dispositivos_info"
                    value={formData.dispositivos_info}
                    onChange={handleInputChange}
                    placeholder="Ej: 2x Laptops, 1x Monitor"
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
                    placeholder="Ej: 5.50"
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
                  variant="success"
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
                      Crear Paquete
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
                Paquetes Recientes
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              <div className="table-responsive">
                <Table hover className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Tracking</th>
                      <th>Transportista</th>
                      <th>Cliente</th>
                      <th>Peso</th>
                      <th>Estado</th>
                      <th>Fecha</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {packages.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="text-center text-muted py-4">
                          No hay paquetes registrados
                        </td>
                      </tr>
                    ) : (
                      packages.map((pkg) => (
                        <tr key={pkg.id}>
                          <td className="fw-bold">{pkg.tracking_number}</td>
                          <td>
                            <i className={`bi bi-${getTransportistaIcon(pkg.transportista)} me-1`}></i>
                            {pkg.transportista}
                          </td>
                          <td>
                            {pkg.cliente_nombre || '-'}
                            {pkg.cliente_email && (
                              <div className="small text-muted">{pkg.cliente_email}</div>
                            )}
                          </td>
                          <td>{pkg.peso_kg ? `${pkg.peso_kg} kg` : '-'}</td>
                          <td>{getStatusBadge(pkg.status)}</td>
                          <td>
                            {new Date(pkg.fecha_creacion).toLocaleDateString()}
                            {pkg.fecha_envio && (
                              <div className="small text-success">
                                Enviado: {new Date(pkg.fecha_envio).toLocaleDateString()}
                              </div>
                            )}
                          </td>
                          <td>
                            <div className="btn-group" role="group">
                              <Button
                                variant="outline-primary"
                                size="sm"
                                onClick={() => generateQRCode(pkg)}
                                title="Generar código QR"
                              >
                                <i className="bi bi-qr-code"></i>
                              </Button>
                              {pkg.status !== 'enviado' && (
                                <Button
                                  variant="outline-success"
                                  size="sm"
                                  onClick={() => handleMarkAsSent(pkg)}
                                  disabled={actionLoading[pkg.id]}
                                  title="Marcar como enviado"
                                >
                                  {actionLoading[pkg.id] ? (
                                    <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                  ) : (
                                    <i className="bi bi-check-circle"></i>
                                  )}
                                </Button>
                              )}
                              {pkg.cliente_email && (
                                <Button
                                  variant="outline-info"
                                  size="sm"
                                  onClick={() => handleSendNotification(pkg)}
                                  disabled={actionLoading[pkg.id]}
                                  title="Enviar notificación"
                                >
                                  {actionLoading[pkg.id] ? (
                                    <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                  ) : (
                                    <i className="bi bi-envelope"></i>
                                  )}
                                </Button>
                              )}
                            </div>
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
          <Modal.Title>Código QR - {selectedPackage?.tracking_number}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center">
          {qrCodeUrl && (
            <>
              <img src={qrCodeUrl} alt="QR Code" className="img-fluid mb-3" />
              <div className="text-muted">
                <p className="mb-1">
                  <i className={`bi bi-${getTransportistaIcon(selectedPackage?.transportista || '')} me-2`}></i>
                  <strong>Transportista:</strong> {selectedPackage?.transportista}
                </p>
                {selectedPackage?.order_code && (
                  <p className="mb-1"><strong>Pedido:</strong> {selectedPackage.order_code}</p>
                )}
                {selectedPackage?.cliente_nombre && (
                  <p className="mb-1"><strong>Cliente:</strong> {selectedPackage.cliente_nombre}</p>
                )}
                {selectedPackage?.peso_kg && (
                  <p className="mb-1"><strong>Peso:</strong> {selectedPackage.peso_kg} kg</p>
                )}
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowQRModal(false)}>
            Cerrar
          </Button>
          <Button variant="success" onClick={printQRCode}>
            <i className="bi bi-printer me-2"></i>
            Imprimir Etiqueta
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default PackagePicking;
