from flaskr.services.email_service import (
    send_email
)


recipient = input(
    "Correo destinatario: "
).strip()


print("Enviando correo de prueba...")


response = send_email(
    recipients=[recipient],
    subject="Prueba del sistema de alertas RFID",
    html="""
        <h2>Sistema de Colecciones</h2>

        <p>
            La comunicación con el servicio
            de correo funciona correctamente.
        </p>

        <p>
            Este mensaje fue enviado desde
            el servidor Ubuntu mediante Resend.
        </p>
    """
)


print("Correo enviado.")
print("Respuesta:", response)