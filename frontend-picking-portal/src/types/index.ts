/**
 * OSE Picking Portal - Type Definitions
 * Version: 2.0.0
 */

// Pallet interface
export interface Pallet {
  id: number;
  pallet_number: string;
  tipo_contenido: string;
  contenido_ids: string;
  pedido_id?: string;
  peso_kg?: number;
  status: string;
  fecha_creacion: string;
  fecha_picking?: string;
  notas?: string;
  creado_por: string;
  qr_code_path?: string;
}

// Package interface
export interface Package {
  id: number;
  tracking_number: string;
  transportista: string;
  order_code?: string;
  cliente_email?: string;
  cliente_nombre?: string;
  dispositivos_info?: string;
  peso_kg?: number;
  status: string;
  fecha_creacion: string;
  fecha_envio?: string;
  fecha_notificacion?: string;
  notas?: string;
  creado_por: string;
  qr_code_path?: string;
}

// Stats interface
export interface Stats {
  palets: {
    total: number;
    preparados: number;
    en_transito: number;
    entregados: number;
  };
  paquetes: {
    total: number;
    preparados: number;
    enviados: number;
    entregados: number;
    emails_pendientes: number;
  };
}

// Transportist type
export type TransportistType = 'Seur' | 'Correos' | 'DHL' | 'UPS' | 'FedEx';

// Status types for pallets and packages
export type PalletStatus = 'preparado' | 'en_transito' | 'entregado' | 'cancelado';
export type PackageStatus = 'preparado' | 'enviado' | 'entregado' | 'devuelto';
