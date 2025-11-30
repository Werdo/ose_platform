import apiClient from './api';

// ════════════════════════════════════════════════════════════════════════
// DELIVERY NOTES / ALBARANES EST912 - API FUNCTIONS
// ════════════════════════════════════════════════════════════════════════

const DELIVERY_API_BASE = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}/api/v1/delivery-notes`;

export interface DeliveryNote {
  id?: string;
  pallet_code: string;
  delivery_note_number: string;
  order_number?: string;
  customer_name: string;
  customer_code?: string;
  total_boxes: number;
  box_configuration?: string;
  total_units?: number;
  product_description?: string;
  sender_name: string;
  sender_address?: string;
  destination_address?: string;
  total_pallets_in_order: number;
  pallet_number_in_order: number;
  labels_to_print: number;
  status: 'preparado' | 'enviado' | 'entregado' | 'cancelado';
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  notes?: string;
}

export const getDeliveryNotes = async (filters?: {
  status?: string;
  order_number?: string;
  customer_name?: string;
  skip?: number;
  limit?: number;
}) => {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.order_number) params.append('order_number', filters.order_number);
  if (filters?.customer_name) params.append('customer_name', filters.customer_name);
  if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
  if (filters?.limit) params.append('limit', filters.limit.toString());

  const response = await apiClient.get(`${DELIVERY_API_BASE}?${params.toString()}`);
  return response.data;
};

export const getDeliveryNote = async (id: string) => {
  const response = await apiClient.get(`${DELIVERY_API_BASE}/${id}`);
  return response.data;
};

export const getByPalletCode = async (palletCode: string) => {
  const response = await apiClient.get(`${DELIVERY_API_BASE}/by-pallet-code/${palletCode}`);
  return response.data;
};

export const createDeliveryNote = async (data: {
  delivery_note_number: string;
  customer_name: string;
  total_boxes: number;
  order_number?: string;
  customer_code?: string;
  box_configuration?: string;
  total_units?: number;
  product_description?: string;
  sender_name?: string;
  sender_address?: string;
  destination_address?: string;
  total_pallets_in_order?: number;
  pallet_number_in_order?: number;
  labels_to_print?: number;
  notes?: string;
}) => {
  const response = await apiClient.post(DELIVERY_API_BASE, data);
  return response.data;
};

export const updateDeliveryNote = async (id: string, data: Partial<DeliveryNote>) => {
  const response = await apiClient.put(`${DELIVERY_API_BASE}/${id}`, data);
  return response.data;
};

export const updateStatus = async (id: string, status: string) => {
  const params = new URLSearchParams();
  params.append('status', status);
  const response = await apiClient.put(`${DELIVERY_API_BASE}/${id}/status?${params.toString()}`);
  return response.data;
};

export const getStatistics = async () => {
  const response = await apiClient.get(`${DELIVERY_API_BASE}/stats/summary`);
  return response.data;
};

export const previewNextCode = async () => {
  const response = await apiClient.get(`${DELIVERY_API_BASE}/preview/next-code`);
  return response.data;
};

// ════════════════════════════════════════════════════════════════════════
// LABEL GENERATION
// ════════════════════════════════════════════════════════════════════════

export const generatePdfLabel = async (
  deliveryNoteId: string,
  labelsCount: number = 1,
  labelSize: 'A6' | '100x150' | '100x100' = 'A6'
): Promise<Blob> => {
  const params = new URLSearchParams();
  params.append('labels_count', labelsCount.toString());
  params.append('label_size', labelSize);

  const response = await apiClient.get(
    `${DELIVERY_API_BASE}/${deliveryNoteId}/label/pdf?${params.toString()}`,
    { responseType: 'blob' }
  );

  return response.data;
};

export const generateZplLabel = async (
  deliveryNoteId: string,
  dpi: number = 203,
  labelWidth: number = 100,
  labelHeight: number = 150
) => {
  const params = new URLSearchParams();
  params.append('dpi', dpi.toString());
  params.append('label_width', labelWidth.toString());
  params.append('label_height', labelHeight.toString());

  const response = await apiClient.get(
    `${DELIVERY_API_BASE}/${deliveryNoteId}/label/zpl?${params.toString()}`
  );

  return response.data;
};

export const generateHtmlPreview = async (deliveryNoteId: string): Promise<string> => {
  const response = await apiClient.get(
    `${DELIVERY_API_BASE}/${deliveryNoteId}/label/preview`,
    { responseType: 'text' }
  );

  return response.data;
};
