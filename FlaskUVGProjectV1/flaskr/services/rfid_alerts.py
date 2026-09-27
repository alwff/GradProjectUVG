from datetime import datetime, timedelta


RFID_ALERT_COOLDOWN_SECONDS = 300


_last_alerts = {}


def can_send_alert(epc):

    now = datetime.now()

    last_alert = _last_alerts.get(epc)

    if last_alert is None:
        return True

    cooldown = timedelta(
        seconds=RFID_ALERT_COOLDOWN_SECONDS
    )

    if now - last_alert >= cooldown:
        return True

    return False


def register_alert(epc):

    _last_alerts[epc] = datetime.now()