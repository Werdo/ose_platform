/**
 * Formatting Utilities
 */

import { format, parseISO } from 'date-fns'

/**
 * Format date string
 */
export function formatDate(date: string | Date | null, formatStr = 'dd/MM/yyyy'): string {
  if (!date) return '-'

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return format(dateObj, formatStr)
  } catch {
    return '-'
  }
}

/**
 * Format datetime string
 */
export function formatDateTime(
  date: string | Date | null,
  formatStr = 'dd/MM/yyyy HH:mm:ss'
): string {
  return formatDate(date, formatStr)
}

/**
 * Format currency
 */
export function formatCurrency(value: number | null, currency = 'EUR', locale = 'es-ES'): string {
  if (value === null || value === undefined) return '-'

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(value)
}

/**
 * Format number
 */
export function formatNumber(value: number | null, decimals = 0, locale = 'es-ES'): string {
  if (value === null || value === undefined) return '-'

  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Format percentage
 */
export function formatPercent(value: number | null, decimals = 2): string {
  if (value === null || value === undefined) return '-'

  return `${formatNumber(value, decimals)}%`
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * Truncate string
 */
export function truncate(str: string, length = 50, suffix = '...'): string {
  if (!str) return ''
  if (str.length <= length) return str

  return str.substring(0, length - suffix.length) + suffix
}

/**
 * Capitalize first letter
 */
export function capitalize(str: string): string {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Uppercase all words
 */
export function titleCase(str: string): string {
  if (!str) return ''
  return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
}

/**
 * Format phone number
 */
export function formatPhone(phone: string): string {
  if (!phone) return '-'

  // Simple format for Spanish phones: +34 XXX XXX XXX
  const cleaned = phone.replace(/\D/g, '')

  if (cleaned.length === 9) {
    return `${cleaned.substring(0, 3)} ${cleaned.substring(3, 6)} ${cleaned.substring(6)}`
  }

  return phone
}

/**
 * Format IMEI (groups of 2-6-6-1)
 */
export function formatIMEI(imei: string): string {
  if (!imei) return '-'

  const cleaned = imei.replace(/\D/g, '')

  if (cleaned.length === 15) {
    return `${cleaned.substring(0, 2)} ${cleaned.substring(2, 8)} ${cleaned.substring(8, 14)} ${cleaned.substring(14)}`
  }

  return imei
}

/**
 * Format CCID/ICCID (groups of 4)
 */
export function formatCCID(ccid: string): string {
  if (!ccid) return '-'

  const cleaned = ccid.replace(/\D/g, '')

  return cleaned.match(/.{1,4}/g)?.join(' ') || ccid
}

/**
 * Format boolean as Yes/No
 */
export function formatBoolean(value: boolean | null, yesText = 'Yes', noText = 'No'): string {
  if (value === null || value === undefined) return '-'
  return value ? yesText : noText
}

/**
 * Format status badge color
 */
export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    // Device statuses
    pending: 'orange',
    in_production: 'blue',
    quality_check: 'purple',
    approved: 'green',
    rejected: 'red',
    in_stock: 'cyan',
    shipped: 'teal',
    installed: 'green',
    active: 'success',
    inactive: 'grey',
    rma: 'orange',
    retired: 'grey',

    // Ticket statuses
    open: 'blue',
    in_progress: 'orange',
    waiting_customer: 'purple',
    resolved: 'green',
    closed: 'grey',

    // Priority
    low: 'grey',
    medium: 'blue',
    high: 'orange',
    critical: 'red',

    // Production order
    completed: 'green',
    cancelled: 'red',
  }

  return statusColors[status.toLowerCase()] || 'grey'
}
