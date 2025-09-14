import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def enviar_email(destinatario: str, mensaje: str):
    load_dotenv(dotenv_path="aplicacion/.env")
    
    remitente = os.getenv("SENDER_EMAIL")
    password = os.getenv("PASSWORD")
    asunto = "Recuperación de contraseña - LO DE MANOLI"

    if not remitente or not password:
        print("Error: No se pudieron cargar las credenciales del archivo .env")
        return False

    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(mensaje, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False