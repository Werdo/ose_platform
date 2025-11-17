/**
 * OSE Platform - Notification Service
 * API service for device series notifications
 */

import apiService from './api.service'
import type {
  Notification,
  NotificationCreate,
  NotificationFilters,
  NotificationStats,
  NotificationResolve,
  NotificationBatchResolve,
} from '../types/notifications'
import type { PaginatedResponse } from '../types'

const notificationService = {
  /**
   * Get all notifications with filters and pagination
   */
  getAll: async (
    page: number = 1,
    limit: number = 20,
    filters?: NotificationFilters
  ): Promise<PaginatedResponse<Notification>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    })

    // TODO: Replace with actual backend endpoint when available
    // return await apiService.get<PaginatedResponse<Notification>>(
    //   `/api/v1/notifications?${params.toString()}`
    // )

    // MOCK DATA - Remove when backend is ready
    return mockGetNotifications(page, limit, filters)
  },

  /**
   * Get notification by ID
   */
  getById: async (id: string): Promise<Notification> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.get<Notification>(`/api/v1/notifications/${id}`)

    return mockGetNotificationById(id)
  },

  /**
   * Create new notification
   */
  create: async (data: NotificationCreate): Promise<Notification> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.post<Notification>('/api/v1/notifications', data)

    return mockCreateNotification(data)
  },

  /**
   * Mark notification as read
   */
  markAsRead: async (id: string): Promise<Notification> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.patch<Notification>(`/api/v1/notifications/${id}/read`)

    return mockMarkAsRead(id)
  },

  /**
   * Resolve notification
   */
  resolve: async (id: string, data: NotificationResolve): Promise<Notification> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.patch<Notification>(`/api/v1/notifications/${id}/resolve`, data)

    return mockResolveNotification(id, data)
  },

  /**
   * Resolve multiple notifications
   */
  resolveMultiple: async (data: NotificationBatchResolve): Promise<{ resolved: number }> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.post<{ resolved: number }>('/api/v1/notifications/resolve-batch', data)

    return mockBatchResolve(data)
  },

  /**
   * Delete notification
   */
  delete: async (id: string): Promise<void> => {
    // TODO: Replace with actual backend endpoint
    // await apiService.delete(`/api/v1/notifications/${id}`)

    mockDeleteNotification(id)
  },

  /**
   * Get pending notifications
   */
  getPending: async (): Promise<Notification[]> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.get<Notification[]>('/api/v1/notifications/pending')

    return mockGetPending()
  },

  /**
   * Get critical notifications
   */
  getCritical: async (): Promise<Notification[]> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.get<Notification[]>('/api/v1/notifications/critical')

    return mockGetCritical()
  },

  /**
   * Get notification statistics
   */
  getStatistics: async (): Promise<NotificationStats> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.get<NotificationStats>('/api/v1/notifications/statistics')

    return mockGetStatistics()
  },

  /**
   * Generate automatic notifications (for batch device registration)
   */
  generateAutomatic: async (): Promise<{ generated: number }> => {
    // TODO: Replace with actual backend endpoint
    // return await apiService.post<{ generated: number }>('/api/v1/notifications/generate-automatic')

    return mockGenerateAutomatic()
  },
}

// ============================================================================
// MOCK DATA FUNCTIONS - Remove when backend is ready
// ============================================================================

let mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'new_device_registered',
    priority: 'high',
    status: 'pending',
    title: 'Nuevo dispositivo registrado',
    message: 'Se ha registrado un nuevo dispositivo GPS tracker con IMEI 123456789012345',
    device_id: 'dev_001',
    device_imei: '123456789012345',
    device_serial: 'GPS-2024-001',
    created_at: new Date().toISOString(),
  },
  {
    id: '2',
    type: 'batch_registered',
    priority: 'critical',
    status: 'pending',
    title: 'Lote completo registrado',
    message: 'Se han registrado 50 dispositivos del lote BATCH-2024-001',
    batch_code: 'BATCH-2024-001',
    affected_count: 50,
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: '3',
    type: 'device_shipped',
    priority: 'medium',
    status: 'read',
    title: 'Dispositivo enviado',
    message: 'Dispositivo GPS-2024-002 enviado al cliente ACME Corp',
    device_serial: 'GPS-2024-002',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    read_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: '4',
    type: 'device_failure',
    priority: 'critical',
    status: 'resolved',
    title: 'Fallo de dispositivo reportado',
    message: 'Dispositivo GPS-2024-003 reportó fallo de batería',
    device_serial: 'GPS-2024-003',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    resolved_at: new Date(Date.now() - 43200000).toISOString(),
    resolved_by: 'admin',
    resolution_notes: 'Batería reemplazada y dispositivo operativo',
  },
]

function mockGetNotifications(
  page: number,
  limit: number,
  filters?: NotificationFilters
): PaginatedResponse<Notification> {
  let filtered = [...mockNotifications]

  if (filters?.type) {
    filtered = filtered.filter((n) => n.type === filters.type)
  }
  if (filters?.priority) {
    filtered = filtered.filter((n) => n.priority === filters.priority)
  }
  if (filters?.status) {
    filtered = filtered.filter((n) => n.status === filters.status)
  }
  if (filters?.search) {
    const search = filters.search.toLowerCase()
    filtered = filtered.filter(
      (n) =>
        n.title.toLowerCase().includes(search) ||
        n.message.toLowerCase().includes(search) ||
        n.device_serial?.toLowerCase().includes(search)
    )
  }

  const start = (page - 1) * limit
  const end = start + limit
  const items = filtered.slice(start, end)

  return {
    items,
    total: filtered.length,
    page,
    size: limit,
    pages: Math.ceil(filtered.length / limit),
  }
}

function mockGetNotificationById(id: string): Notification {
  const notification = mockNotifications.find((n) => n.id === id)
  if (!notification) {
    throw new Error('Notification not found')
  }
  return notification
}

function mockCreateNotification(data: NotificationCreate): Notification {
  const newNotification: Notification = {
    id: `${mockNotifications.length + 1}`,
    ...data,
    status: 'pending',
    created_at: new Date().toISOString(),
  }
  mockNotifications.unshift(newNotification)
  return newNotification
}

function mockMarkAsRead(id: string): Notification {
  const notification = mockNotifications.find((n) => n.id === id)
  if (!notification) {
    throw new Error('Notification not found')
  }
  notification.status = 'read'
  notification.read_at = new Date().toISOString()
  return notification
}

function mockResolveNotification(id: string, data: NotificationResolve): Notification {
  const notification = mockNotifications.find((n) => n.id === id)
  if (!notification) {
    throw new Error('Notification not found')
  }
  notification.status = 'resolved'
  notification.resolved_at = new Date().toISOString()
  notification.resolution_notes = data.resolution_notes
  return notification
}

function mockBatchResolve(data: NotificationBatchResolve): { resolved: number } {
  let count = 0
  data.ids.forEach((id) => {
    const notification = mockNotifications.find((n) => n.id === id)
    if (notification && notification.status !== 'resolved') {
      notification.status = 'resolved'
      notification.resolved_at = new Date().toISOString()
      notification.resolution_notes = data.resolution_notes
      count++
    }
  })
  return { resolved: count }
}

function mockDeleteNotification(id: string): void {
  const index = mockNotifications.findIndex((n) => n.id === id)
  if (index > -1) {
    mockNotifications.splice(index, 1)
  }
}

function mockGetPending(): Notification[] {
  return mockNotifications.filter((n) => n.status === 'pending')
}

function mockGetCritical(): Notification[] {
  return mockNotifications.filter((n) => n.priority === 'critical' && n.status !== 'resolved')
}

function mockGetStatistics(): NotificationStats {
  const stats: NotificationStats = {
    total: mockNotifications.length,
    pending: mockNotifications.filter((n) => n.status === 'pending').length,
    read: mockNotifications.filter((n) => n.status === 'read').length,
    resolved: mockNotifications.filter((n) => n.status === 'resolved').length,
    by_priority: {
      low: mockNotifications.filter((n) => n.priority === 'low').length,
      medium: mockNotifications.filter((n) => n.priority === 'medium').length,
      high: mockNotifications.filter((n) => n.priority === 'high').length,
      critical: mockNotifications.filter((n) => n.priority === 'critical').length,
    },
    by_type: {},
    recent_trend: [],
  }
  return stats
}

function mockGenerateAutomatic(): { generated: number } {
  return { generated: 0 }
}

export default notificationService
