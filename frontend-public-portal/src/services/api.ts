/**
 * Public Portal - API Service
 * Service for communicating with the backend public API
 */

import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

class PublicApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor - Add token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('public_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - Handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('public_token')
          localStorage.removeItem('public_user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth methods
  async register(data: {
    email: string
    password: string
    nombre: string
    apellidos?: string
    telefono?: string
    empresa?: string
  }) {
    const response = await this.api.post('/public/auth/register', data)
    return response.data
  }

  async login(email: string, password: string) {
    const response = await this.api.post('/public/auth/login', { email, password })
    return response.data
  }

  async getMe() {
    const response = await this.api.get('/public/auth/me')
    return response.data
  }

  async logout() {
    const response = await this.api.post('/public/auth/logout')
    localStorage.removeItem('public_token')
    localStorage.removeItem('public_user')
    return response.data
  }

  // Ticket methods
  async createTicket(data: {
    device_imei: string
    issue_type: string
    description: string
    priority?: string
  }) {
    const response = await this.api.post('/public/tickets/', data)
    return response.data
  }

  async getMyTickets(status?: string) {
    const params = status ? { status_filter: status } : {}
    const response = await this.api.get('/public/tickets/', { params })
    return response.data
  }

  async getTicket(ticketId: string) {
    const response = await this.api.get(`/public/tickets/${ticketId}`)
    return response.data
  }

  async addMessage(ticketId: string, message: string) {
    const response = await this.api.post(`/public/tickets/${ticketId}/messages`, { message })
    return response.data
  }

  async trackTicket(ticketNumber: string, email: string) {
    const response = await this.api.get(`/public/tickets/track/${ticketNumber}`, {
      params: { email }
    })
    return response.data
  }
}

export const apiService = new PublicApiService()
