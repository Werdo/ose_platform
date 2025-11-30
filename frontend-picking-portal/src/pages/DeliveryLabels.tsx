import { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Table,
  Button,
  Form,
  Modal,
  Badge,
  Spinner,
  Alert,
  InputGroup,
  ButtonGroup,
} from 'react-bootstrap';
import * as deliveryService from '../services/delivery-notes';
import type { DeliveryNote } from '../services/delivery-notes';

const DeliveryLabels = () => {
  // State
  const [deliveryNotes, setDeliveryNotes] = useState<DeliveryNote[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [nextCode, setNextCode] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showLabelModal, setShowLabelModal] = useState(false);
  const [showZplModal, setShowZplModal] = useState(false);
  const [selectedNote, setSelectedNote] = useState<DeliveryNote | null>(null);

  // Form Data
  const [formData, setFormData] = useState({
    delivery_note_number: '',
    customer_name: '',
    total_boxes: 1,
    order_number: '',
    product_description: '',
    total_pallets_in_order: 1,
    pallet_number_in_order: 1,
    labels_to_print: 1,
  });

  // Label Config
  const [labelConfig, setLabelConfig] = useState({
    labelsCount: 1,
    labelSize: 'A6' as 'A6' | '100x150' | '100x100',
  });

  const [zplConfig, setZplConfig] = useState({
    dpi: 203,
    labelWidth: 100,
    labelHeight: 150,
  });

  const [zplCode, setZplCode] = useState<string>('');

  useEffect(() => {
    loadDeliveryNotes();
    loadStats();
    loadNextCode();
  }, [filterStatus]);

  const loadDeliveryNotes = async () => {
    try {
      setLoading(true);
      const response = await deliveryService.getDeliveryNotes({ status: filterStatus });
      setDeliveryNotes(response.delivery_notes || []);
    } catch (error) {
      console.error('Error loading delivery notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await deliveryService.getStatistics();
      setStats(response.stats);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadNextCode = async () => {
    try {
      const response = await deliveryService.previewNextCode();
      setNextCode(response.next_code || '');
    } catch (error) {
      console.error('Error loading next code:', error);
    }
  };

  const handleCreateDeliveryNote = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await deliveryService.createDeliveryNote(formData);
      alert('Albarán creado correctamente');
      setShowCreateModal(false);
      resetForm();
      loadDeliveryNotes();
      loadNextCode();
    } catch (error) {
      console.error('Error creating delivery note:', error);
      alert('Error al crear albarán');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (noteId: string, status: string) => {
    try {
      await deliveryService.updateStatus(noteId, status);
      alert('Estado actualizado');
      loadDeliveryNotes();
      loadStats();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Error al actualizar estado');
    }
  };

  const handleGeneratePdfLabel = async () => {
    if (!selectedNote || !selectedNote.id) return;
    try {
      setLoading(true);
      const blob = await deliveryService.generatePdfLabel(
        selectedNote.id,
        labelConfig.labelsCount,
        labelConfig.labelSize
      );
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `etiqueta_${selectedNote.pallet_code}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      alert('PDF generado correctamente');
      setShowLabelModal(false);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error al generar PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateZplLabel = async () => {
    if (!selectedNote || !selectedNote.id) return;
    try {
      setLoading(true);
      const response = await deliveryService.generateZplLabel(
        selectedNote.id,
        zplConfig.dpi,
        zplConfig.labelWidth,
        zplConfig.labelHeight
      );
      setZplCode(response.zpl_code);
      alert('Código ZPL generado');
    } catch (error) {
      console.error('Error generating ZPL:', error);
      alert('Error al generar ZPL');
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewLabel = async (note: DeliveryNote) => {
    if (!note.id) return;
    try {
      const htmlContent = await deliveryService.generateHtmlPreview(note.id);
      const previewWindow = window.open('', '_blank');
      if (previewWindow) {
        previewWindow.document.write(htmlContent);
        previewWindow.document.close();
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      alert('Error al generar preview');
    }
  };

  const copyZplToClipboard = () => {
    navigator.clipboard.writeText(zplCode);
    alert('Código ZPL copiado');
  };

  const resetForm = () => {
    setFormData({
      delivery_note_number: '',
      customer_name: '',
      total_boxes: 1,
      order_number: '',
      product_description: '',
      total_pallets_in_order: 1,
      pallet_number_in_order: 1,
      labels_to_print: 1,
    });
  };

  const getStatusBadge = (status: string) => {
    const variants: any = {
      preparado: 'primary',
      enviado: 'info',
      entregado: 'success',
      cancelado: 'danger',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status.toUpperCase()}</Badge>;
  };

  const filteredNotes = deliveryNotes.filter((note) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      note.pallet_code.toLowerCase().includes(search) ||
      note.delivery_note_number.toLowerCase().includes(search) ||
      note.customer_name.toLowerCase().includes(search) ||
      (note.order_number?.toLowerCase() || '').includes(search)
    );
  });

  return (
    <Container className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-upc-scan me-2"></i>
            Albaranes y Etiquetas EST912
          </h2>
          <p className="text-muted">Sistema de códigos de palet y generación de etiquetas</p>
        </Col>
        <Col xs="auto">
          <Button variant="success" onClick={() => setShowCreateModal(true)}>
            <i className="bi bi-plus-circle me-2"></i>
            Nuevo Albarán
          </Button>
        </Col>
      </Row>

      {/* Statistics */}
      {stats && (
        <Row className="g-3 mb-4">
          <Col xs={6} md={3}>
            <Card className="text-center border-primary">
              <Card.Body>
                <h3 className="text-primary">{stats.total}</h3>
                <small className="text-muted">Total</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={6} md={3}>
            <Card className="text-center border-info">
              <Card.Body>
                <h3 className="text-info">{stats.preparado}</h3>
                <small className="text-muted">Preparados</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={6} md={3}>
            <Card className="text-center border-warning">
              <Card.Body>
                <h3 className="text-warning">{stats.enviado}</h3>
                <small className="text-muted">Enviados</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={6} md={3}>
            <Card className="text-center border-success">
              <Card.Body>
                <h3 className="text-success">{stats.entregado}</h3>
                <small className="text-muted">Entregados</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Next Code */}
      {nextCode && (
        <Alert variant="info" className="mb-4">
          <strong>Próximo código:</strong> <code className="ms-2">{nextCode}</code>
        </Alert>
      )}

      {/* Filters */}
      <Card className="mb-4">
        <Card.Body>
          <Row className="g-3">
            <Col md={6}>
              <InputGroup>
                <InputGroup.Text><i className="bi bi-search"></i></InputGroup.Text>
                <Form.Control
                  placeholder="Buscar..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
            </Col>
            <Col md={4}>
              <Form.Select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                <option value="">Todos</option>
                <option value="preparado">Preparado</option>
                <option value="enviado">Enviado</option>
                <option value="entregado">Entregado</option>
                <option value="cancelado">Cancelado</option>
              </Form.Select>
            </Col>
            <Col md={2}>
              <Button variant="outline-secondary" onClick={loadDeliveryNotes} className="w-100">
                <i className="bi bi-arrow-clockwise"></i>
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Table */}
      <Card>
        <Card.Body className="p-0">
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
            </div>
          ) : filteredNotes.length === 0 ? (
            <div className="text-center py-5 text-muted">
              <i className="bi bi-inbox display-1 d-block mb-3"></i>
              <p>No hay albaranes</p>
            </div>
          ) : (
            <Table responsive hover className="mb-0">
              <thead className="bg-light">
                <tr>
                  <th>Código EST912</th>
                  <th>Albarán</th>
                  <th>Cliente</th>
                  <th>Cajas</th>
                  <th>Estado</th>
                  <th className="text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredNotes.map((note) => (
                  <tr key={note.id}>
                    <td><code className="fw-bold">{note.pallet_code}</code></td>
                    <td>{note.delivery_note_number}</td>
                    <td>{note.customer_name}</td>
                    <td>{note.total_boxes}</td>
                    <td>{getStatusBadge(note.status)}</td>
                    <td>
                      <ButtonGroup size="sm">
                        <Button
                          variant="outline-primary"
                          onClick={() => {
                            setSelectedNote(note);
                            setShowLabelModal(true);
                          }}
                          title="PDF"
                        >
                          <i className="bi bi-file-pdf"></i>
                        </Button>
                        <Button
                          variant="outline-success"
                          onClick={() => {
                            setSelectedNote(note);
                            setShowZplModal(true);
                            setZplCode('');
                          }}
                          title="ZPL"
                        >
                          <i className="bi bi-printer"></i>
                        </Button>
                        <Button
                          variant="outline-info"
                          onClick={() => handlePreviewLabel(note)}
                          title="Vista Previa"
                        >
                          <i className="bi bi-eye"></i>
                        </Button>
                        {note.status !== 'entregado' && note.status !== 'cancelado' && note.id && (
                          <Button
                            variant="outline-secondary"
                            onClick={() => {
                              const nextStatus = note.status === 'preparado' ? 'enviado' : 'entregado';
                              handleUpdateStatus(note.id!, nextStatus);
                            }}
                            title="Cambiar Estado"
                          >
                            <i className="bi bi-arrow-right-circle"></i>
                          </Button>
                        )}
                      </ButtonGroup>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* CREATE MODAL */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Nuevo Albarán</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreateDeliveryNote}>
          <Modal.Body>
            <Row className="g-3">
              <Col md={6}>
                <Form.Group>
                  <Form.Label>Número de Albarán *</Form.Label>
                  <Form.Control
                    required
                    value={formData.delivery_note_number}
                    onChange={(e) => setFormData({ ...formData, delivery_note_number: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group>
                  <Form.Label>Número de Pedido</Form.Label>
                  <Form.Control
                    value={formData.order_number}
                    onChange={(e) => setFormData({ ...formData, order_number: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={12}>
                <Form.Group>
                  <Form.Label>Cliente *</Form.Label>
                  <Form.Control
                    required
                    value={formData.customer_name}
                    onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Total Cajas *</Form.Label>
                  <Form.Control
                    type="number"
                    required
                    min={1}
                    value={formData.total_boxes}
                    onChange={(e) => setFormData({ ...formData, total_boxes: parseInt(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={8}>
                <Form.Group>
                  <Form.Label>Producto</Form.Label>
                  <Form.Control
                    value={formData.product_description}
                    onChange={(e) => setFormData({ ...formData, product_description: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Total Palets</Form.Label>
                  <Form.Control
                    type="number"
                    min={1}
                    value={formData.total_pallets_in_order}
                    onChange={(e) => setFormData({ ...formData, total_pallets_in_order: parseInt(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Nº Palet</Form.Label>
                  <Form.Control
                    type="number"
                    min={1}
                    value={formData.pallet_number_in_order}
                    onChange={(e) => setFormData({ ...formData, pallet_number_in_order: parseInt(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Etiquetas</Form.Label>
                  <Form.Control
                    type="number"
                    min={1}
                    value={formData.labels_to_print}
                    onChange={(e) => setFormData({ ...formData, labels_to_print: parseInt(e.target.value) })}
                  />
                </Form.Group>
              </Col>
            </Row>
            {nextCode && (
              <Alert variant="success" className="mt-3 mb-0">
                Se generará el código: <code>{nextCode}</code>
              </Alert>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancelar</Button>
            <Button variant="success" type="submit" disabled={loading}>
              {loading ? 'Creando...' : 'Crear'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* PDF LABEL MODAL */}
      <Modal show={showLabelModal} onHide={() => setShowLabelModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Generar Etiqueta PDF</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedNote && (
            <>
              <Alert variant="info">
                <strong>Código:</strong> <code>{selectedNote.pallet_code}</code>
              </Alert>
              <Form.Group className="mb-3">
                <Form.Label>Cantidad de Etiquetas</Form.Label>
                <Form.Control
                  type="number"
                  min={1}
                  max={100}
                  value={labelConfig.labelsCount}
                  onChange={(e) => setLabelConfig({ ...labelConfig, labelsCount: parseInt(e.target.value) })}
                />
              </Form.Group>
              <Form.Group>
                <Form.Label>Tamaño</Form.Label>
                <Form.Select
                  value={labelConfig.labelSize}
                  onChange={(e) => setLabelConfig({ ...labelConfig, labelSize: e.target.value as any })}
                >
                  <option value="A6">A6 (105x148mm) - Folios A4</option>
                  <option value="100x150">100x150mm - Zebra Estándar</option>
                  <option value="100x100">100x100mm - Zebra Cuadrada</option>
                </Form.Select>
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowLabelModal(false)}>Cancelar</Button>
          <Button variant="primary" onClick={handleGeneratePdfLabel} disabled={loading}>
            {loading ? 'Generando...' : 'Descargar PDF'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* ZPL LABEL MODAL */}
      <Modal show={showZplModal} onHide={() => setShowZplModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Generar Código ZPL (Zebra)</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedNote && (
            <>
              <Alert variant="info">
                <strong>Código:</strong> <code>{selectedNote.pallet_code}</code>
              </Alert>
              <Row className="g-3 mb-3">
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>DPI</Form.Label>
                    <Form.Select value={zplConfig.dpi} onChange={(e) => setZplConfig({ ...zplConfig, dpi: parseInt(e.target.value) })}>
                      <option value="203">203 DPI</option>
                      <option value="300">300 DPI</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Ancho (mm)</Form.Label>
                    <Form.Control type="number" value={zplConfig.labelWidth} onChange={(e) => setZplConfig({ ...zplConfig, labelWidth: parseInt(e.target.value) })} />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Alto (mm)</Form.Label>
                    <Form.Control type="number" value={zplConfig.labelHeight} onChange={(e) => setZplConfig({ ...zplConfig, labelHeight: parseInt(e.target.value) })} />
                  </Form.Group>
                </Col>
              </Row>
              {!zplCode && (
                <Button variant="success" onClick={handleGenerateZplLabel} disabled={loading}>
                  {loading ? 'Generando...' : 'Generar Código ZPL'}
                </Button>
              )}
              {zplCode && (
                <>
                  <Alert variant="success">Código ZPL Generado</Alert>
                  <Form.Group className="mb-3">
                    <Form.Control as="textarea" rows={10} value={zplCode} readOnly />
                  </Form.Group>
                  <Button variant="outline-primary" onClick={copyZplToClipboard}>
                    <i className="bi bi-clipboard me-2"></i>
                    Copiar al Portapapeles
                  </Button>
                </>
              )}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowZplModal(false)}>Cerrar</Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default DeliveryLabels;
