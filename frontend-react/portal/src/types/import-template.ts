/**
 * Tipos para plantillas de importación
 */

export interface ImportTemplate {
  id: string
  name: string
  description?: string
  destination: 'devices' | 'inventory' | 'service_tickets' | 'depositos' | 'customers'
  file_types: string[]
  mapping: Record<string, string>
  validation?: Record<string, any>
  transformations?: Record<string, any>
  default_values?: Record<string, any>
  required_fields: string[]
  skip_rows: number
  encoding: string
  delimiter: string
  sheet_name?: string
  is_active: boolean
  usage_count: number
  last_used_at?: string
  created_at: string
  updated_at: string
}

export interface ImportTemplateListItem {
  id: string
  name: string
  description?: string
  destination: string
  usage_count: number
  last_used_at?: string
  created_at: string
}

export interface CreateTemplateRequest {
  name: string
  description?: string
  destination?: 'devices' | 'inventory' | 'service_tickets' | 'depositos' | 'customers'
  file_types?: string[]
  mapping: Record<string, string>
  validation?: Record<string, any>
  transformations?: Record<string, any>
  default_values?: Record<string, any>
  required_fields?: string[]
  skip_rows?: number
  encoding?: string
  delimiter?: string
  sheet_name?: string
}

export interface UpdateTemplateRequest {
  name?: string
  description?: string
  mapping?: Record<string, string>
  validation?: Record<string, any>
  transformations?: Record<string, any>
  default_values?: Record<string, any>
  required_fields?: string[]
  skip_rows?: number
  encoding?: string
  delimiter?: string
  sheet_name?: string
  is_active?: boolean
}

export interface ImportWithTemplateRequest {
  file: File
  template_id?: string
  template_name?: string
}

export interface TemplatesResponse {
  success: boolean
  count: number
  templates: ImportTemplateListItem[]
}

export interface TemplateDetailResponse {
  success: boolean
  template: ImportTemplate
}

export interface CreateTemplateResponse {
  success: boolean
  message: string
  template_id: string
  template: {
    id: string
    name: string
    description?: string
  }
}

export interface UpdateTemplateResponse {
  success: boolean
  message: string
  template_id: string
}

export interface DeleteTemplateResponse {
  success: boolean
  message: string
}
