import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interfaces
export interface Ticket {
  id: number;
  email: string;
  ticket_number: string;
  date: string;
  total: number;
  image_url?: string;
  status: 'pending' | 'invoiced' | 'rejected';
  items: TicketItem[];
  billing_name?: string;
  billing_nif?: string;
  billing_address?: string;
  created_at: string;
}

export interface TicketItem {
  id?: number;
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface TicketCreate {
  email: string;
  ticket_number: string;
  date: string;
  total: number;
  items: TicketItem[];
  billing_name?: string;
  billing_nif?: string;
  billing_address?: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  email: string;
  date: string;
  total: number;
  pdf_url: string;
  ticket_ids: number[];
  billing_name: string;
  billing_nif: string;
  billing_address: string;
  created_at: string;
}

export interface InvoiceCreate {
  email: string;
  ticket_ids: number[];
  billing_name: string;
  billing_nif: string;
  billing_address: string;
}

export interface OCRResult {
  ticket_number?: string;
  date?: string;
  items: TicketItem[];
  total?: number;
}

// API Methods

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Tickets
export const getTicketsByEmail = async (email: string): Promise<Ticket[]> => {
  const response = await api.get(`/public/tickets`, {
    params: { email }
  });
  return response.data;
};

export const getTicketById = async (ticketId: number): Promise<Ticket> => {
  const response = await api.get(`/public/tickets/${ticketId}`);
  return response.data;
};

export const createTicket = async (ticket: TicketCreate): Promise<Ticket> => {
  const response = await api.post('/public/tickets', ticket);
  return response.data;
};

export const uploadTicketImage = async (ticketId: number, file: File): Promise<{ image_url: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post(`/public/tickets/${ticketId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const scanTicketOCR = async (file: File): Promise<OCRResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/public/tickets/scan', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Invoices
export const getInvoicesByEmail = async (email: string): Promise<Invoice[]> => {
  const response = await api.get(`/public/invoices`, {
    params: { email }
  });
  return response.data;
};

export const createInvoice = async (invoice: InvoiceCreate): Promise<Invoice> => {
  // El backend espera los datos como query params
  const response = await api.post('/public/tickets/generate', null, {
    params: {
      email: invoice.email,
      ticket_ids: invoice.ticket_ids.join(','),
      billing_name: invoice.billing_name,
      billing_nif: invoice.billing_nif,
      billing_address: invoice.billing_address,
    }
  });
  return response.data;
};

export const downloadInvoicePDF = async (invoiceId: number): Promise<Blob> => {
  const response = await api.get(`/public/tickets/download/${invoiceId}`, {
    responseType: 'blob',
  });
  return response.data;
};

// Error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
