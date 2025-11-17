"""
Test script para verificar configuración SMTP
"""
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def test_smtp():
    # Configuración SMTP
    smtp_host = "smtp.dondominio.com"
    smtp_port = 587
    smtp_user = "trazabilidad@neowaybyose.com"
    smtp_password = "@S1i9m8o1n"

    # Crear mensaje de prueba
    message = MIMEMultipart()
    message["From"] = f"OSE Platform <{smtp_user}>"
    message["To"] = "ppelaez@oversunenergy.com"
    message["Subject"] = "Test Email - OSE Platform"

    body = """
    Este es un email de prueba del sistema OSE Platform.

    Si recibes este mensaje, la configuración SMTP está funcionando correctamente.

    Servidor: smtp.dondominio.com
    Puerto: 587
    Usuario: trazabilidad@neowaybyose.com
    """

    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        print("Conectando al servidor SMTP...")
        print(f"Host: {smtp_host}")
        print(f"Port: {smtp_port}")
        print(f"User: {smtp_user}")

        # Conectar y enviar (usando STARTTLS)
        async with aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, start_tls=True) as smtp:
            print("[OK] Conectado al servidor")
            print("[OK] TLS iniciado")

            await smtp.login(smtp_user, smtp_password)
            print("[OK] Autenticacion exitosa")

            await smtp.send_message(message)
            print("[OK] Email enviado correctamente!")
            print(f"     Destinatario: ppelaez@oversunenergy.com")

        return True

    except aiosmtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] Autenticacion fallida: {e}")
        print("        Verifica el usuario y contrasena")
        return False

    except aiosmtplib.SMTPConnectError as e:
        print(f"[ERROR] Error de conexion: {e}")
        print("        Verifica el host y puerto")
        return False

    except Exception as e:
        print(f"[ERROR] Error inesperado: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Test de configuración SMTP - OSE Platform")
    print("=" * 60)

    result = asyncio.run(test_smtp())

    print("=" * 60)
    if result:
        print("RESULTADO: [OK] Configuracion SMTP correcta")
    else:
        print("RESULTADO: [ERROR] Hay problemas con la configuracion SMTP")
    print("=" * 60)
