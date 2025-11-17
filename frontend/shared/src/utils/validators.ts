/**
 * Validation Utilities
 */

import type { ValidationRule } from '@/types'

/**
 * Required field validator
 */
export function required(message = 'This field is required'): ValidationRule {
  return (value: any) => {
    if (value === null || value === undefined || value === '') {
      return message
    }
    if (Array.isArray(value) && value.length === 0) {
      return message
    }
    return true
  }
}

/**
 * Email validator
 */
export function email(message = 'Please enter a valid email'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || message
  }
}

/**
 * Min length validator
 */
export function minLength(min: number, message?: string): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const msg = message || `Minimum ${min} characters required`
    return value.length >= min || msg
  }
}

/**
 * Max length validator
 */
export function maxLength(max: number, message?: string): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const msg = message || `Maximum ${max} characters allowed`
    return value.length <= max || msg
  }
}

/**
 * Min value validator
 */
export function minValue(min: number, message?: string): ValidationRule {
  return (value: number) => {
    if (value === null || value === undefined) return true
    const msg = message || `Minimum value is ${min}`
    return value >= min || msg
  }
}

/**
 * Max value validator
 */
export function maxValue(max: number, message?: string): ValidationRule {
  return (value: number) => {
    if (value === null || value === undefined) return true
    const msg = message || `Maximum value is ${max}`
    return value <= max || msg
  }
}

/**
 * Pattern validator
 */
export function pattern(regex: RegExp, message = 'Invalid format'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    return regex.test(value) || message
  }
}

/**
 * IMEI validator (15 digits)
 */
export function imei(message = 'IMEI must be 15 digits'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^\d{15}$/
    return pattern.test(value) || message
  }
}

/**
 * CCID/ICCID validator (19-20 digits)
 */
export function ccid(message = 'CCID must be 19-20 digits'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^\d{19,20}$/
    return pattern.test(value) || message
  }
}

/**
 * Phone number validator
 */
export function phone(message = 'Invalid phone number'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/
    return pattern.test(value) || message
  }
}

/**
 * URL validator
 */
export function url(message = 'Invalid URL'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    try {
      new URL(value)
      return true
    } catch {
      return message
    }
  }
}

/**
 * Match validator (for password confirmation)
 */
export function match(otherValue: any, message = 'Values do not match'): ValidationRule {
  return (value: any) => {
    return value === otherValue || message
  }
}

/**
 * Numeric validator
 */
export function numeric(message = 'Only numbers allowed'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^\d+$/
    return pattern.test(value) || message
  }
}

/**
 * Alpha validator (letters only)
 */
export function alpha(message = 'Only letters allowed'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^[a-zA-Z]+$/
    return pattern.test(value) || message
  }
}

/**
 * Alphanumeric validator
 */
export function alphanumeric(message = 'Only letters and numbers allowed'): ValidationRule {
  return (value: string) => {
    if (!value) return true
    const pattern = /^[a-zA-Z0-9]+$/
    return pattern.test(value) || message
  }
}
