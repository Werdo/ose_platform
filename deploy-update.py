#!/usr/bin/env python3
"""
OSE Platform - Update and Deploy Script
Hace pull del repositorio y ejecuta el deploy
"""

import sys
import paramiko

SERVER = "167.235.58.24"
USERNAME = "admin"
PASSWORD = "bb474edf"
PORT = 22

def execute_command(ssh, command):
    """Ejecuta un comando"""
    print(f"$ {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if output:
        print(output)
    if error and 'warning' not in error.lower():
        print(f"ERROR: {error}")
    return stdout.channel.recv_exit_status()

def main():
    print("="*60)
    print("OSE PLATFORM - UPDATE AND DEPLOY")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1/4] Conectando al servidor...")
        ssh.connect(SERVER, port=PORT, username=USERNAME, password=PASSWORD, timeout=30)
        print("[OK] Conectado")

        print("\n[2/4] Actualizando codigo...")
        execute_command(ssh, "cd ~/ose-platform && git pull origin main")

        print("\n[3/4] Construyendo contenedores Docker...")
        execute_command(ssh, "cd ~/ose-platform && docker compose build --no-cache")

        print("\n[4/4] Levantando servicios...")
        execute_command(ssh, "cd ~/ose-platform && docker compose up -d")

        print("\n" + "="*60)
        print("Verificando servicios...")
        print("="*60)
        execute_command(ssh, "cd ~/ose-platform && docker compose ps")

        print("\n" + "="*60)
        print("[OK] DESPLIEGUE COMPLETADO")
        print("="*60)
        print(f"\nServicios disponibles en:")
        print(f"  - Backend:  http://{SERVER}:8001/health")
        print(f"  - Frontend: http://{SERVER}:3001/")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1
    finally:
        ssh.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
