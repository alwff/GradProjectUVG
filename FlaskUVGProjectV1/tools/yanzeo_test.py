from flaskr.services.rfid_reader import read_epc


print("Probando lector Yanzeo SR692...")

epc = read_epc()

if epc:
    print("Tag detectado")
    print("EPC:", epc)
else:
    print("No se detecto ningun tag.")