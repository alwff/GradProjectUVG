import time
import uuid
from datetime import (
    datetime,
    timezone
)
from flaskr import create_app
from flaskr.services.rfid_supervisor import (
    supervise_epc
)
from flaskr.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from flaskr.services.rfid_alerts import (
    create_detection_event,
    get_detection_event,
    send_unauthorized_alert
)
from flaskr.services.rfid_reader import (
    read_epc
)

RFID_ABSENCE_THRESHOLD_SECONDS = 10

POLL_INTERVAL_SECONDS = 1

app = create_app()
present_tags = {}
pending_detections = {}

def reset_database_session():

    try:
        db.session.rollback()

    except Exception as error:
        print(
            "[ERROR ROLLBACK]",
            error
        )

    try:
        db.session.remove()

    except Exception as error:
        print(
            "[ERROR CLEANUP]",
            error
        )

def register_presence(epc):

    present_tags[epc] = {
        "last_seen": datetime.now(
            timezone.utc
        )
    }


def update_presence(epc):

    present_tags[epc]["last_seen"] = (
        datetime.now(
            timezone.utc
        )
    )

def process_new_presence(epc):

    if epc not in pending_detections:
        pending_detections[epc] = str(
            uuid.uuid4()
        )

    detection_key = pending_detections[epc]

    event = get_detection_event(
        detection_key
    )

    if event is not None:

        print(
            "[DATABASE] Evento existente recuperado:",
            event.id
        )

        print(
            "[DATABASE] No se genera otro evento ni otra alerta."
        )

        return

    result = supervise_epc(
        epc
    )

    event, created = create_detection_event(
        result,
        detection_key
    )

    if not created:
        print(
            "[DATABASE] Evento recuperado. No se reenvía alerta."
        )
        return

    print()
    print(
        f"[DETECCION] {epc}"
    )

    print(
        f"Evento RFID: {event.id}"
    )

    print(
        f"Estado: {result['status']}"
    )

    if result["specimen"]:

        print(
            "Especimen:",
            result["specimen"].portal_code
        )

    try:
        alert_sent = send_unauthorized_alert(
            result,
            event
        )

        if alert_sent:
            print(
                "[ALERTA] Correo enviado."
            )

    except Exception as error:
        print(
            "[ERROR ALERTA]",
            error
        )

        reset_database_session()

def remove_absent_tags():

    now = datetime.now(
        timezone.utc
    )

    expired_epcs = []

    for epc, data in present_tags.items():

        absence_seconds = (
            now - data["last_seen"]
        ).total_seconds()

        if (
            absence_seconds
            >= RFID_ABSENCE_THRESHOLD_SECONDS
        ):
            expired_epcs.append(
                epc
            )

    for epc in expired_epcs:

        del present_tags[epc]

        print(
            f"[AUSENTE] {epc}"
        )

def run_worker():

    print(
        "Worker RFID iniciado."
    )

    print(
        "Lector:",
        "10.77.0.2:49152"
    )

    print(
        "Ausencia para nueva presencia:",
        f"{RFID_ABSENCE_THRESHOLD_SECONDS} segundos"
    )

    print(
        "Presiona Ctrl+C para detener."
    )

    while True:

        try:

            epc = read_epc()

            if epc:

                if epc in present_tags:

                    update_presence(
                        epc
                    )

                else:

                    process_new_presence(
                        epc
                    )

                    register_presence(
                        epc
                    )

                    pending_detections.pop(
                        epc,
                        None
                    )

            remove_absent_tags()

        except OSError as error:

            print(
                "[ERROR RFID]",
                error
            )

            print(
                "Reintentando..."
            )
        
        except SQLAlchemyError as error:

            print(
                "[ERROR DATABASE]",
                error
            )

            reset_database_session()

            print(
                "[DATABASE] Recuperación de sesión intentada."
            )


        except Exception as error:

            print(
                "[ERROR WORKER]",
                error
            )

            reset_database_session()

        time.sleep(
            POLL_INTERVAL_SECONDS
        )

if __name__ == "__main__":

    try:

        with app.app_context():

            run_worker()

    except KeyboardInterrupt:

        print()
        print(
            "Worker RFID detenido."
        )