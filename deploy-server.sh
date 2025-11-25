#!/bin/bash
# OSE Platform - Server Deployment Script
# Para ejecutar en el servidor Linux

set -e  # Exit on error

echo "============================================================"
echo "OSE PLATFORM - DEPLOYMENT SCRIPT"
echo "============================================================"

cd ~/ose-platform

echo ""
echo "[1/5] Actualizando código desde Git..."
git pull origin main

echo ""
echo "[2/5] Construyendo imágenes Docker..."
docker compose build --no-cache

echo ""
echo "[3/5] Levantando servicios..."
docker compose up -d

echo ""
echo "[4/5] Esperando a que los servicios inicien..."
sleep 10

echo ""
echo "[5/5] Verificando estado de los servicios..."
docker compose ps

echo ""
echo "============================================================"
echo "Logs de los contenedores:"
echo "============================================================"
docker compose logs --tail=50

echo ""
echo "============================================================"
echo "DEPLOYMENT COMPLETADO"
echo "============================================================"
echo ""
echo "Servicios disponibles:"
echo "  - Backend:  http://localhost:8001/health"
echo "  - Frontend: http://localhost:3001/"
echo ""
echo "Para ver logs en tiempo real:"
echo "  docker compose logs -f"
echo ""
