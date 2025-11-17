/**
 * OSE Platform - Notification Types
 * Types for device series notifications system
 */

// Notification Types
export type NotificationType =
  | 'new_device_registered'      // Nuevo dispositivo registrado
  | 'device_shipped'             // Dispositivo enviado
  | 'device_delivered'           // Dispositivo entregado
  | 'device_activated'           // Dispositivo activado
  | 'device_failure'             // Fallo de dispositivo
  | 'device_maintenance'         // Mantenimiento requerido
  | 'batch_registered'           // Lote completo registrado
  | 'custom'                     // Notificación personalizada

// Priority Levels
export type NotificationPriority = 'low' | 'medium' | 'high' | 'critical'

// Notification Status
export type NotificationStatus = 'pending' | 'read' | 'resolved' | 'archived'

// Main Notification Interface
export interface Notification {
  id: string
  type: NotificationType
  priority: NotificationPriority
  status: NotificationStatus
  title: string
  message: string
  device_id?: string
  device_imei?: string
  device_serial?: string
  batch_code?: string
  affected_count?: number
  created_at: string
  read_at?: string
  resolved_at?: string
  resolved_by?: string
  resolution_notes?: string
  metadata?: Record<string, any>
}

// Create Notification DTO
export interface NotificationCreate {
  type: NotificationType
  priority: NotificationPriority
  title: string
  message: string
  device_id?: string
  device_imei?: string
  device_serial?: string
  batch_code?: string
  affected_count?: number
  metadata?: Record<string, any>
}

// Notification Filters
export interface NotificationFilters {
  type?: NotificationType
  priority?: NotificationPriority
  status?: NotificationStatus
  device_imei?: string
  batch_code?: string
  date_from?: string
  date_to?: string
  search?: string
}

// Notification Statistics
export interface NotificationStats {
  total: number
  pending: number
  read: number
  resolved: number
  by_priority: {
    low: number
    medium: number
    high: number
    critical: number
  }
  by_type: {
    [key in NotificationType]?: number
  }
  recent_trend: {
    date: string
    count: number
  }[]
}

// Resolve Notification DTO
export interface NotificationResolve {
  resolution_notes?: string
}

// Batch Resolve DTO
export interface NotificationBatchResolve {
  ids: string[]
  resolution_notes?: string
}
