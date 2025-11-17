/**
 * ESTRUCTURA MONGODB - OVERSUN ENERGY
 * Sistema de Gestión, Trazabilidad y Post-Venta
 * 
 * Arquitectura optimizada para:
 * - Trazabilidad completa de dispositivos
 * - Gestión de producción
 * - Control de calidad
 * - Servicio post-venta
 * - Garantías y RMA
 */

// ==========================================
// 1. COLECCIÓN: devices (Dispositivos)
// Registro maestro de cada dispositivo único
// ==========================================
db.createCollection("devices", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["imei", "ccid", "production_order", "status", "created_at"],
      properties: {
        imei: {
          bsonType: "string",
          description: "IMEI único del dispositivo - requerido",
          pattern: "^[0-9]{15,17}$"
        },
        ccid: {
          bsonType: "string",
          description: "ICCID de la SIM - requerido",
          pattern: "^[0-9]{18,22}$"
        },
        production_order: {
          bsonType: "string",
          description: "Referencia a orden de producción - requerido"
        },
        sku: {
          bsonType: "int",
          description: "Código SKU del producto"
        },
        reference_number: {
          bsonType: "string",
          description: "Número de referencia/modelo"
        },
        brand: {
          bsonType: "string",
          description: "Marca del dispositivo"
        },
        batch: {
          bsonType: "int",
          description: "Lote de producción"
        },
        production_line: {
          bsonType: "int",
          enum: [1, 2, 3],
          description: "Línea de producción (1, 2 o 3)"
        },
        status: {
          bsonType: "string",
          enum: ["in_production", "quality_control", "approved", "rejected", "shipped", "in_service", "faulty", "rma", "retired"],
          description: "Estado actual del dispositivo"
        },
        quality_control: {
          bsonType: "object",
          properties: {
            passed: { bsonType: "bool" },
            inspection_date: { bsonType: "date" },
            inspector: { bsonType: "string" },
            notes: { bsonType: "string" },
            defects: { bsonType: "array", items: { bsonType: "string" } }
          }
        },
        shipping_info: {
          bsonType: "object",
          properties: {
            shipped_date: { bsonType: "date" },
            destination: { bsonType: "string" },
            tracking_number: { bsonType: "string" },
            customer_id: { bsonType: "objectId" }
          }
        },
        warranty: {
          bsonType: "object",
          properties: {
            start_date: { bsonType: "date" },
            end_date: { bsonType: "date" },
            coverage_type: { bsonType: "string" },
            extended: { bsonType: "bool" }
          }
        },
        current_location: {
          bsonType: "string",
          description: "Ubicación actual (warehouse, customer, service_center, etc.)"
        },
        firmware_version: {
          bsonType: "string",
          description: "Versión de firmware instalada"
        },
        hardware_version: {
          bsonType: "string",
          description: "Versión de hardware"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de registro inicial - requerido"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización"
        },
        metadata: {
          bsonType: "object",
          description: "Datos adicionales flexibles"
        }
      }
    }
  }
});

// Índices para devices
db.devices.createIndex({ "imei": 1 }, { unique: true });
db.devices.createIndex({ "ccid": 1 }, { unique: true });
db.devices.createIndex({ "production_order": 1 });
db.devices.createIndex({ "status": 1 });
db.devices.createIndex({ "sku": 1 });
db.devices.createIndex({ "created_at": -1 });
db.devices.createIndex({ "shipping_info.customer_id": 1 });
db.devices.createIndex({ "warranty.end_date": 1 });

// ==========================================
// 2. COLECCIÓN: production_orders (Órdenes de Producción)
// Gestión de órdenes de producción
// ==========================================
db.createCollection("production_orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["order_number", "reference_number", "quantity", "status", "created_at"],
      properties: {
        order_number: {
          bsonType: "string",
          description: "Número único de orden - requerido"
        },
        reference_number: {
          bsonType: "string",
          description: "Número de referencia del producto - requerido"
        },
        sku: {
          bsonType: "int",
          description: "Código SKU"
        },
        brand: {
          bsonType: "string",
          description: "Marca"
        },
        quantity: {
          bsonType: "int",
          minimum: 1,
          description: "Cantidad total a producir - requerido"
        },
        produced: {
          bsonType: "int",
          minimum: 0,
          description: "Cantidad producida"
        },
        approved: {
          bsonType: "int",
          minimum: 0,
          description: "Cantidad aprobada en control de calidad"
        },
        rejected: {
          bsonType: "int",
          minimum: 0,
          description: "Cantidad rechazada"
        },
        status: {
          bsonType: "string",
          enum: ["pending", "in_progress", "on_hold", "completed", "cancelled"],
          description: "Estado de la orden - requerido"
        },
        production_line: {
          bsonType: "int",
          enum: [1, 2, 3],
          description: "Línea asignada"
        },
        responsible: {
          bsonType: "string",
          description: "Responsable de la orden"
        },
        start_date: {
          bsonType: "date",
          description: "Fecha de inicio de producción"
        },
        end_date: {
          bsonType: "date",
          description: "Fecha de finalización"
        },
        estimated_completion: {
          bsonType: "date",
          description: "Fecha estimada de finalización"
        },
        batches: {
          bsonType: "array",
          description: "Información de lotes",
          items: {
            bsonType: "object",
            properties: {
              batch_number: { bsonType: "int" },
              quantity: { bsonType: "int" },
              start_date: { bsonType: "date" },
              end_date: { bsonType: "date" },
              operator: { bsonType: "string" },
              workstation: { bsonType: "int" }
            }
          }
        },
        labels_required: {
          bsonType: "object",
          properties: {
            label_24: { bsonType: "int" },
            label_48: { bsonType: "int" },
            label_80: { bsonType: "int" },
            label_96: { bsonType: "int" }
          }
        },
        notes: {
          bsonType: "string",
          description: "Notas o detalles adicionales"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación - requerido"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización"
        }
      }
    }
  }
});

// Índices para production_orders
db.production_orders.createIndex({ "order_number": 1 }, { unique: true });
db.production_orders.createIndex({ "status": 1 });
db.production_orders.createIndex({ "reference_number": 1 });
db.production_orders.createIndex({ "created_at": -1 });
db.production_orders.createIndex({ "production_line": 1 });

// ==========================================
// 3. COLECCIÓN: device_events (Trazabilidad)
// Historial completo de eventos de cada dispositivo
// ==========================================
db.createCollection("device_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["device_id", "event_type", "timestamp"],
      properties: {
        device_id: {
          bsonType: "objectId",
          description: "Referencia al dispositivo - requerido"
        },
        imei: {
          bsonType: "string",
          description: "IMEI para consultas rápidas"
        },
        event_type: {
          bsonType: "string",
          enum: [
            "created",
            "production_started",
            "production_completed",
            "quality_check_passed",
            "quality_check_failed",
            "packed",
            "shipped",
            "delivered",
            "activated",
            "warranty_started",
            "service_request_opened",
            "repair_started",
            "repair_completed",
            "replaced",
            "returned",
            "retired"
          ],
          description: "Tipo de evento - requerido"
        },
        timestamp: {
          bsonType: "date",
          description: "Fecha y hora del evento - requerido"
        },
        operator: {
          bsonType: "string",
          description: "Usuario u operador que registró el evento"
        },
        production_order: {
          bsonType: "string",
          description: "Orden de producción asociada"
        },
        batch: {
          bsonType: "int",
          description: "Lote asociado"
        },
        workstation: {
          bsonType: "int",
          description: "Puesto de trabajo"
        },
        production_line: {
          bsonType: "int",
          description: "Línea de producción"
        },
        old_status: {
          bsonType: "string",
          description: "Estado anterior"
        },
        new_status: {
          bsonType: "string",
          description: "Nuevo estado"
        },
        location: {
          bsonType: "string",
          description: "Ubicación física"
        },
        data: {
          bsonType: "object",
          description: "Datos adicionales del evento (flexible)"
        },
        notes: {
          bsonType: "string",
          description: "Notas del evento"
        }
      }
    }
  }
});

// Índices para device_events
db.device_events.createIndex({ "device_id": 1, "timestamp": -1 });
db.device_events.createIndex({ "imei": 1, "timestamp": -1 });
db.device_events.createIndex({ "event_type": 1, "timestamp": -1 });
db.device_events.createIndex({ "timestamp": -1 });
db.device_events.createIndex({ "production_order": 1 });

// ==========================================
// 4. COLECCIÓN: service_tickets (Tickets Post-Venta)
// Gestión de incidencias y servicios técnicos
// ==========================================
db.createCollection("service_tickets", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["ticket_number", "device_id", "customer_id", "issue_type", "status", "created_at"],
      properties: {
        ticket_number: {
          bsonType: "string",
          description: "Número único de ticket - requerido"
        },
        device_id: {
          bsonType: "objectId",
          description: "Referencia al dispositivo - requerido"
        },
        imei: {
          bsonType: "string",
          description: "IMEI del dispositivo"
        },
        customer_id: {
          bsonType: "objectId",
          description: "ID del cliente - requerido"
        },
        issue_type: {
          bsonType: "string",
          enum: [
            "hardware_failure",
            "software_issue",
            "connectivity_problem",
            "battery_issue",
            "screen_damage",
            "water_damage",
            "configuration_help",
            "warranty_claim",
            "replacement_request",
            "other"
          ],
          description: "Tipo de incidencia - requerido"
        },
        priority: {
          bsonType: "string",
          enum: ["low", "medium", "high", "critical"],
          description: "Prioridad del ticket"
        },
        status: {
          bsonType: "string",
          enum: ["open", "in_progress", "waiting_parts", "waiting_customer", "resolved", "closed", "cancelled"],
          description: "Estado del ticket - requerido"
        },
        description: {
          bsonType: "string",
          description: "Descripción del problema"
        },
        reported_by: {
          bsonType: "object",
          properties: {
            name: { bsonType: "string" },
            email: { bsonType: "string" },
            phone: { bsonType: "string" }
          }
        },
        assigned_to: {
          bsonType: "string",
          description: "Técnico asignado"
        },
        diagnosis: {
          bsonType: "string",
          description: "Diagnóstico del problema"
        },
        solution: {
          bsonType: "string",
          description: "Solución aplicada"
        },
        warranty_valid: {
          bsonType: "bool",
          description: "Si está cubierto por garantía"
        },
        repair_cost: {
          bsonType: "double",
          description: "Costo de reparación (si aplica)"
        },
        parts_used: {
          bsonType: "array",
          description: "Piezas utilizadas en la reparación",
          items: {
            bsonType: "object",
            properties: {
              part_number: { bsonType: "string" },
              description: { bsonType: "string" },
              quantity: { bsonType: "int" },
              cost: { bsonType: "double" }
            }
          }
        },
        service_location: {
          bsonType: "string",
          description: "Centro de servicio"
        },
        expected_resolution_date: {
          bsonType: "date",
          description: "Fecha esperada de resolución"
        },
        resolution_date: {
          bsonType: "date",
          description: "Fecha de resolución real"
        },
        customer_satisfaction: {
          bsonType: "int",
          minimum: 1,
          maximum: 5,
          description: "Valoración del cliente (1-5)"
        },
        attachments: {
          bsonType: "array",
          description: "Archivos adjuntos (fotos, documentos)",
          items: {
            bsonType: "object",
            properties: {
              filename: { bsonType: "string" },
              url: { bsonType: "string" },
              type: { bsonType: "string" },
              uploaded_at: { bsonType: "date" }
            }
          }
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación - requerido"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización"
        },
        notes: {
          bsonType: "array",
          description: "Notas y actualizaciones del ticket",
          items: {
            bsonType: "object",
            properties: {
              author: { bsonType: "string" },
              note: { bsonType: "string" },
              timestamp: { bsonType: "date" },
              internal: { bsonType: "bool" }
            }
          }
        }
      }
    }
  }
});

// Índices para service_tickets
db.service_tickets.createIndex({ "ticket_number": 1 }, { unique: true });
db.service_tickets.createIndex({ "device_id": 1 });
db.service_tickets.createIndex({ "imei": 1 });
db.service_tickets.createIndex({ "customer_id": 1 });
db.service_tickets.createIndex({ "status": 1 });
db.service_tickets.createIndex({ "priority": 1, "status": 1 });
db.service_tickets.createIndex({ "created_at": -1 });
db.service_tickets.createIndex({ "assigned_to": 1, "status": 1 });

// ==========================================
// 5. COLECCIÓN: customers (Clientes)
// Información de clientes finales o distribuidores
// ==========================================
db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customer_code", "type", "status", "created_at"],
      properties: {
        customer_code: {
          bsonType: "string",
          description: "Código único de cliente - requerido"
        },
        type: {
          bsonType: "string",
          enum: ["end_user", "distributor", "reseller", "enterprise"],
          description: "Tipo de cliente - requerido"
        },
        company_name: {
          bsonType: "string",
          description: "Nombre de empresa (si aplica)"
        },
        contact_person: {
          bsonType: "object",
          properties: {
            first_name: { bsonType: "string" },
            last_name: { bsonType: "string" },
            position: { bsonType: "string" },
            email: { bsonType: "string" },
            phone: { bsonType: "string" },
            mobile: { bsonType: "string" }
          }
        },
        address: {
          bsonType: "object",
          properties: {
            street: { bsonType: "string" },
            city: { bsonType: "string" },
            state: { bsonType: "string" },
            postal_code: { bsonType: "string" },
            country: { bsonType: "string" }
          }
        },
        tax_id: {
          bsonType: "string",
          description: "CIF/NIF/VAT"
        },
        status: {
          bsonType: "string",
          enum: ["active", "inactive", "blocked"],
          description: "Estado del cliente - requerido"
        },
        devices_count: {
          bsonType: "int",
          description: "Número total de dispositivos"
        },
        service_tickets_count: {
          bsonType: "int",
          description: "Número total de tickets"
        },
        credit_limit: {
          bsonType: "double",
          description: "Límite de crédito"
        },
        payment_terms: {
          bsonType: "int",
          description: "Días de pago"
        },
        notes: {
          bsonType: "string",
          description: "Notas adicionales"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de alta - requerido"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización"
        }
      }
    }
  }
});

// Índices para customers
db.customers.createIndex({ "customer_code": 1 }, { unique: true });
db.customers.createIndex({ "type": 1 });
db.customers.createIndex({ "status": 1 });
db.customers.createIndex({ "contact_person.email": 1 });
db.customers.createIndex({ "company_name": 1 });

// ==========================================
// 6. COLECCIÓN: employees (Personal)
// Personal operativo y administrativo
// ==========================================
db.createCollection("employees", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["employee_id", "name", "role", "status", "created_at"],
      properties: {
        employee_id: {
          bsonType: "string",
          description: "ID único del empleado - requerido"
        },
        name: {
          bsonType: "string",
          description: "Nombre completo - requerido"
        },
        surname: {
          bsonType: "string",
          description: "Apellidos"
        },
        role: {
          bsonType: "string",
          enum: ["operator", "supervisor", "quality_inspector", "technician", "admin", "manager"],
          description: "Rol del empleado - requerido"
        },
        status: {
          bsonType: "string",
          enum: ["active", "inactive", "on_leave"],
          description: "Estado - requerido"
        },
        permissions: {
          bsonType: "object",
          properties: {
            production_line1_station1: { bsonType: "bool" },
            production_line1_station2: { bsonType: "bool" },
            production_line2_station1: { bsonType: "bool" },
            production_line2_station2: { bsonType: "bool" },
            production_line3_station1: { bsonType: "bool" },
            production_line3_station2: { bsonType: "bool" },
            quality_control: { bsonType: "bool" },
            admin_access: { bsonType: "bool" }
          }
        },
        assigned_lines: {
          bsonType: "array",
          description: "Líneas asignadas",
          items: { bsonType: "int" }
        },
        contact: {
          bsonType: "object",
          properties: {
            email: { bsonType: "string" },
            phone: { bsonType: "string" },
            emergency_contact: { bsonType: "string" }
          }
        },
        hire_date: {
          bsonType: "date",
          description: "Fecha de contratación"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de registro - requerido"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización"
        }
      }
    }
  }
});

// Índices para employees
db.employees.createIndex({ "employee_id": 1 }, { unique: true });
db.employees.createIndex({ "role": 1, "status": 1 });
db.employees.createIndex({ "status": 1 });

// ==========================================
// 7. COLECCIÓN: quality_control (Control de Calidad)
// Registros detallados de inspecciones
// ==========================================
db.createCollection("quality_control", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["device_id", "inspection_date", "inspector", "result", "production_line"],
      properties: {
        device_id: {
          bsonType: "objectId",
          description: "Referencia al dispositivo - requerido"
        },
        imei: {
          bsonType: "string",
          description: "IMEI del dispositivo"
        },
        ccid: {
          bsonType: "string",
          description: "ICCID de la SIM"
        },
        production_order: {
          bsonType: "string",
          description: "Orden de producción"
        },
        production_line: {
          bsonType: "int",
          enum: [1, 2, 3],
          description: "Línea de producción - requerido"
        },
        inspection_date: {
          bsonType: "date",
          description: "Fecha de inspección - requerido"
        },
        inspector: {
          bsonType: "string",
          description: "Inspector asignado - requerido"
        },
        result: {
          bsonType: "string",
          enum: ["passed", "failed", "conditional"],
          description: "Resultado de la inspección - requerido"
        },
        checklist: {
          bsonType: "object",
          properties: {
            physical_appearance: { bsonType: "bool" },
            functionality_test: { bsonType: "bool" },
            connectivity_test: { bsonType: "bool" },
            firmware_verification: { bsonType: "bool" },
            label_verification: { bsonType: "bool" },
            packaging: { bsonType: "bool" }
          }
        },
        defects_found: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              category: { bsonType: "string" },
              severity: { bsonType: "string", enum: ["minor", "major", "critical"] },
              description: { bsonType: "string" }
            }
          }
        },
        corrective_actions: {
          bsonType: "string",
          description: "Acciones correctivas tomadas"
        },
        retest_required: {
          bsonType: "bool",
          description: "Si requiere reinspección"
        },
        retest_date: {
          bsonType: "date",
          description: "Fecha de reinspección"
        },
        notes: {
          bsonType: "string",
          description: "Notas adicionales"
        }
      }
    }
  }
});

// Índices para quality_control
db.quality_control.createIndex({ "device_id": 1 });
db.quality_control.createIndex({ "imei": 1 });
db.quality_control.createIndex({ "inspection_date": -1 });
db.quality_control.createIndex({ "result": 1, "production_line": 1 });
db.quality_control.createIndex({ "production_order": 1 });

// ==========================================
// 8. COLECCIÓN: rma_cases (RMA - Return Merchandise Authorization)
// Gestión de devoluciones y reemplazos
// ==========================================
db.createCollection("rma_cases", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["rma_number", "device_id", "customer_id", "reason", "status", "created_at"],
      properties: {
        rma_number: {
          bsonType: "string",
          description: "Número único de RMA - requerido"
        },
        device_id: {
          bsonType: "objectId",
          description: "Dispositivo original - requerido"
        },
        imei: {
          bsonType: "string",
          description: "IMEI del dispositivo"
        },
        customer_id: {
          bsonType: "objectId",
          description: "Cliente - requerido"
        },
        service_ticket_id: {
          bsonType: "objectId",
          description: "Ticket de servicio relacionado"
        },
        reason: {
          bsonType: "string",
          enum: ["doa", "hardware_failure", "software_issue", "customer_dissatisfaction", "wrong_product", "other"],
          description: "Motivo de devolución - requerido"
        },
        status: {
          bsonType: "string",
          enum: ["requested", "approved", "rejected", "device_received", "inspecting", "replacement_sent", "refund_processed", "closed"],
          description: "Estado del RMA - requerido"
        },
        warranty_status: {
          bsonType: "string",
          enum: ["in_warranty", "out_of_warranty", "extended_warranty"],
          description: "Estado de garantía"
        },
        authorization_date: {
          bsonType: "date",
          description: "Fecha de autorización"
        },
        authorized_by: {
          bsonType: "string",
          description: "Persona que autorizó"
        },
        device_received_date: {
          bsonType: "date",
          description: "Fecha de recepción del dispositivo"
        },
        inspection_result: {
          bsonType: "string",
          enum: ["defective_confirmed", "defect_not_found", "customer_damage", "normal_wear"],
          description: "Resultado de inspección"
        },
        resolution_type: {
          bsonType: "string",
          enum: ["replacement", "repair", "refund", "credit_note"],
          description: "Tipo de resolución"
        },
        replacement_device_id: {
          bsonType: "objectId",
          description: "Dispositivo de reemplazo"
        },
        replacement_shipped_date: {
          bsonType: "date",
          description: "Fecha de envío del reemplazo"
        },
        refund_amount: {
          bsonType: "double",
          description: "Monto de reembolso"
        },
        refund_date: {
          bsonType: "date",
          description: "Fecha de reembolso"
        },
        shipping_cost: {
          bsonType: "double",
          description: "Costo de envío"
        },
        customer_notes: {
          bsonType: "string",
          description: "Notas del cliente"
        },
        internal_notes: {
          bsonType: "string",
          description: "Notas internas"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación - requerido"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización"
        },
        closed_at: {
          bsonType: "date",
          description: "Fecha de cierre"
        }
      }
    }
  }
});

// Índices para rma_cases
db.rma_cases.createIndex({ "rma_number": 1 }, { unique: true });
db.rma_cases.createIndex({ "device_id": 1 });
db.rma_cases.createIndex({ "customer_id": 1 });
db.rma_cases.createIndex({ "status": 1 });
db.rma_cases.createIndex({ "created_at": -1 });

// ==========================================
// 9. COLECCIÓN: inventory (Inventario)
// Control de stock de componentes y productos
// ==========================================
db.createCollection("inventory", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["part_number", "description", "quantity", "unit", "updated_at"],
      properties: {
        part_number: {
          bsonType: "string",
          description: "Número de parte único - requerido"
        },
        description: {
          bsonType: "string",
          description: "Descripción del componente - requerido"
        },
        category: {
          bsonType: "string",
          enum: ["finished_product", "component", "packaging", "tool", "consumable"],
          description: "Categoría del artículo"
        },
        quantity: {
          bsonType: "int",
          minimum: 0,
          description: "Cantidad actual - requerido"
        },
        unit: {
          bsonType: "string",
          description: "Unidad de medida (pcs, kg, m, etc.) - requerido"
        },
        minimum_stock: {
          bsonType: "int",
          description: "Stock mínimo"
        },
        maximum_stock: {
          bsonType: "int",
          description: "Stock máximo"
        },
        location: {
          bsonType: "string",
          description: "Ubicación en almacén"
        },
        supplier: {
          bsonType: "string",
          description: "Proveedor principal"
        },
        unit_cost: {
          bsonType: "double",
          description: "Costo unitario"
        },
        last_purchase_date: {
          bsonType: "date",
          description: "Última fecha de compra"
        },
        updated_at: {
          bsonType: "date",
          description: "Última actualización - requerido"
        }
      }
    }
  }
});

// Índices para inventory
db.inventory.createIndex({ "part_number": 1 }, { unique: true });
db.inventory.createIndex({ "category": 1 });
db.inventory.createIndex({ "quantity": 1 });

// ==========================================
// 10. COLECCIÓN: metrics (Métricas y KPIs)
// Agregación de métricas de producción y post-venta
// ==========================================
db.createCollection("metrics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["metric_type", "period", "date", "value"],
      properties: {
        metric_type: {
          bsonType: "string",
          enum: [
            "production_daily",
            "production_weekly",
            "production_monthly",
            "quality_rate",
            "rejection_rate",
            "service_tickets_opened",
            "service_tickets_resolved",
            "average_resolution_time",
            "rma_rate",
            "customer_satisfaction",
            "warranty_claims"
          ],
          description: "Tipo de métrica - requerido"
        },
        period: {
          bsonType: "string",
          enum: ["daily", "weekly", "monthly", "quarterly", "yearly"],
          description: "Período de la métrica - requerido"
        },
        date: {
          bsonType: "date",
          description: "Fecha de la métrica - requerido"
        },
        value: {
          bsonType: "double",
          description: "Valor de la métrica - requerido"
        },
        production_line: {
          bsonType: "int",
          description: "Línea específica (si aplica)"
        },
        product_sku: {
          bsonType: "int",
          description: "SKU específico (si aplica)"
        },
        metadata: {
          bsonType: "object",
          description: "Datos adicionales de contexto"
        }
      }
    }
  }
});

// Índices para metrics
db.metrics.createIndex({ "metric_type": 1, "date": -1 });
db.metrics.createIndex({ "period": 1, "date": -1 });
db.metrics.createIndex({ "production_line": 1, "date": -1 });

// ==========================================
// VISTAS ÚTILES PARA CONSULTAS FRECUENTES
// ==========================================

// Vista: Dispositivos en garantía activa
db.createView(
  "devices_under_warranty",
  "devices",
  [
    {
      $match: {
        "warranty.end_date": { $gte: new Date() },
        status: { $in: ["approved", "shipped", "in_service"] }
      }
    },
    {
      $project: {
        imei: 1,
        ccid: 1,
        sku: 1,
        reference_number: 1,
        warranty: 1,
        shipping_info: 1,
        current_location: 1
      }
    }
  ]
);

// Vista: Tickets abiertos por prioridad
db.createView(
  "open_tickets_by_priority",
  "service_tickets",
  [
    {
      $match: {
        status: { $in: ["open", "in_progress", "waiting_parts"] }
      }
    },
    {
      $group: {
        _id: "$priority",
        count: { $sum: 1 },
        tickets: { $push: "$$ROOT" }
      }
    },
    {
      $sort: { "_id": 1 }
    }
  ]
);

// Vista: Producción del día actual
db.createView(
  "today_production",
  "devices",
  [
    {
      $match: {
        created_at: {
          $gte: new Date(new Date().setHours(0, 0, 0, 0)),
          $lt: new Date(new Date().setHours(23, 59, 59, 999))
        }
      }
    },
    {
      $group: {
        _id: {
          production_line: "$production_line",
          sku: "$sku"
        },
        count: { $sum: 1 },
        approved: {
          $sum: {
            $cond: [{ $eq: ["$status", "approved"] }, 1, 0]
          }
        },
        rejected: {
          $sum: {
            $cond: [{ $eq: ["$status", "rejected"] }, 1, 0]
          }
        }
      }
    }
  ]
);

console.log("✅ Estructura MongoDB creada exitosamente");
console.log("📊 Colecciones principales:");
console.log("  1. devices - Registro maestro de dispositivos");
console.log("  2. production_orders - Órdenes de producción");
console.log("  3. device_events - Trazabilidad completa");
console.log("  4. service_tickets - Tickets post-venta");
console.log("  5. customers - Clientes");
console.log("  6. employees - Personal");
console.log("  7. quality_control - Control de calidad");
console.log("  8. rma_cases - Devoluciones y reemplazos");
console.log("  9. inventory - Inventario");
console.log("  10. metrics - KPIs y métricas");
