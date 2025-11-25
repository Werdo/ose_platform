#!/bin/bash

# ════════════════════════════════════════════════════════════════════════════
# OSE PLATFORM - Deployment Script
# ════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   OSE PLATFORM - Production Deployment${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Server configuration
SERVER_USER="admin"
SERVER_HOST="167.235.58.24"
SERVER_PATH="/var/www/ose-platform"

echo -e "${YELLOW}[1/5] Creating deployment directory on server...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "mkdir -p ${SERVER_PATH}"

echo -e "${YELLOW}[2/5] Copying project files to server...${NC}"
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude 'dist' \
  --exclude 'build' \
  --exclude '*.pyc' \
  --exclude '.env' \
  --exclude 'logs' \
  --exclude 'tmp' \
  --exclude 'backend-new-backup-*' \
  --exclude 'frontend-backup-*' \
  --exclude 'backend' \
  --exclude 'frontend' \
  --exclude 'frontend-invoice-portal' \
  --exclude 'frontend-picking-portal' \
  --exclude 'frontend-public-portal' \
  --exclude '.claude' \
  ./ ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/

echo -e "${YELLOW}[3/5] Setting permissions...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "chmod +x ${SERVER_PATH}/deploy.sh"

echo -e "${YELLOW}[4/5] Stopping existing containers (if any)...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${SERVER_PATH} && docker-compose down || true"

echo -e "${YELLOW}[5/5] Starting containers with Docker Compose...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${SERVER_PATH} && docker-compose up -d --build"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Deployment completed successfully!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Services:${NC}"
echo -e "  Frontend: ${GREEN}http://167.235.58.24:3001${NC}"
echo -e "  Backend:  ${GREEN}http://167.235.58.24:8001${NC}"
echo -e "  MongoDB:  ${GREEN}localhost:27018${NC} (internal)"
echo ""
echo -e "${YELLOW}Check status:${NC}"
echo -e "  ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${SERVER_PATH} && docker-compose ps'"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo -e "  ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${SERVER_PATH} && docker-compose logs -f'"
echo ""
