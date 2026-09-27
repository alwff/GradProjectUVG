from flaskr import create_app
from flaskr.services.rfid_supervisor import identify_specimen


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

    else:
        print("No se identifico un especimen registrado.")