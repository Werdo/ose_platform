# 🔐 Guía de Configuración de Credenciales - OSE Platform

## 📋 Índice
1. [Configuración Rápida](#configuración-rápida)
2. [MongoDB - Usuarios y Contraseñas](#mongodb---usuarios-y-contraseñas)
3. [JWT - Claves de Seguridad](#jwt---claves-de-seguridad)
4. [Email - Configuración SMTP](#email---configuración-smtp)
5. [Generación de Claves Seguras](#generación-de-claves-seguras)
6. [Ejemplos de Configuración](#ejemplos-de-configuración)

---

## 🚀 Configuración Rápida

### Paso 1: Copiar el archivo de ejemplo
```bash
cp .env.example .env
```

### Paso 2: Editar el archivo .env
```bash
# Windows
notepad .env

# Linux/Mac
nano .env
```

### Paso 3: Rellenar TODAS las variables marcadas como "RELLENAR_AQUI"

---

## 🗄️ MongoDB - Usuarios y Contraseñas

### Variables a configurar:

#### `MONGODB_ROOT_USER`
- **Qué es:** Usuario administrador de MongoDB
- **Recomendación:** `admin_oversun` o `mongodb_admin`
- **Permisos:** Control total de la base de datos

#### `MONGODB_ROOT_PASSWORD`
- **Qué es:** Contraseña del usuario root
- **Requisitos:** Mínimo 12 caracteres, mayúsculas, minúsculas, números y símbolos
- **Ejemplo:** `P@ssw0rd_Secure_2025!`
- **Generar segura:**
  ```bash
  openssl rand -base64 16
  ```

#### `MONGODB_APP_USER`
- **Qué es:** Usuario de la aplicación (FastAPI lo usa para todo)
- **Recomendación:** `oversun_api` o `ose_app`
- **Permisos:** Lectura y escritura en `oversun_production`

#### `MONGODB_APP_PASSWORD`
- **Qué es:** Contraseña del usuario de aplicación
- **Requisitos:** Mínimo 12 caracteres
- **Ejemplo:** `ApiUser_2025_Secure!`

#### `MONGODB_READONLY_USER`
- **Qué es:** Usuario de solo lectura (para dashboards, reportes)
- **Recomendación:** `oversun_readonly`
- **Permisos:** Solo lectura en `oversun_production`

#### `MONGODB_READONLY_PASSWORD`
- **Qué es:** Contraseña del usuario de solo lectura
- **Ejemplo:** `ReadOnly_2025!`

### ⚠️ IMPORTANTE:
- NUNCA uses contraseñas predecibles como "admin", "12345", etc.
- NUNCA uses la misma contraseña para diferentes usuarios
- Guarda las contraseñas en un gestor seguro (1Password, LastPass, etc.)

---

## 🔑 JWT - Claves de Seguridad

### Variables a configurar:

#### `JWT_SECRET_KEY`
- **Qué es:** Clave secreta para firmar los tokens de autenticación
- **Requisitos:** Cadena aleatoria de al menos 32 caracteres
- **Generar (recomendado):**
  ```bash
  # Linux/Mac/Git Bash
  openssl rand -hex 32

  # PowerShell (Windows)
  -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})

  # Python
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Ejemplo de salida:**
  ```
  7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
  ```

#### `ENCRYPTION_SECRET_KEY`
- **Qué es:** Clave adicional para encriptación de datos sensibles
- **Generar:** Igual que JWT_SECRET_KEY (debe ser DIFERENTE)

### ⚠️ SEGURIDAD CRÍTICA:
- **NUNCA** compartas estas claves por email o chat
- **NUNCA** las subas a Git (el .env ya está en .gitignore)
- Si se comprometen, debes regenerarlas INMEDIATAMENTE
- En producción, considera usar un servicio de gestión de secretos (AWS Secrets Manager, HashiCorp Vault)

---

## 📧 Email - Configuración SMTP

### Opciones de Servidor de Correo:

#### Opción 1: Gmail (Más común)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=True
SMTP_SSL=False
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Pasos para obtener la contraseña de Gmail:**

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Seguridad → Verificación en dos pasos (activar si no está activo)
3. Contraseñas de aplicaciones → Generar
4. Selecciona "Correo" y "Otro dispositivo personalizado"
5. Copia la contraseña de 16 caracteres (sin espacios)

**Documentación oficial:** https://support.google.com/accounts/answer/185833

---

#### Opción 2: Outlook / Office 365

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_TLS=True
SMTP_SSL=False
SMTP_USER=tu_correo@outlook.com
SMTP_PASSWORD=tu_contraseña_normal
```

---

#### Opción 3: Servidor SMTP Propio / Corporativo

```env
SMTP_HOST=mail.tuempresa.com
SMTP_PORT=587  # o 465 si usa SSL
SMTP_TLS=True  # o False si usa SSL
SMTP_SSL=False # o True si el puerto es 465
SMTP_USER=notificaciones@tuempresa.com
SMTP_PASSWORD=contraseña_del_correo
```

**Consulta con tu administrador de sistemas:**
- Host del servidor SMTP
- Puerto (587 para TLS, 465 para SSL)
- Credenciales de autenticación

---

#### Opción 4: SendGrid (Servicio profesional - recomendado para producción)

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_TLS=True
SMTP_SSL=False
SMTP_USER=apikey
SMTP_PASSWORD=TU_API_KEY_DE_SENDGRID
```

**Pasos:**
1. Crea cuenta en https://sendgrid.com/
2. API Keys → Create API Key
3. Copia la API key generada

---

### Variables adicionales de Email:

#### `EMAIL_FROM`
- **Qué es:** Remitente que verán los destinatarios
- **Formato:** `"Nombre Visible <email@dominio.com>"`
- **Ejemplos:**
  ```
  "OSE Platform <notificaciones@oversun.com>"
  "Oversun Energy <noreply@oversun.com>"
  "Sistema de Trazabilidad <sistema@oversun.com>"
  ```

#### `EMAIL_REPLY_TO`
- **Qué es:** Email al que responderán los usuarios
- **Ejemplo:** `soporte@oversun.com`

#### `EMAIL_ADMIN_COPY`
- **Qué es:** Emails que reciben copia de todas las notificaciones
- **Formato:** Separados por comas
- **Ejemplo:** `admin@oversun.com,logistica@oversun.com,calidad@oversun.com`

---

## 🔐 Generación de Claves Seguras

### Método 1: OpenSSL (Linux/Mac/Git Bash)
```bash
# Clave hexadecimal (recomendado para JWT)
openssl rand -hex 32

# Clave base64
openssl rand -base64 32
```

### Método 2: Python
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Método 3: PowerShell (Windows)
```powershell
# Generar cadena aleatoria de 64 caracteres
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
```

### Método 4: Online (SOLO para desarrollo, NUNCA para producción)
- https://www.random.org/strings/
- https://passwordsgenerator.net/

---

## 📝 Ejemplos de Configuración

### Ejemplo 1: Desarrollo Local
```env
MONGODB_ROOT_USER=admin_dev
MONGODB_ROOT_PASSWORD=DevP@ss2025!
MONGODB_APP_USER=ose_dev
MONGODB_APP_PASSWORD=AppDev2025!

JWT_SECRET_KEY=7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=True
SMTP_USER=desarrollo@oversun.com
SMTP_PASSWORD=abcd efgh ijkl mnop

EMAIL_FROM="OSE Dev <desarrollo@oversun.com>"
```

### Ejemplo 2: Producción
```env
MONGODB_ROOT_USER=admin_oversun_prod
MONGODB_ROOT_PASSWORD=Pr0d_S3cur3_P@ssw0rd_2025!XyZ
MONGODB_APP_USER=oversun_api_prod
MONGODB_APP_PASSWORD=Api_Pr0d_2025!_S3cur3_K3y

JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxx

EMAIL_FROM="Oversun Energy Platform <notificaciones@oversun.com>"
EMAIL_ADMIN_COPY=admin@oversun.com,it@oversun.com
```

---

## ✅ Checklist de Configuración

Antes de iniciar el sistema, verifica que has configurado:

### MongoDB
- [ ] `MONGODB_ROOT_USER` - Usuario administrador
- [ ] `MONGODB_ROOT_PASSWORD` - Contraseña root (mínimo 12 caracteres)
- [ ] `MONGODB_APP_USER` - Usuario de aplicación
- [ ] `MONGODB_APP_PASSWORD` - Contraseña de app
- [ ] `MONGODB_READONLY_USER` - Usuario de solo lectura
- [ ] `MONGODB_READONLY_PASSWORD` - Contraseña readonly

### Seguridad
- [ ] `JWT_SECRET_KEY` - Clave JWT (generada con openssl)
- [ ] `ENCRYPTION_SECRET_KEY` - Clave de encriptación (diferente a JWT)

### Email
- [ ] `SMTP_HOST` - Servidor SMTP
- [ ] `SMTP_PORT` - Puerto (587 o 465)
- [ ] `SMTP_USER` - Usuario de correo
- [ ] `SMTP_PASSWORD` - Contraseña o API key
- [ ] `EMAIL_FROM` - Remitente visible
- [ ] `EMAIL_REPLY_TO` - Email de respuesta

### CORS
- [ ] `CORS_ORIGINS` - Dominios de tus frontends

---

## 🆘 Problemas Comunes

### Error: "Authentication failed" en MongoDB
**Causa:** Usuario o contraseña incorrectos
**Solución:** Verifica que no haya espacios al inicio/final de las credenciales

### Error: "SMTPAuthenticationError"
**Causa:** Credenciales de email incorrectas
**Solución Gmail:** Usa "App Password", no tu contraseña normal

### Error: "Invalid JWT"
**Causa:** La JWT_SECRET_KEY cambió o es inválida
**Solución:** Regenera la clave y reinicia el servicio

### Docker no inicia MongoDB
**Causa:** Puerto 27017 ya en uso
**Solución:** Para el MongoDB local si lo tienes corriendo

---

## 📞 Soporte

Si necesitas ayuda con la configuración:
1. Revisa esta guía completa
2. Consulta los logs: `docker-compose logs`
3. Verifica el archivo `.env` no tenga errores de sintaxis

---

## 🔒 Seguridad - Mejores Prácticas

1. ✅ Usa contraseñas diferentes para cada servicio
2. ✅ Genera claves aleatorias con herramientas criptográficas
3. ✅ Nunca compartas credenciales por email o chat no cifrado
4. ✅ Rota las contraseñas cada 90 días en producción
5. ✅ Usa gestores de contraseñas (1Password, Bitwarden, etc.)
6. ✅ Habilita 2FA en servicios que lo permitan
7. ✅ El archivo `.env` ya está en `.gitignore` - NUNCA lo subas a Git
8. ❌ Nunca uses contraseñas como "admin", "password", "123456"
9. ❌ Nunca reutilices contraseñas de otros sistemas
10. ❌ Nunca compartas el `JWT_SECRET_KEY`

---

**Última actualización:** 11 de Noviembre, 2025
