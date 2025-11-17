/**
 * Configuration Form Component
 * Formulario de configuración de facturación
 */

import { useState, useEffect } from 'react'
import { Card, Form, Button, Row, Col, Spinner, Alert, Tabs, Tab } from 'react-bootstrap'
import { apiService } from '../../services/api.service'
import toast from 'react-hot-toast'
import type { AppConfig } from '../../types/invoice'
import LogoUploader from './LogoUploader'

export default function ConfigurationForm() {
  const [config, setConfig] = useState<AppConfig>({
    company: {
      name: '',
      nif: '',
      address: '',
      city: '',
      postal_code: '',
      phone: '',
      email: '',
      logo_url: ''
    },
    invoice: {
      series: 'F',
      next_number: 1,
      reset_yearly: true,
      tax_rate: 0.21,
      template: 'default',
      primary_color: '#007bff',
      secondary_color: '#6c757d',
      footer_text: ''
    },
    ocr: {
      enabled: true,
      confidence_threshold: 0.7,
      allow_manual_entry: true
    }
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const response = await apiService.get('/api/app5/config')
      if (response.config) {
        // Merge con defaults para asegurar que todas las propiedades existen
        setConfig({
          company: {
            name: response.config.company?.name || '',
            nif: response.config.company?.nif || '',
            address: response.config.company?.address || '',
            city: response.config.company?.city || '',
            postal_code: response.config.company?.postal_code || '',
            phone: response.config.company?.phone || '',
            email: response.config.company?.email || '',
            logo_url: response.config.company?.logo_url || ''
          },
          invoice: {
            series: response.config.invoice?.series || 'F',
            next_number: response.config.invoice?.next_number || 1,
            reset_yearly: response.config.invoice?.reset_yearly !== undefined ? response.config.invoice.reset_yearly : true,
            tax_rate: response.config.invoice?.tax_rate || 0.21,
            template: response.config.invoice?.template || 'default',
            primary_color: response.config.invoice?.primary_color || '#007bff',
            secondary_color: response.config.invoice?.secondary_color || '#6c757d',
            footer_text: response.config.invoice?.footer_text || ''
          },
          ocr: {
            enabled: response.config.ocr?.enabled !== undefined ? response.config.ocr.enabled : true,
            confidence_threshold: response.config.ocr?.confidence_threshold || 0.7,
            allow_manual_entry: response.config.ocr?.allow_manual_entry !== undefined ? response.config.ocr.allow_manual_entry : true
          }
        })
      }
    } catch (error: any) {
      console.error('Error cargando configuración:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await apiService.put('/api/app5/config', config)
      toast.success('Configuración guardada correctamente')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error guardando configuración')
    } finally {
      setSaving(false)
    }
  }

  const handleLogoUploaded = (url: string) => {
    setConfig({
      ...config,
      company: {
        ...config.company,
        logo_url: url
      }
    })
  }

  if (loading) {
    return (
      <div className="text-center py-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2 text-muted">Cargando configuración...</p>
      </div>
    )
  }

  return (
    <Card className="border-0 shadow-sm">
      <Card.Header className="bg-white border-bottom">
        <h5 className="mb-0">
          <i className="bi bi-gear me-2"></i>
          Configuración de Facturación
        </h5>
      </Card.Header>
      <Card.Body>
        <Tabs defaultActiveKey="company" className="mb-4">
          {/* Company Tab */}
          <Tab
            eventKey="company"
            title={
              <>
                <i className="bi bi-building me-2"></i>
                Datos de Empresa
              </>
            }
          >
            <Form>
              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Nombre de la Empresa *</Form.Label>
                    <Form.Control
                      type="text"
                      value={config.company.name}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, name: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>NIF/CIF *</Form.Label>
                    <Form.Control
                      type="text"
                      value={config.company.nif}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, nif: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={12}>
                  <Form.Group>
                    <Form.Label>Dirección *</Form.Label>
                    <Form.Control
                      type="text"
                      value={config.company.address}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, address: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Ciudad</Form.Label>
                    <Form.Control
                      type="text"
                      value={config.company.city || ''}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, city: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Código Postal</Form.Label>
                    <Form.Control
                      type="text"
                      value={config.company.postal_code || ''}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, postal_code: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Teléfono</Form.Label>
                    <Form.Control
                      type="text"
                      value={config.company.phone || ''}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, phone: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      value={config.company.email || ''}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          company: { ...config.company, email: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={12}>
                  <Form.Label>Logo de la Empresa</Form.Label>
                  <LogoUploader
                    currentLogoUrl={config.company.logo_url}
                    onLogoUploaded={handleLogoUploaded}
                  />
                </Col>
              </Row>
            </Form>
          </Tab>

          {/* Invoice Tab */}
          <Tab
            eventKey="invoice"
            title={
              <>
                <i className="bi bi-receipt me-2"></i>
                Facturación
              </>
            }
          >
            <Form>
              <Alert variant="info">
                <i className="bi bi-info-circle me-2"></i>
                Configura la numeración y formato de tus facturas
              </Alert>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Serie de Factura</Form.Label>
                    <Form.Control
                      type="text"
                      maxLength={3}
                      value={config.invoice.series}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, series: e.target.value.toUpperCase() }
                        })
                      }
                    />
                    <Form.Text className="text-muted">
                      Ejemplo: F, FAC, INV
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Próximo Número</Form.Label>
                    <Form.Control
                      type="number"
                      value={config.invoice.next_number}
                      readOnly
                      className="bg-light"
                    />
                    <Form.Text className="text-muted">
                      Se auto-incrementa automáticamente
                    </Form.Text>
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Tasa de IVA</Form.Label>
                    <Form.Control
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={config.invoice.tax_rate}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, tax_rate: parseFloat(e.target.value) || 0 }
                        })
                      }
                    />
                    <Form.Text className="text-muted">
                      Valor decimal (0.21 = 21%)
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Check
                      type="checkbox"
                      label="Reiniciar numeración cada año"
                      checked={config.invoice.reset_yearly}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, reset_yearly: e.target.checked }
                        })
                      }
                      className="mt-4"
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Plantilla</Form.Label>
                    <Form.Select
                      value={config.invoice.template}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, template: e.target.value }
                        })
                      }
                    >
                      <option value="default">Por Defecto</option>
                      <option value="modern">Moderna</option>
                      <option value="classic">Clásica</option>
                      <option value="minimal">Minimalista</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Color Primario</Form.Label>
                    <Form.Control
                      type="color"
                      value={config.invoice.primary_color || '#007bff'}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, primary_color: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Color Secundario</Form.Label>
                    <Form.Control
                      type="color"
                      value={config.invoice.secondary_color || '#6c757d'}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, secondary_color: e.target.value }
                        })
                      }
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={12}>
                  <Form.Group>
                    <Form.Label>Texto del Pie de Página</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      value={config.invoice.footer_text || ''}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          invoice: { ...config.invoice, footer_text: e.target.value }
                        })
                      }
                      placeholder="Texto que aparecerá en el pie de página de las facturas..."
                    />
                  </Form.Group>
                </Col>
              </Row>
            </Form>
          </Tab>

          {/* OCR Tab */}
          <Tab
            eventKey="ocr"
            title={
              <>
                <i className="bi bi-cpu me-2"></i>
                OCR
              </>
            }
          >
            <Form>
              <Alert variant="info">
                <i className="bi bi-info-circle me-2"></i>
                Configura el procesamiento automático de tickets mediante OCR
              </Alert>

              <Row className="mb-3">
                <Col md={12}>
                  <Form.Check
                    type="switch"
                    id="ocr-enabled"
                    label="Habilitar OCR automático"
                    checked={config.ocr.enabled}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        ocr: { ...config.ocr, enabled: e.target.checked }
                      })
                    }
                  />
                  <Form.Text className="text-muted">
                    Procesa automáticamente los tickets subidos para extraer datos
                  </Form.Text>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Umbral de Confianza</Form.Label>
                    <Form.Control
                      type="number"
                      min="0"
                      max="1"
                      step="0.05"
                      value={config.ocr.confidence_threshold}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          ocr: { ...config.ocr, confidence_threshold: parseFloat(e.target.value) || 0.7 }
                        })
                      }
                    />
                    <Form.Text className="text-muted">
                      Nivel mínimo de confianza (0.0 - 1.0)
                    </Form.Text>
                  </Form.Group>
                </Col>
              </Row>

              <Row className="mb-3">
                <Col md={12}>
                  <Form.Check
                    type="switch"
                    id="manual-entry"
                    label="Permitir entrada manual"
                    checked={config.ocr.allow_manual_entry}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        ocr: { ...config.ocr, allow_manual_entry: e.target.checked }
                      })
                    }
                  />
                  <Form.Text className="text-muted">
                    Permite editar manualmente los datos extraídos por OCR
                  </Form.Text>
                </Col>
              </Row>
            </Form>
          </Tab>
        </Tabs>

        {/* Save Button */}
        <div className="d-flex justify-content-end">
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            {saving ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Guardando...
              </>
            ) : (
              <>
                <i className="bi bi-check-circle me-2"></i>
                Guardar Configuración
              </>
            )}
          </Button>
        </div>
      </Card.Body>
    </Card>
  )
}
