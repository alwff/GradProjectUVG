from flaskr import create_app
from flaskr import create_app
from flaskr.services.rfid_supervisor import (
    supervise_detection
)

app = create_app()


with app.app_context():

    print("Esperando deteccion RFID...")

    result = supervise_detection()

    print()
    print("Resultado del supervisor")
    print("Estado:", result["status"])
    print("Razon:", result["reason"])

    if result["epc"]:
        print(
            "EPC detectado:",
            result["epc"]
        )

    specimen = result["specimen"]
    movement = result["movement"]

    if specimen:

        print()
        print("Especimen")
        print("Portal:", specimen.portal_code)
        print("EPC:", specimen.rfid_epc)
        print("Estado:", specimen.status)

    if movement:

        print()
        print("Movimiento relacionado")
        print("ID:", movement.id)
        print("Tipo:", movement.movement_type)
        print("Origen:", movement.source)

        if movement.request_id:
            print(
                "Solicitud:",
                movement.request_record.tracking_code
            )

        if movement.notes:
            print(
                "Observaciones:",
                movement.notes
            )