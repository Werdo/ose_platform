/**
 * Brand Service
 * Gestión de marcas de dispositivos
 */

import api from './api.service'

export interface Brand {
  id: string
  name: string
  code?: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BrandResponse {
  success: boolean
  count?: number
  brands?: Brand[]
  brand?: Brand
  message?: string
  created?: number
  existing?: number
}

const brandService = {
  /**
   * Obtiene todas las marcas
   */
  getBrands: async (activeOnly: boolean = true): Promise<BrandResponse> => {
    const response = await api.get(`/brands?active_only=${activeOnly}`)
    return response.data
  },

  /**
   * Obtiene una marca por ID
   */
  getBrand: async (brandId: string): Promise<BrandResponse> => {
    const response = await api.get(`/brands/${brandId}`)
    return response.data
  },

  /**
   * Crea una nueva marca
   */
  createBrand: async (
    name: string,
    code?: string,
    description?: string
  ): Promise<BrandResponse> => {
    const params = new URLSearchParams()
    params.append('name', name)
    if (code) params.append('code', code)
    if (description) params.append('description', description)

    const response = await api.post(`/brands?${params.toString()}`)
    return response.data
  },

  /**
   * Actualiza una marca existente
   */
  updateBrand: async (
    brandId: string,
    name?: string,
    code?: string,
    description?: string,
    is_active?: boolean
  ): Promise<BrandResponse> => {
    const params = new URLSearchParams()
    if (name) params.append('name', name)
    if (code !== undefined) params.append('code', code)
    if (description !== undefined) params.append('description', description)
    if (is_active !== undefined) params.append('is_active', is_active.toString())

    const response = await api.put(`/brands/${brandId}?${params.toString()}`)
    return response.data
  },

  /**
   * Desactiva una marca (soft delete)
   */
  deleteBrand: async (brandId: string): Promise<BrandResponse> => {
    const response = await api.delete(`/brands/${brandId}`)
    return response.data
  },

  /**
   * Inicializa las marcas por defecto
   */
  initializeDefaults: async (): Promise<BrandResponse> => {
    const response = await api.post('/brands/initialize-defaults')
    return response.data
  }
}

export default brandService
