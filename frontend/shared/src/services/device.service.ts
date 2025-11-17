/**
 * Device Service
 * CRUD operations for devices
 */

import apiService from './api.service'
import type { Device, PaginatedResponse } from '@/types'

class DeviceService {
  private readonly basePath = '/devices'

  /**
   * Get all devices with optional pagination and filters
   */
  async getAll(params?: {
    page?: number
    per_page?: number
    search?: string
    status?: string
    production_line?: number
  }): Promise<PaginatedResponse<Device>> {
    return apiService.get<PaginatedResponse<Device>>(this.basePath, { params })
  }

  /**
   * Get device by ID
   */
  async getById(id: string): Promise<Device> {
    return apiService.get<Device>(`${this.basePath}/${id}`)
  }

  /**
   * Get device by IMEI
   */
  async getByImei(imei: string): Promise<Device> {
    return apiService.get<Device>(`${this.basePath}/imei/${imei}`)
  }

  /**
   * Create new device
   */
  async create(device: Partial<Device>): Promise<Device> {
    return apiService.post<Device>(this.basePath, device)
  }

  /**
   * Update device
   */
  async update(id: string, device: Partial<Device>): Promise<Device> {
    return apiService.put<Device>(`${this.basePath}/${id}`, device)
  }

  /**
   * Partial update device
   */
  async patch(id: string, updates: Partial<Device>): Promise<Device> {
    return apiService.patch<Device>(`${this.basePath}/${id}`, updates)
  }

  /**
   * Delete device
   */
  async delete(id: string): Promise<void> {
    return apiService.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Bulk create devices
   */
  async bulkCreate(devices: Partial<Device>[]): Promise<Device[]> {
    return apiService.post<Device[]>(`${this.basePath}/bulk`, { devices })
  }

  /**
   * Validate device data
   */
  async validate(device: Partial<Device>): Promise<{ valid: boolean; errors?: string[] }> {
    return apiService.post<{ valid: boolean; errors?: string[] }>(`${this.basePath}/validate`, device)
  }
}

// Export singleton instance
export default new DeviceService()
