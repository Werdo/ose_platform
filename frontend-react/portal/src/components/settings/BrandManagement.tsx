/**
 * Brand Management Component
 * Gestión CRUD de marcas de dispositivos
 */

import { useState, useEffect } from 'react'
import { Card, Button, Table, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap'
import brandService, { Brand } from '../../services/brand.service'

export default function BrandManagement() {
  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingBrand, setEditingBrand] = useState<Brand | null>(null)

  // Form states
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: ''
  })

  // Load brands on component mount
  useEffect(() => {
    loadBrands()
  }, [])

  const loadBrands = async (activeOnly: boolean = false) => {
    setLoading(true)
    setError(null)
    try {
      const response = await brandService.getBrands(activeOnly)
      if (response.success && response.brands) {
        setBrands(response.brands)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar las marcas')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateBrand = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await brandService.createBrand(
        formData.name,
        formData.code || undefined,
        formData.description || undefined
      )
      if (response.success) {
        setSuccess('Marca creada exitosamente')
        setShowCreateModal(false)
        resetForm()
        loadBrands()
        setTimeout(() => setSuccess(null), 3000)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear la marca')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateBrand = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingBrand) return

    setLoading(true)
    setError(null)
    try {
      const response = await brandService.updateBrand(
        editingBrand.id,
        formData.name,
        formData.code,
        formData.description,
        undefined
      )
      if (response.success) {
        setSuccess('Marca actualizada exitosamente')
        setShowEditModal(false)
        setEditingBrand(null)
        resetForm()
        loadBrands()
        setTimeout(() => setSuccess(null), 3000)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar la marca')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteBrand = async (brandId: string) => {
    if (!confirm('¿Está seguro de desactivar esta marca?')) return

    setLoading(true)
    setError(null)
    try {
      const response = await brandService.deleteBrand(brandId)
      if (response.success) {
        setSuccess('Marca desactivada exitosamente')
        loadBrands()
        setTimeout(() => setSuccess(null), 3000)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al desactivar la marca')
    } finally {
      setLoading(false)
    }
  }

  const handleInitializeDefaults = async () => {
    if (!confirm('¿Inicializar marcas por defecto?')) return

    setLoading(true)
    setError(null)
    try {
      const response = await brandService.initializeDefaults()
      if (response.success) {
        setSuccess(`${response.created} marcas creadas, ${response.existing} ya existían`)
        loadBrands()
        setTimeout(() => setSuccess(null), 3000)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al inicializar marcas')
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (brand: Brand) => {
    setEditingBrand(brand)
    setFormData({
      name: brand.name,
      code: brand.code || '',
      description: brand.description || ''
    })
    setShowEditModal(true)
  }

  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      description: ''
    })
  }

  const handleCloseCreateModal = () => {
    setShowCreateModal(false)
    resetForm()
    setError(null)
  }

  const handleCloseEditModal = () => {
    setShowEditModal(false)
    setEditingBrand(null)
    resetForm()
    setError(null)
  }

  return (
    <Card className="border-0 shadow-sm">
      <Card.Header className="gradient-primary text-white fw-bold d-flex justify-content-between align-items-center">
        <div>
          <i className="bi bi-tags me-2"></i>
          Gestión de Marcas
        </div>
        <div>
          <Button
            variant="light"
            size="sm"
            onClick={() => setShowCreateModal(true)}
            className="me-2"
          >
            <i className="bi bi-plus-lg me-1"></i>
            Nueva Marca
          </Button>
          <Button
            variant="outline-light"
            size="sm"
            onClick={handleInitializeDefaults}
          >
            <i className="bi bi-arrow-repeat me-1"></i>
            Inicializar
          </Button>
        </div>
      </Card.Header>
      <Card.Body>
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {loading && brands.length === 0 ? (
          <div className="text-center py-4">
            <Spinner animation="border" />
            <p className="mt-2 text-muted">Cargando marcas...</p>
          </div>
        ) : brands.length === 0 ? (
          <div className="text-center py-4 text-muted">
            <i className="bi bi-inbox display-4"></i>
            <p className="mt-2">No hay marcas registradas</p>
            <Button variant="primary" onClick={handleInitializeDefaults}>
              Inicializar Marcas por Defecto
            </Button>
          </div>
        ) : (
          <Table responsive hover>
            <thead className="table-light">
              <tr>
                <th>Nombre</th>
                <th>Código</th>
                <th>Descripción</th>
                <th>Estado</th>
                <th className="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {brands.map((brand) => (
                <tr key={brand.id}>
                  <td className="fw-semibold">{brand.name}</td>
                  <td>
                    {brand.code ? (
                      <code className="text-primary">{brand.code}</code>
                    ) : (
                      <span className="text-muted">-</span>
                    )}
                  </td>
                  <td className="text-muted small">{brand.description || '-'}</td>
                  <td>
                    {brand.is_active ? (
                      <Badge bg="success">Activa</Badge>
                    ) : (
                      <Badge bg="secondary">Inactiva</Badge>
                    )}
                  </td>
                  <td className="text-end">
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => openEditModal(brand)}
                      className="me-2"
                    >
                      <i className="bi bi-pencil"></i>
                    </Button>
                    {brand.is_active && (
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDeleteBrand(brand.id)}
                      >
                        <i className="bi bi-trash"></i>
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}

        <div className="mt-3 text-end">
          <Form.Check
            type="switch"
            id="show-inactive"
            label="Mostrar marcas inactivas"
            onChange={(e) => loadBrands(!e.target.checked)}
          />
        </div>
      </Card.Body>

      {/* Modal Crear Marca */}
      <Modal show={showCreateModal} onHide={handleCloseCreateModal}>
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-plus-circle me-2"></i>
            Nueva Marca
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleCreateBrand}>
            <Form.Group className="mb-3">
              <Form.Label>
                Nombre <span className="text-danger">*</span>
              </Form.Label>
              <Form.Control
                type="text"
                placeholder="Ej: QUECTEL"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Código</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ej: QUEC"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              />
              <Form.Text className="text-muted">
                Código corto o abreviatura
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Descripción</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="Descripción de la marca"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseCreateModal}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleCreateBrand} disabled={loading}>
            {loading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Creando...
              </>
            ) : (
              <>
                <i className="bi bi-check-lg me-1"></i>
                Crear Marca
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Modal Editar Marca */}
      <Modal show={showEditModal} onHide={handleCloseEditModal}>
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-pencil me-2"></i>
            Editar Marca
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleUpdateBrand}>
            <Form.Group className="mb-3">
              <Form.Label>
                Nombre <span className="text-danger">*</span>
              </Form.Label>
              <Form.Control
                type="text"
                placeholder="Ej: QUECTEL"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Código</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ej: QUEC"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Descripción</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="Descripción de la marca"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseEditModal}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleUpdateBrand} disabled={loading}>
            {loading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Guardando...
              </>
            ) : (
              <>
                <i className="bi bi-check-lg me-1"></i>
                Guardar Cambios
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </Card>
  )
}
