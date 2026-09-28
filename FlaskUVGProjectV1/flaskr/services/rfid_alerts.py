from datetime import datetime, timedelta
from flaskr.extensions import db
from flaskr.models import (
    User,
    RFIDDetectionEvent
)
from flaskr.services.email_service import send_email

RFID_ALERT_COOLDOWN_SECONDS = 300

def create_detection_event(result):

    event = RFIDDetectionEvent(
        epc=result["epc"],
        specimen_id=(
            result["specimen"].id
            if result["specimen"]
            else None
        ),
        classification=result["status"],
        reason=result["reason"],
        alert_sent=False
    )

    db.session.add(event)
    db.session.commit()

    return event

def can_send_alert(epc):

    cooldown_limit = (
        datetime.now()
        - timedelta(
            seconds=RFID_ALERT_COOLDOWN_SECONDS
        )
    )

    recent_alert = (
        RFIDDetectionEvent.query
        .filter(
            RFIDDetectionEvent.epc == epc,
            RFIDDetectionEvent.alert_sent.is_(True),
            RFIDDetectionEvent.alert_sent_at
            >= cooldown_limit
        )
        .order_by(
            RFIDDetectionEvent.alert_sent_at.desc()
        )
        .first()
    )

    return recent_alert is None

def send_unauthorized_alert(
    result,
    event
):
    if result["status"] != "unauthorized":
        return False

    epc = result["epc"]
    specimen = result["specimen"]

    if specimen is None or not epc:
        return False

    if not can_send_alert(epc):
        return False

    users = (
        User.query
        .filter(User.email.isnot(None))
        .all()
    )

    recipients = [
        user.email
        for user in users
        if user.email
    ]

    if not recipients:
        return False

    subject = (
        "Alerta de movimiento no autorizado"
    )

    html = f"""
        <h2>
            Alerta de movimiento no autorizado
        </h2>

        <p>
            El espécimen
            <strong>{specimen.portal_code}</strong>
            fue detectado en el punto de control
            sin un movimiento autorizado registrado.
        </p>

        <p>
            <strong>Código de Portal:</strong>
            {specimen.portal_code}
            <br>

            <strong>EPC RFID:</strong>
            {epc}
            <br>

            <strong>Nombre científico:</strong>
            {specimen.scientific_name}
            <br>

            <strong>Colección:</strong>
            {specimen.collection}
        </p>

        <p>
            Se recomienda verificar la ubicación
            del espécimen y consultar su historial
            de movimientos.
        </p>

        <p>
            <em>
                Mensaje generado automáticamente
                por el Sistema de Colecciones.
            </em>
        </p>
    """

    send_email(
        recipients=recipients,
        subject=subject,
        html=html
    )

    event.alert_sent = True
    event.alert_sent_at = db.func.now()

    db.session.commit()

    return True