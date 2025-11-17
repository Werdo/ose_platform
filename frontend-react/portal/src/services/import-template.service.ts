/**
 * Servicio para gestionar plantillas de importación
 */

import { apiService } from './api.service'
import type {
  ImportTemplate,
  ImportTemplateListItem,
  CreateTemplateRequest,
  UpdateTemplateRequest,
  TemplatesResponse,
  TemplateDetailResponse,
  CreateTemplateResponse,
  UpdateTemplateResponse,
  DeleteTemplateResponse
} from '../types/import-template'

const importTemplateService = {
  /**
   * Obtener todas las plantillas activas
   */
  getTemplates: async (): Promise<ImportTemplateListItem[]> => {
    try {
      const response = await apiService.get<TemplatesResponse>('/api/app2/templates')
      return response.templates || []
    } catch (error) {
      console.error('Error obteniendo plantillas:', error)
      throw error
    }
  },

  /**
   * Obtener detalles de una plantilla
   */
  getTemplateById: async (id: string): Promise<ImportTemplate> => {
    try {
      const response = await apiService.get<TemplateDetailResponse>(`/api/app2/templates/${id}`)
      return response.template
    } catch (error) {
      console.error(`Error obteniendo plantilla ${id}:`, error)
      throw error
    }
  },

  /**
   * Crear una nueva plantilla
   */
  createTemplate: async (data: CreateTemplateRequest): Promise<CreateTemplateResponse> => {
    try {
      const response = await apiService.post<CreateTemplateResponse>('/api/app2/templates', data)
      return response
    } catch (error) {
      console.error('Error creando plantilla:', error)
      throw error
    }
  },

  /**
   * Actualizar una plantilla existente
   */
  updateTemplate: async (id: string, data: UpdateTemplateRequest): Promise<UpdateTemplateResponse> => {
    try {
      const response = await apiService.put<UpdateTemplateResponse>(`/api/app2/templates/${id}`, data)
      return response
    } catch (error) {
      console.error(`Error actualizando plantilla ${id}:`, error)
      throw error
    }
  },

  /**
   * Desactivar una plantilla (soft delete)
   */
  deleteTemplate: async (id: string): Promise<DeleteTemplateResponse> => {
    try {
      const response = await apiService.delete<DeleteTemplateResponse>(`/api/app2/templates/${id}`)
      return response
    } catch (error) {
      console.error(`Error eliminando plantilla ${id}:`, error)
      throw error
    }
  },

  /**
   * Importar archivo usando una plantilla
   */
  uploadWithTemplate: async (file: File, templateId?: string, templateName?: string): Promise<any> => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const params: Record<string, string> = {}
      if (templateId) {
        params.template_id = templateId
      } else if (templateName) {
        params.template_name = templateName
      }

      const queryString = new URLSearchParams(params).toString()
      const url = `/api/app2/upload-with-template${queryString ? `?${queryString}` : ''}`

      const response = await apiService.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      return response
    } catch (error) {
      console.error('Error subiendo archivo con plantilla:', error)
      throw error
    }
  },

  /**
   * Crear la plantilla NEOWAY_PRODUCCION_IMPORT
   */
  createNeowayTemplate: async (): Promise<CreateTemplateResponse> => {
    try {
      const response = await apiService.post<CreateTemplateResponse>('/api/app2/templates/create-neoway')
      return response
    } catch (error) {
      console.error('Error creando plantilla NEOWAY:', error)
      throw error
    }
  }
}

export default importTemplateService
