# 🚀 DESPLEGAR AHORA - Instrucciones Ejecutivas

## ⏱️ Tiempo estimado: 15-20 minutos

---

## 📥 PASO 1: Descargar e Instalar WinSCP

1. Ir a: https://winscp.net/eng/download.php
2. Descargar e instalar la versión más reciente
3. Ejecutar WinSCP

⏱️ Tiempo: 3 minutos

---

## 🔌 PASO 2: Conectar al Servidor

En WinSCP, configurar nueva conexión:

```
Protocolo de archivo: SFTP
Nombre del servidor: 167.235.58.24
Número de puerto: 22
Nombre de usuario: admin
Contraseña: bb474edf
```

Hacer clic en **"Iniciar sesión"**

✅ **Verificación:** Deberías ver los directorios del servidor en el panel derecho.

⏱️ Tiempo: 1 minuto

---

## 📂 PASO 3: Crear Directorio en el Servidor

En WinSCP:

1. En el panel **derecho** (servidor), navegar a: `/var/www/`
2. Clic derecho → **New** → **Directory**
3. Nombre: `ose-platform`
4. Hacer doble clic para entrar en la carpeta

✅ **Verificación:** La ruta debe mostrar `/var/www/ose-platform`

⏱️ Tiempo: 30 segundos

---

## 📤 PASO 4: Subir Archivos al Servidor

En WinSCP:

### Panel Izquierdo (Tu PC):
Navegar a: `C:\Users\pedro\claude-code-workspace\OSE-Platform`

### Panel Derecho (Servidor):
Debe estar en: `/var/www/ose-platform`

### Arrastrar estos archivos/carpetas del panel izquierdo al derecho:

1. 📁 **Carpeta:** `backend-new/` (completa)
2. 📁 **Carpeta:** `frontend-react/` (completa)
3. 📄 **Archivo:** `docker-compose.yml`
4. 📄 **Archivo:** `.env.production`

**IMPORTANTE:**
- NO subir carpetas de backup (`backend-new-backup-*`, `frontend-backup-*`)
- NO subir `.git/`, `node_modules/`, `__pycache__/`
- Esperar a que termine completamente la transferencia

✅ **Verificación:** En el panel derecho deberías ver:
```
/var/www/ose-platform/
  ├── backend-new/
  ├── frontend-react/
  ├── docker-compose.yml
  └── .env.production
```

⏱️ Tiempo: 5-10 minutos (dependiendo de la velocidad de conexión)

---

## 🐳 PASO 5: Instalar Docker (Si no está instalado)

En WinSCP:

1. Presionar **Ctrl+T** para abrir terminal SSH
2. Copiar y pegar este comando completo:

```bash
docker --version 2>/dev/null || (curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker admin && sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose && echo "Docker instalado - Por favor cierra esta sesión y reconecta")
```

3. Presionar **Enter**
4. Si Docker se instaló, **cerrar WinSCP** y volver a conectar (Paso 2)

✅ **Verificación:** Ejecutar `docker --version` debe mostrar la versión instalada

⏱️ Tiempo: 2-3 minutos (solo la primera vez)

---

## 🚀 PASO 6: Desplegar la Aplicación

En la terminal SSH de WinSCP (Ctrl+T):

1. **Navegar al directorio:**
```bash
cd /var/www/ose-platform
```

2. **Iniciar los servicios:**
```bash
docker-compose up -d --build
```

3. **Esperar** a que termine el build (2-5 minutos)

✅ **Verificación:** Ver el progreso. Al terminar debe mostrar:
```
Creating ose_mongodb ... done
Creating ose_backend ... done
Creating ose_frontend ... done
```

⏱️ Tiempo: 3-5 minutos

---

## ✅ PASO 7: Verificar el Despliegue

### En la terminal SSH:

1. **Verificar estado de contenedores:**
```bash
docker-compose ps
```

Debe mostrar 3 contenedores con estado "Up":
```
NAME            STATUS
ose_mongodb     Up
ose_backend     Up
ose_frontend    Up
```

2. **Ver logs (opcional):**
```bash
docker-compose logs -f
```
(Presionar Ctrl+C para salir)

### En tu navegador:

1. **Frontend:** http://167.235.58.24:3001
   - ✅ Debe cargar la página de login de OSE Platform

2. **Backend Health:** http://167.235.58.24:8001/health
   - ✅ Debe mostrar: `{"status":"healthy"}`

3. **Backend API Docs:** http://167.235.58.24:8001/docs
   - ✅ Debe mostrar la documentación Swagger de la API

✅ **Verificación completa:** Si todo funciona, ¡el despliegue fue exitoso! 🎉

⏱️ Tiempo: 1 minuto

---

## 🎯 RESUMEN DE COMANDOS ÚTILES

### Ver estado de servicios
```bash
cd /var/www/ose-platform
docker-compose ps
```

### Ver logs en tiempo real
```bash
cd /var/www/ose-platform
docker-compose logs -f
```

### Reiniciar un servicio
```bash
cd /var/www/ose-platform
docker-compose restart backend
```

### Detener todo
```bash
cd /var/www/ose-platform
docker-compose down
```

### Iniciar todo
```bash
cd /var/www/ose-platform
docker-compose up -d
```

### Reconstruir y reiniciar
```bash
cd /var/www/ose-platform
docker-compose down
docker-compose up -d --build
```

---

## 🔧 TROUBLESHOOTING RÁPIDO

### Problema: Un contenedor no inicia

**Solución:**
```bash
cd /var/www/ose-platform
docker-compose logs [nombre_servicio]
docker-compose restart [nombre_servicio]
```

### Problema: Puerto ocupado

**Solución:**
```bash
cd /var/www/ose-platform
docker-compose down
docker-compose up -d
```

### Problema: Frontend muestra error 502/503

**Solución:**
```bash
cd /var/www/ose-platform
docker-compose restart backend
# Esperar 30 segundos y recargar la página
```

### Problema: Base de datos no conecta

**Solución:**
```bash
cd /var/www/ose-platform
docker-compose restart mongodb
docker-compose restart backend
```

---

## 📊 INFORMACIÓN DEL DESPLIEGUE

### URLs de Acceso
- **Frontend:** http://167.235.58.24:3001
- **Backend:** http://167.235.58.24:8001
- **API Docs:** http://167.235.58.24:8001/docs
- **Health Check:** http://167.235.58.24:8001/health

### Credenciales MongoDB
- **Usuario:** admin
- **Password:** oseplatform2025secure
- **Database:** ose_platform

### Servidor SSH
- **Host:** 167.235.58.24
- **Usuario:** admin
- **Password:** bb474edf

### Servicios y Puertos
- **MongoDB:** Puerto 27018 (interno)
- **Backend:** Puerto 8001 (FastAPI)
- **Frontend:** Puerto 3001 (Nginx + React)

---

## 📚 MÁS INFORMACIÓN

Si necesitas instrucciones más detalladas o configuración avanzada:

- **Guía Rápida:** [QUICK_START.md](QUICK_START.md)
- **Instrucciones Completas:** [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)
- **Checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Resumen Técnico:** [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
- **README General:** [README_DEPLOYMENT.md](README_DEPLOYMENT.md)

---

## ✅ CHECKLIST FINAL

- [ ] WinSCP instalado y funcionando
- [ ] Conectado al servidor (167.235.58.24)
- [ ] Directorio `/var/www/ose-platform` creado
- [ ] Archivos subidos correctamente
- [ ] Docker y Docker Compose instalados
- [ ] Servicios iniciados con `docker-compose up -d --build`
- [ ] 3 contenedores corriendo (mongodb, backend, frontend)
- [ ] Frontend accesible en http://167.235.58.24:3001
- [ ] Backend health check OK en http://167.235.58.24:8001/health
- [ ] Logs sin errores críticos

---

## 🎉 ¡LISTO!

Si completaste todos los pasos y todas las verificaciones son correctas, **¡tu aplicación OSE Platform está desplegada en producción!**

### Próximos pasos recomendados:

1. **Crear usuario administrador** (ver documentación del backend)
2. **Probar funcionalidades** principales
3. **Configurar dominio** platform.oversunenergy.com
4. **Implementar SSL/HTTPS** con Let's Encrypt
5. **Cambiar passwords** por defecto
6. **Configurar backups** automáticos

---

**Tiempo total estimado:** 15-20 minutos

**Estado:** ✅ Despliegue completado

**Fecha:** 2025-11-25

---

¿Necesitas ayuda? Consulta la documentación completa o contacta: admin@oversunenergy.com
