/**
 * OSE Platform - Series Notification Service
 * Service for notifying device series (IMEI/ICCID) to clients
 */

import apiService from './api.service'
import type {
  DeviceSerial,
  SeriesNotificationRequest,
  SeriesNotificationResponse,
  NotificationHistoryItem,
  Device,
  Customer,
  ParseResult,
  ValidationResult,
  BulkValidationResult,
  CSVFormat,
} from '../types/series-notification'

const seriesNotificationService = {
  /**
   * Parse input text to extract IMEI/ICCID/Package numbers
   */
  parseInput: (input: string): ParseResult => {
    const lines = input.trim().split('\n').filter(line => line.trim())
    const valid: DeviceSerial[] = []
    const invalid: { input: string; error: string }[] = []

    for (const line of lines) {
      const trimmed = line.trim()

      // Check if it's a package number (25 digits starting with 99)
      if (/^99\d{23}$/.test(trimmed)) {
        valid.push({ imei: '', iccid: '', package_no: trimmed })
        continue
      }

      // Split by space or tab
      const parts = trimmed.split(/\s+/)

      if (parts.length === 1) {
        const value = parts[0]
        // Determine if it's IMEI (15 digits) or ICCID (19-22 alphanumeric chars)
        if (/^\d{15}$/.test(value)) {
          valid.push({ imei: value, iccid: '' })
        } else if (/^[0-9A-F]{19,22}$/i.test(value)) {
          valid.push({ imei: '', iccid: value })
        } else {
          invalid.push({ input: trimmed, error: 'Formato inválido. Debe ser IMEI (15 dígitos) o ICCID (19-22 caracteres alfanuméricos)' })
        }
      } else if (parts.length === 2) {
        const [first, second] = parts
        let imei = ''
        let iccid = ''

        // Identify which is IMEI and which is ICCID
        if (/^\d{15}$/.test(first)) imei = first
        else if (/^[0-9A-F]{19,22}$/i.test(first)) iccid = first

        if (/^\d{15}$/.test(second)) imei = second
        else if (/^[0-9A-F]{19,22}$/i.test(second)) iccid = second

        if (imei || iccid) {
          valid.push({ imei, iccid })
        } else {
          invalid.push({ input: trimmed, error: 'No se pudo identificar IMEI o ICCID válidos' })
        }
      } else {
        invalid.push({ input: trimmed, error: 'Demasiados valores en la línea' })
      }
    }

    return { valid, invalid }
  },

  /**
   * Parse CSV file content
   */
  parseCSV: (content: string): ParseResult => {
    // Remove BOM if present
    const cleaned = content.replace(/^\uFEFF/, '')
    return seriesNotificationService.parseInput(cleaned)
  },

  /**
   * Validate a single device serial
   */
  validateSerial: async (serial: DeviceSerial): Promise<ValidationResult> => {
    try {
      const response = await apiService.post<ValidationResult>(
        '/api/v1/series-notifications/validate',
        { serial }
      )
      return response
    } catch (error) {
      return {
        serial,
        valid: false,
        exists: false,
        already_notified: false,
        error: 'Error al validar dispositivo',
      }
    }
  },

  /**
   * Validate multiple serials
   */
  validateBulk: async (serials: DeviceSerial[]): Promise<BulkValidationResult> => {
    try {
      // Extract IMEIs from DeviceSerial objects - backend expects array of IMEI strings
      const series = serials.map(s => s.imei).filter(imei => imei && imei.trim())

      // Backend response format (Spanish keys)
      interface BackendResponse {
        success: boolean
        total: number
        validos: number
        invalidos: number
        resultados: Array<{
          imei: string
          iccid?: string
          valido: boolean
          existe: boolean
          notificado: boolean
          message: string
          device_id?: string
          marca?: string
          nro_referencia?: string
          estado?: string
          cliente?: string
          cliente_nombre?: string
          operador?: string
          caja_master?: string
          pallet_id?: string
          package_no?: string
          order_number?: string
        }>
      }

      const backendResponse = await apiService.post<BackendResponse>(
        '/api/v1/series-notifications/validate-bulk',
        { series }
      )

      // Transform to frontend format
      const transformedResponse: BulkValidationResult = {
        total: backendResponse.total,
        valid: backendResponse.validos,
        invalid: backendResponse.invalidos,
        already_notified: backendResponse.resultados.filter(r => r.notificado).length,
        results: backendResponse.resultados.map(r => ({
          serial: {
            imei: r.imei,
            iccid: r.iccid || '',
            package_no: r.package_no || '',
            device_id: r.device_id,
            marca: r.marca,
            nro_referencia: r.nro_referencia,
            operador: r.operador,
            caja_master: r.caja_master,
            pallet_id: r.pallet_id,
            order_number: r.order_number || r.nro_referencia
          },
          valid: r.valido,
          exists: r.existe,
          already_notified: r.notificado,
          error: !r.valido || !r.existe || r.notificado ? r.message : undefined
        }))
      }

      return transformedResponse
    } catch (error) {
      console.error('Error validating bulk serials:', error)
      throw error
    }
  },

  /**
   * Get list of customers
   */
  getCustomers: async (): Promise<Customer[]> => {
    try {
      const response = await apiService.get<{ customers: Customer[] }>(
        '/api/v1/series-notifications/config/options'
      )
      return response.customers
    } catch (error) {
      console.error('Error loading customers:', error)
      return []
    }
  },

  /**
   * Send notification
   */
  sendNotification: async (request: SeriesNotificationRequest): Promise<SeriesNotificationResponse> => {
    try {
      const response = await apiService.post<SeriesNotificationResponse>(
        '/api/v1/series-notifications/send',
        request
      )
      return response
    } catch (error) {
      console.error('Error sending notification:', error)
      throw new Error('Error al enviar notificación')
    }
  },

  /**
   * Generate CSV content
   */
  generateCSV: (serials: DeviceSerial[], format: CSVFormat): string => {
    if (format === 'separated') {
      // 📋 Estándar - Two columns: IMEI | ICCID
      let csv = 'IMEI,ICCID\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''},${serial.iccid || ''}\n`
      }
      return csv
    } else if (format === 'unified') {
      // 📝 Simplificado - One column: "IMEI ICCID"
      let csv = 'Número de Serie\n'
      for (const serial of serials) {
        const combined = [serial.imei, serial.iccid].filter(Boolean).join(' ')
        csv += `${combined}\n`
      }
      return csv
    } else if (format === 'detailed') {
      // 📊 Detallado - Multiple columns with brand and reference
      let csv = 'IMEI,ICCID,Paquete,Marca,Referencia\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''},${serial.iccid || ''},${serial.package_no || ''},N/A,N/A\n`
      }
      return csv
    } else if (format === 'compact') {
      // 🗜️ Compacto - Only IMEIs
      let csv = 'IMEI\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''}\n`
      }
      return csv
    } else if (format === 'logistica-trazable') {
      // 📦 Logística Trazable - IMEI, ICCID, Marca, Operador, Caja Master, Pallet
      let csv = 'IMEI,ICCID,Marca,Operador,Caja Master,Pallet\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''},${serial.iccid || ''},${serial.marca || ''},${serial.operador || ''},${serial.caja_master || ''},${serial.pallet_id || ''}\n`
      }
      return csv
    } else if (format === 'imei-marca') {
      // 🏷️ IMEI-Marca - IMEI, Marca
      let csv = 'IMEI,Marca\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''},${serial.marca || ''}\n`
      }
      return csv
    } else if (format === 'inspide') {
      // 🔍 Inspide - IMEI, ICCID (similar a separated pero con nombre diferente)
      let csv = 'IMEI,ICCID\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''},${serial.iccid || ''}\n`
      }
      return csv
    } else if (format === 'clientes-genericos') {
      // 👥 Clientes Genéricos - IMEI, Marca, Número de Orden
      let csv = 'IMEI,Marca,Número de Orden\n'
      for (const serial of serials) {
        csv += `${serial.imei || ''},${serial.marca || ''},${serial.order_number || serial.nro_referencia || ''}\n`
      }
      return csv
    }
    // Default fallback to separated format
    return seriesNotificationService.generateCSV(serials, 'separated')
  },

  /**
   * Download CSV file
   */
  downloadCSV: (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)

    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  },

  /**
   * Get notification history
   */
  getHistory: async (
    page: number = 1,
    limit: number = 20,
    searchEmail?: string,
    searchCustomer?: string,
    searchLocation?: string
  ): Promise<{
    items: NotificationHistoryItem[]
    total: number
    pages: number
  }> => {
    try {
      const params: any = { page, limit }

      if (searchEmail) params.search_email = searchEmail
      if (searchCustomer) params.search_customer = searchCustomer
      if (searchLocation) params.search_location = searchLocation

      const response = await apiService.get<{
        items: NotificationHistoryItem[]
        total: number
        pages: number
      }>('/api/v1/series-notifications/history', {
        params
      })
      return response
    } catch (error) {
      console.error('Error loading history:', error)
      return { items: [], total: 0, pages: 0 }
    }
  },

  /**
   * Get notification details
   */
  getNotificationDetails: async (id: string): Promise<NotificationHistoryItem | null> => {
    try {
      // TODO: Replace with real API call
      // return await apiService.get<NotificationHistoryItem>(`/api/v1/series-notifications/${id}`)

      return null
    } catch (error) {
      return null
    }
  },

  /**
   * Smart scan - Detecta automáticamente el tipo de código y busca los dispositivos
   */
  smartScan: async (code: string): Promise<{
    success: boolean
    type: string
    identifier: string
    count: number
    serials: DeviceSerial[]
    message: string
    lote?: string
    pallet_id?: string
    carton_count?: number
  }> => {
    try {
      const response = await apiService.post(
        '/api/v1/series-notifications/search/smart-scan',
        null,
        {
          params: { code }
        }
      )
      return response
    } catch (error) {
      console.error('Error en smart scan:', error)
      throw new Error('Error al buscar dispositivos')
    }
  },

  /**
   * Buscar dispositivos por lote
   */
  searchByLocation: async (location: string): Promise<{
    success: boolean
    type: string
    identifier: string
    count: number
    serials: DeviceSerial[]
    message: string
  }> => {
    try {
      const response = await apiService.get(
        `/api/v1/series-notifications/search/by-location/${encodeURIComponent(location)}`
      )
      return response
    } catch (error) {
      console.error('Error buscando por lote:', error)
      throw new Error('Error al buscar dispositivos por lote')
    }
  },

  /**
   * Buscar dispositivos por cartón
   */
  searchByCarton: async (cartonId: string): Promise<{
    success: boolean
    type: string
    identifier: string
    count: number
    serials: DeviceSerial[]
    message: string
    pallet_id?: string
    lote?: string
  }> => {
    try {
      const response = await apiService.get(
        `/api/v1/series-notifications/search/by-carton/${encodeURIComponent(cartonId)}`
      )
      return response
    } catch (error) {
      console.error('Error buscando por cartón:', error)
      throw new Error('Error al buscar dispositivos por cartón')
    }
  },

  /**
   * Buscar dispositivos por pallet
   */
  searchByPallet: async (palletId: string): Promise<{
    success: boolean
    type: string
    identifier: string
    count: number
    serials: DeviceSerial[]
    message: string
    lote?: string
    carton_count?: number
  }> => {
    try {
      const response = await apiService.get(
        `/api/v1/series-notifications/search/by-pallet/${encodeURIComponent(palletId)}`
      )
      return response
    } catch (error) {
      console.error('Error buscando por pallet:', error)
      throw new Error('Error al buscar dispositivos por pallet')
    }
  },
}

export default seriesNotificationService
