import socket


READER_IP = "192.168.1.116"
READER_PORT = 49152
READER_TIMEOUT = 3


def connect_reader():
    reader = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    reader.settimeout(READER_TIMEOUT)

    reader.connect(
        (READER_IP, READER_PORT)
    )

    return reader

def read_epc():

    reader = connect_reader()

    command = bytes([
        0x7C,
        0xFF,
        0xFF,
        0x20,
        0x00,
        0x00,
        0x66
    ])

    try:

        reader.sendall(command)

        try:
            response = reader.recv(4096)

        except socket.timeout:
            print(
                "DEBUG RFID: timeout sin respuesta"
            )
            return None

        print(
            "DEBUG RFID:",
            len(response),
            response.hex(" ").upper()
        )

        if len(response) < 22:
            return None

        if response[4] != 0x02:
            return None

        pc = response[7:9]

        epc_length = (
            ((pc[0] >> 3) & 0x1F) * 2
        )

        epc_start = 9
        epc_end = (
            epc_start + epc_length
        )

        epc = response[
            epc_start:epc_end
        ]

        return epc.hex().upper()

    finally:
        reader.close()