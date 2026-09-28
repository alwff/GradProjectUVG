import time

from datetime import (
    datetime,
    timezone
)

from flaskr import create_app

from flaskr.services.rfid_supervisor import (
    supervise_detection
)

from flaskr.services.rfid_alerts import (
    create_detection_event,
    send_unauthorized_alert
)


RFID_ABSENCE_THRESHOLD_SECONDS = 10

POLL_INTERVAL_SECONDS = 1


app = create_app()


present_tags = {}

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