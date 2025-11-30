import axios from 'axios';

const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}/api/v1/app6`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for auth
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ════════════════════════════════════════════════════════════════════════
// PALLET API FUNCTIONS
// ════════════════════════════════════════════════════════════════════════

export const createPallet = async (data: {
  tipo_contenido: string;
  contenido_ids: string[];
  pedido_id?: string;
  peso_kg?: number;
  volumen_m3?: number;
  ubicacion?: string;
  notas?: string;
}) => {
  const params = new URLSearchParams();
  params.append('tipo_contenido', data.tipo_contenido);
  data.contenido_ids.forEach(id => params.append('contenido_ids', id));
  if (data.pedido_id) params.append('pedido_id', data.pedido_id);
  if (data.peso_kg !== undefined) params.append('peso_kg', data.peso_kg.toString());
  if (data.volumen_m3 !== undefined) params.append('volumen_m3', data.volumen_m3.toString());
  if (data.ubicacion) params.append('ubicacion', data.ubicacion);
  if (data.notas) params.append('notas', data.notas);

  const response = await apiClient.post(`/palets/nuevo?${params.toString()}`);
  return response.data;
};

export const getPallets = async (filters?: {
  estado?: string;
  pedido_id?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  limit?: number;
  skip?: number;
}) => {
  const params = new URLSearchParams();
  if (filters?.estado) params.append('estado', filters.estado);
  if (filters?.pedido_id) params.append('pedido_id', filters.pedido_id);
  if (filters?.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
  if (filters?.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);
  if (filters?.limit) params.append('limit', filters.limit.toString());
  if (filters?.skip) params.append('skip', filters.skip.toString());

  const response = await apiClient.get(`/palets?${params.toString()}`);
  return response.data;
};

export const getPalletById = async (id: string) => {
  const response = await apiClient.get(`/palets/${id}`);
  return response.data;
};

export const updatePalletStatus = async (id: string, status: string) => {
  const params = new URLSearchParams();
  params.append('nuevo_estado', status);
  const response = await apiClient.put(`/palets/${id}/estado?${params.toString()}`);
  return response.data;
};

// ════════════════════════════════════════════════════════════════════════
// PACKAGE API FUNCTIONS
// ════════════════════════════════════════════════════════════════════════

export const createPackage = async (data: {
  tracking_number: string;
  transportista: string;
  order_code: string;
  cliente_email: string;
  dispositivos_imeis: string[];
  cliente_nombre?: string;
  direccion_envio?: string;
  ciudad?: string;
  codigo_postal?: string;
  peso_kg?: number;
  enlace_seguimiento?: string;
  notas?: string;
}) => {
  const params = new URLSearchParams();
  params.append('tracking_number', data.tracking_number);
  params.append('transportista', data.transportista);
  params.append('order_code', data.order_code);
  params.append('cliente_email', data.cliente_email);
  data.dispositivos_imeis.forEach(imei => params.append('dispositivos_imeis', imei));
  if (data.cliente_nombre) params.append('cliente_nombre', data.cliente_nombre);
  if (data.direccion_envio) params.append('direccion_envio', data.direccion_envio);
  if (data.ciudad) params.append('ciudad', data.ciudad);
  if (data.codigo_postal) params.append('codigo_postal', data.codigo_postal);
  if (data.peso_kg !== undefined) params.append('peso_kg', data.peso_kg.toString());
  if (data.enlace_seguimiento) params.append('enlace_seguimiento', data.enlace_seguimiento);
  if (data.notas) params.append('notas', data.notas);

  const response = await apiClient.post(`/paquetes/nuevo?${params.toString()}`);
  return response.data;
};

export const getPackages = async (filters?: {
  transportista?: string;
  estado?: string;
  order_code?: string;
  cliente_email?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  limit?: number;
  skip?: number;
}) => {
  const params = new URLSearchParams();
  if (filters?.transportista) params.append('transportista', filters.transportista);
  if (filters?.estado) params.append('estado', filters.estado);
  if (filters?.order_code) params.append('order_code', filters.order_code);
  if (filters?.cliente_email) params.append('cliente_email', filters.cliente_email);
  if (filters?.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
  if (filters?.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);
  if (filters?.limit) params.append('limit', filters.limit.toString());
  if (filters?.skip) params.append('skip', filters.skip.toString());

  const response = await apiClient.get(`/paquetes?${params.toString()}`);
  return response.data;
};

export const getPackageByTracking = async (tracking: string) => {
  const response = await apiClient.get(`/paquetes/${tracking}`);
  return response.data;
};

export const updatePackageStatus = async (tracking: string, status: string) => {
  const params = new URLSearchParams();
  params.append('nuevo_estado', status);
  const response = await apiClient.put(`/paquetes/${tracking}/estado?${params.toString()}`);
  return response.data;
};

export const markAsSent = async (tracking: string) => {
  const response = await apiClient.post(`/paquetes/${tracking}/marcar-enviado`);
  return response.data;
};

export const sendNotification = async (tracking: string) => {
  const response = await apiClient.post(`/paquetes/${tracking}/notificar`);
  return response.data;
};

// ════════════════════════════════════════════════════════════════════════
// STATS API FUNCTION
// ════════════════════════════════════════════════════════════════════════

export const getStats = async () => {
  const response = await apiClient.get('/stats');
  return response.data;
};

export default apiClient;
