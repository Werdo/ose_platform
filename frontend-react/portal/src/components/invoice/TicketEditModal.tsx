/**
 * Ticket Edit Modal Component
 * Modal para editar datos de un ticket manualmente
 */

import { useState, useEffect } from 'react'
import { Modal, Button, Form, Row, Col, Alert } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import toast from 'react-hot-toast'
import type { Ticket, TicketOCRData, TicketItem } from '../../types/invoice'

interface TicketEditModalProps {
  show: boolean
  ticket: Ticket
  onHide: () => void
  onComplete: () => void
}

export default function TicketEditModal({ show, ticket, onHide, onComplete }: TicketEditModalProps) {
  const [ocrData, setOcrData] = useState<TicketOCRData>({
    ticket_number: '',
    date: '',
    items: [],
    subtotal: 0,
    tax: 0,
    total: 0,
    merchant: '',
    confidence: 0
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (ticket.ocr_data) {
      setOcrData(ticket.ocr_data)
    }
  }, [ticket])

  const handleAddItem = () => {
    const newItem: TicketItem = {
      description: '',
      quantity: 1,
      unit_price: 0,
      total: 0
    }
    setOcrData({
      ...ocrData,
      items: [...(ocrData.items || []), newItem]
    })
  }

  const handleRemoveItem = (index: number) => {
    const newItems = [...(ocrData.items || [])]
    newItems.splice(index, 1)
    setOcrData({ ...ocrData, items: newItems })
    recalculateTotals(newItems)
  }

  const handleItemChange = (index: number, field: keyof TicketItem, value: any) => {
    const newItems = [...(ocrData.items || [])]
    newItems[index] = { ...newItems[index], [field]: value }

    // Recalcular total del item
    if (field === 'quantity' || field === 'unit_price') {
      newItems[index].total = newItems[index].quantity * newItems[index].unit_price
    }

    setOcrData({ ...ocrData, items: newItems })
    recalculateTotals(newItems)
  }

  const recalculateTotals = (items: TicketItem[]) => {
    const subtotal = items.reduce((sum, item) => sum + item.total, 0)
    const tax = subtotal * 0.21 // Asumiendo 21% IVA
    const total = subtotal + tax

    setOcrData(prev => ({
      ...prev,
      subtotal,
      tax,
      total
    }))
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await apiService.patch(`/api/app5/tickets/${ticket.id}`, {
        ocr_data: ocrData
      })
      toast.success('Ticket actualizado correctamente')
      onComplete()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error actualizando ticket')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton className="bg-primary text-white">
        <Modal.Title>
          <i className="bi bi-pencil me-2"></i>
          Editar Ticket: {ticket.ticket_number}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Row className="mb-3">
            <Col md={6}>
              <Form.Group>
                <Form.Label>Número de Ticket</Form.Label>
                <Form.Control
                  type="text"
                  value={ocrData.ticket_number || ''}
                  onChange={(e) => setOcrData({ ...ocrData, ticket_number: e.target.value })}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group>
                <Form.Label>Fecha</Form.Label>
                <Form.Control
                  type="date"
                  value={ocrData.date || ''}
                  onChange={(e) => setOcrData({ ...ocrData, date: e.target.value })}
                />
              </Form.Group>
            </Col>
          </Row>

          <Row className="mb-3">
            <Col>
              <Form.Group>
                <Form.Label>Comercio</Form.Label>
                <Form.Control
                  type="text"
                  value={ocrData.merchant || ''}
                  onChange={(e) => setOcrData({ ...ocrData, merchant: e.target.value })}
                />
              </Form.Group>
            </Col>
          </Row>

          <div className="mb-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <Form.Label className="mb-0">Items</Form.Label>
              <Button variant="success" size="sm" onClick={handleAddItem}>
                <i className="bi bi-plus-circle me-1"></i>
                Agregar Item
              </Button>
            </div>

            {(!ocrData.items || ocrData.items.length === 0) ? (
              <Alert variant="info">
                No hay items. Haz clic en "Agregar Item" para añadir.
              </Alert>
            ) : (
              ocrData.items.map((item, index) => (
                <div key={index} className="border rounded p-3 mb-2 bg-light">
                  <Row className="mb-2">
                    <Col md={12}>
                      <Form.Group>
                        <Form.Label>Descripción</Form.Label>
                        <Form.Control
                          type="text"
                          value={item.description}
                          onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  <Row>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Cantidad</Form.Label>
                        <Form.Control
                          type="number"
                          min="1"
                          step="1"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                        />
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Precio Unit.</Form.Label>
                        <Form.Control
                          type="number"
                          min="0"
                          step="0.01"
                          value={item.unit_price}
                          onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                        />
                      </Form.Group>
                    </Col>
                    <Col md={3}>
                      <Form.Group>
                        <Form.Label>Total</Form.Label>
                        <Form.Control
                          type="text"
                          value={item.total.toFixed(2)}
                          readOnly
                          className="bg-white"
                        />
                      </Form.Group>
                    </Col>
                    <Col md={1} className="d-flex align-items-end">
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleRemoveItem(index)}
                      >
                        <i className="bi bi-trash"></i>
                      </Button>
                    </Col>
                  </Row>
                </div>
              ))
            )}
          </div>

          <Row className="mb-3">
            <Col md={4}>
              <Form.Group>
                <Form.Label>Subtotal</Form.Label>
                <Form.Control
                  type="text"
                  value={ocrData.subtotal?.toFixed(2) || '0.00'}
                  readOnly
                  className="bg-light"
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>IVA</Form.Label>
                <Form.Control
                  type="text"
                  value={ocrData.tax?.toFixed(2) || '0.00'}
                  readOnly
                  className="bg-light"
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label><strong>Total</strong></Form.Label>
                <Form.Control
                  type="text"
                  value={ocrData.total?.toFixed(2) || '0.00'}
                  readOnly
                  className="bg-light fw-bold"
                />
              </Form.Group>
            </Col>
          </Row>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancelar
        </Button>
        <Button variant="primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Guardando...' : 'Guardar Cambios'}
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
