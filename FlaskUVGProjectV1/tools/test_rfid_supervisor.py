from flaskr import create_app
from flaskr.services.rfid_supervisor import (
    identify_specimen,
    get_latest_movement,
    classify_detection
)

app = create_app()


with app.app_context():

    print("Esperando lectura RFID...")

    specimen, result = identify_specimen()

    print("Resultado:", result)

    if specimen:

        print("Especimen identificado")
        print("Portal:", specimen.portal_code)
        print("EPC:", specimen.rfid_epc)
        print("Estado:", specimen.status)

        movement = get_latest_movement(
            specimen
        )

        if movement:

            print()
            print("Ultimo movimiento registrado")
            print("ID:", movement.id)
            print(
                "Tipo:",
                movement.movement_type
            )
            print(
                "Origen:",
                movement.source
            )
            print(
                "Realizado por:",
                movement.performed_by
            )
            print(
                "Fecha:",
                movement.created_at
            )

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

        else:

            print()
            print(
                "El especimen no tiene "
                "movimientos registrados."
            )

        classification = classify_detection(
            specimen
        )

        print()
        print("Clasificacion RFID")
        print(
            "Estado:",
            classification["status"]
        )
        print(
            "Razon:",
            classification["reason"]
        )

    else:

        print(
            "No se identifico un especimen registrado."
        )