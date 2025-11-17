/**
 * OSE Platform - Invoice Types
 * Type definitions for App5: Invoice Management
 */

export interface Ticket {
  id: string
  ticket_number: string
  customer_email: string
  upload_date: string
  image_url?: string
  status: 'pending' | 'processed' | 'invoiced' | 'error'
  ocr_data?: TicketOCRData
  processed_at?: string
  error_message?: string
}

export interface TicketOCRData {
  ticket_number?: string
  date?: string
  items?: TicketItem[]
  subtotal?: number
  tax?: number
  total?: number
  merchant?: string
  confidence?: number
}

export interface TicketItem {
  description: string
  quantity: number
  unit_price: number
  total: number
}

export interface Invoice {
  id: string
  invoice_number: string
  ticket_id?: string
  customer_email: string
  customer_name?: string
  customer_nif?: string
  customer_address?: string
  issue_date: string
  due_date?: string
  items: InvoiceItem[]
  subtotal: number
  tax_rate: number
  tax_amount: number
  total: number
  status: 'draft' | 'issued' | 'sent' | 'paid' | 'cancelled'
  pdf_url?: string
  sent_at?: string
  paid_at?: string
  cancelled_at?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface InvoiceItem {
  description: string
  quantity: number
  unit_price: number
  total: number
}

export interface CompanyConfig {
  name: string
  nif: string
  address: string
  city?: string
  postal_code?: string
  phone?: string
  email?: string
  logo_url?: string
}

export interface InvoiceConfig {
  series: string
  next_number: number
  reset_yearly: boolean
  tax_rate: number
  template: string
  primary_color?: string
  secondary_color?: string
  footer_text?: string
}

export interface OCRConfig {
  enabled: boolean
  confidence_threshold: number
  allow_manual_entry: boolean
}

export interface AppConfig {
  company: CompanyConfig
  invoice: InvoiceConfig
  ocr: OCRConfig
}

export interface InvoiceStats {
  total_tickets: number
  pending_tickets: number
  processed_tickets: number
  total_invoices: number
  draft_invoices: number
  issued_invoices: number
  sent_invoices: number
  paid_invoices: number
  total_amount: number
  month_amount: number
}

export interface TicketFilters {
  status?: string
  email?: string
  date_from?: string
  date_to?: string
  search?: string
}

export interface InvoiceFilters {
  status?: string
  customer?: string
  date_from?: string
  date_to?: string
  search?: string
}

export interface TicketUploadResponse {
  ticket: Ticket
  message: string
}

export interface InvoiceGenerateRequest {
  ticket_id?: string
  customer_email: string
  customer_name: string
  customer_nif?: string
  customer_address?: string
  items: InvoiceItem[]
  notes?: string
}

export interface InvoiceUpdateRequest {
  status?: string
  customer_name?: string
  customer_nif?: string
  customer_address?: string
  items?: InvoiceItem[]
  notes?: string
}
