from flaskr.services.rfid_alerts import (
    can_send_alert,
    register_alert
)


TEST_EPC = "AA0004EF55555555AA24E551"


print(
    "Primera comprobacion:",
    can_send_alert(TEST_EPC)
)

register_alert(TEST_EPC)

print(
    "Despues de registrar alerta:",
    can_send_alert(TEST_EPC)
)

print(
    "Otro EPC:",
    can_send_alert("OTRO_EPC")
)