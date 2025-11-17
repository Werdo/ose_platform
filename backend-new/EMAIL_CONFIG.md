# Configuración de Correo Electrónico - OSE Platform

## Cuentas de Correo Configuradas

### 1. Cuenta Principal (RMA y Notificaciones)
- **Email**: serviciorma@neowaybyose.com
- **Password**: @S1i9m8o1n
- **Uso**: Envío de notificaciones RMA, alertas de sistema, emails transaccionales

### 2. Cuenta Secundaria (Trazabilidad)
- **Email**: trazabilidad@neowaybyose.com
- **Password**: @S1i9m8o1n
- **Uso**: Notificaciones de trazabilidad, seguimiento de envíos

## Servidores SMTP Disponibles

### Opción 1: Servidores con Soporte SSL (RECOMENDADO) ✓
```
Servidor SMTP: smtp.dondominio.com
Puerto TLS: 587
Puerto SSL: 465
POP3: pop3.dondominio.com
IMAP: imap.dondominio.com
```

### Opción 2: Servidores de Marca Blanca
```
Servidor SMTP: smtp.panel247.com
POP3: pop3.panel247.com
IMAP: imap.panel247.com
```

### Opción 3: Servidores Sin SSL
```
Servidor SMTP: smtp.neowaybyose.com
POP3: pop3.neowaybyose.com
IMAP: imap.neowaybyose.com
```

## Configuración Actual

La plataforma está configurada para usar:
- **Servidor**: smtp.dondominio.com (Con SSL)
- **Puerto**: 587 (TLS)
- **Cuenta principal**: serviciorma@neowaybyose.com

## Ubicaciones de Configuración

### 1. Archivo de Configuración Principal
**Archivo**: `backend-new/app/config.py`
**Líneas**: 74-97

```python
SMTP_ENABLED: bool = True
SMTP_HOST: str = "smtp.dondominio.com"
SMTP_PORT: int = 587
SMTP_TLS: bool = True
SMTP_USER: str = "serviciorma@neowaybyose.com"
SMTP_PASSWORD: str = "@S1i9m8o1n"

EMAIL_FROM: str = "serviciorma@neowaybyose.com"
EMAIL_FROM_NAME: str = "OSE Platform - Servicio RMA"
EMAIL_TRACKING: str = "trazabilidad@neowaybyose.com"
```

### 2. Variables de Entorno (Opcional)
**Archivo**: `backend-new/.env`

Puedes sobrescribir la configuración creando un archivo .env:
```env
SMTP_HOST="smtp.dondominio.com"
SMTP_PORT=587
SMTP_USER="serviciorma@neowaybyose.com"
SMTP_PASSWORD="@S1i9m8o1n"
EMAIL_FROM="serviciorma@neowaybyose.com"
```

## Funcionalidades de Email en la Plataforma

### App 1 - Notificación de Series
- Envío de notificaciones de números de serie
- Alertas de stock

### App 3 - RMA & Tickets
- Notificaciones de nuevos RMA
- Actualizaciones de estado de tickets
- Confirmaciones de resolución

### App 6 - Picking & Etiquetado
- Notificaciones de envío de paquetes
- Confirmaciones de tracking
- Alertas de estado de entrega

## Pruebas de Configuración

Para verificar que el servicio de correo funciona correctamente:

```bash
# Desde el directorio backend-new
python -c "
from app.config import get_settings
settings = get_settings()
print(f'SMTP Host: {settings.SMTP_HOST}')
print(f'SMTP Port: {settings.SMTP_PORT}')
print(f'SMTP User: {settings.SMTP_USER}')
print(f'Email From: {settings.EMAIL_FROM}')
"
```

## Solución de Problemas

### Error: "Connection refused"
- Verificar que el firewall no bloquea el puerto 587
- Comprobar que las credenciales son correctas

### Error: "Authentication failed"
- Verificar usuario y contraseña
- Comprobar que la cuenta no está bloqueada

### Error: "TLS handshake failed"
- Verificar configuración SMTP_TLS=True
- Intentar con puerto 465 y SMTP_SSL=True

## Cambiar Configuración de Correo

Para cambiar a otro servidor o cuenta:

1. Editar `backend-new/app/config.py` líneas 78-83
2. O crear/editar `backend-new/.env` con las nuevas credenciales
3. Reiniciar el backend para aplicar cambios

## Seguridad

- Las contraseñas están en texto plano en config.py (solo desarrollo)
- En producción, usar variables de entorno o secretos encriptados
- Considerar usar ENCRYPTION_KEY para datos sensibles

## Soporte

Para problemas con el servicio de correo:
- Email: serviciorma@neowaybyose.com
- Verificar logs en: `/var/log/ose/app.log`
