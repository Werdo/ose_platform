#!/usr/bin/env python3
"""
OSE Platform - Automated Deployment Script
Conecta al servidor vía SSH y ejecuta el despliegue
"""

import sys
import time

try:
    import paramiko
except ImportError:
    print("ERROR: paramiko no está instalado")
    print("Instala con: pip install paramiko")
    sys.exit(1)

# Configuración del servidor
SERVER = "167.235.58.24"
USERNAME = "admin"
PASSWORD = "bb474edf"
PORT = 22

def execute_command(ssh, command, description=""):
    """Ejecuta un comando en el servidor SSH"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}")

    print(f"$ {command}")

    stdin, stdout, stderr = ssh.exec_command(command)

    # Leer output
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_code = stdout.channel.recv_exit_status()

    if output:
        print(output)
    if error:
        print(f"STDERR: {error}")

    return exit_code, output, error


def main():
    print("="*60)
    print("OSE PLATFORM - AUTOMATED DEPLOYMENT")
    print("="*60)
    print(f"Servidor: {SERVER}")
    print(f"Usuario: {USERNAME}")
    print("="*60)

    # Crear cliente SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectar al servidor
        print("\n[1/10] Conectando al servidor...")
        ssh.connect(
            SERVER,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            timeout=30
        )
        print("[OK] Conexion establecida")

        # 1. Ir al directorio
        execute_command(ssh, "cd ~/ose-platform && pwd", "[2/10] Verificando directorio")

        # 2. Verificar Docker
        execute_command(ssh, "which docker", "[3/10] Verificando Docker")
        code, output, _ = execute_command(ssh, "docker --version", "")

        if code != 0:
            print("\n[WARN] ADVERTENCIA: Docker no parece estar instalado")
            print("Instalando Docker...")
            execute_command(ssh, """
                sudo apt-get update &&
                sudo apt-get install -y docker.io docker-compose-plugin &&
                sudo usermod -aG docker admin
            """, "[4/10] Instalando Docker")
        else:
            print("\n[OK] Docker está instalado")

        # 3. Verificar Docker Compose
        code, output, _ = execute_command(ssh, "docker compose version", "[5/10] Verificando Docker Compose")

        if code != 0:
            print("\n[WARN] Docker Compose no disponible, instalando...")
            execute_command(ssh, "sudo apt-get install -y docker-compose-plugin", "")
        else:
            print("\n[OK] Docker Compose está instalado")

        # 4. Verificar archivos
        execute_command(ssh, "cd ~/ose-platform && ls -la docker-compose.yml .env.production",
                       "[6/10] Verificando archivos de configuración")

        # 5. Detener contenedores existentes
        execute_command(ssh, "cd ~/ose-platform && docker compose down 2>&1",
                       "[7/10] Deteniendo contenedores existentes")

        # 6. Construir imágenes
        print("\n[8/10] Construyendo imágenes Docker (esto puede tardar varios minutos)...")
        execute_command(ssh, "cd ~/ose-platform && docker compose build --no-cache", "")

        # 7. Levantar contenedores
        execute_command(ssh, "cd ~/ose-platform && docker compose up -d",
                       "[9/10] Levantando contenedores")

        # 8. Verificar estado
        time.sleep(5)  # Esperar a que los contenedores inicien
        execute_command(ssh, "cd ~/ose-platform && docker compose ps",
                       "[10/10] Verificando estado de los contenedores")

        # 9. Mostrar logs
        print("\n" + "="*60)
        print("LOGS DE LOS CONTENEDORES (últimas 50 líneas)")
        print("="*60)
        execute_command(ssh, "cd ~/ose-platform && docker compose logs --tail=50", "")

        # 10. Verificar endpoints
        print("\n" + "="*60)
        print("VERIFICANDO ENDPOINTS")
        print("="*60)
        execute_command(ssh, "curl -s http://localhost:8001/health | head -20", "Backend Health Check")
        execute_command(ssh, "curl -s -I http://localhost:3001/ | head -10", "Frontend Status")

        print("\n" + "="*60)
        print("[OK] DESPLIEGUE COMPLETADO")
        print("="*60)
        print(f"\nEndpoints accesibles en:")
        print(f"  - Backend:  http://{SERVER}:8001/health")
        print(f"  - Frontend: http://{SERVER}:3001/")
        print(f"  - API Docs: http://{SERVER}:8001/docs")
        print("\nPróximos pasos:")
        print("  1. Configurar Nginx como reverse proxy")
        print("  2. Configurar DNS para platform.oversunenergy.com")
        print("  3. Obtener certificado SSL con Let's Encrypt")

    except paramiko.AuthenticationException:
        print("\n[ERROR] ERROR: Autenticación fallida. Verifica usuario/contraseña.")
        return 1
    except paramiko.SSHException as e:
        print(f"\n[ERROR] ERROR SSH: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        return 1
    finally:
        ssh.close()
        print("\nConexión cerrada.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
