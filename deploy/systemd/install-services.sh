#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con sudo."
    echo
    echo "Uso:"
    echo "  sudo $0"
    exit 1
fi

SCRIPT_DIR="$(
    cd "$(dirname "$0")"
    pwd
)"

echo "Instalando servicios de UVG Collections..."
echo

if [ ! -f "$SCRIPT_DIR/uvgcollections.service" ]; then
    echo "Error: no se encontro uvgcollections.service"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/uvg-rfid.service" ]; then
    echo "Error: no se encontro uvg-rfid.service"
    exit 1
fi

if [ ! -f /etc/uvgcollections.env ]; then
    echo "Error: no existe /etc/uvgcollections.env"
    echo
    echo "Crea primero el archivo usando:"
    echo "  deploy/env/uvgcollections.env.example"
    exit 1
fi

echo "Copiando servicios..."

cp \
    "$SCRIPT_DIR/uvgcollections.service" \
    /etc/systemd/system/uvgcollections.service

cp \
    "$SCRIPT_DIR/uvg-rfid.service" \
    /etc/systemd/system/uvg-rfid.service

echo "Recargando systemd..."

systemctl daemon-reload

echo "Habilitando servicios..."

systemctl enable uvgcollections.service
systemctl enable uvg-rfid.service

echo
echo "Instalacion completada."
echo
echo "Los servicios quedaron habilitados para iniciar"
echo "automaticamente con el sistema."
echo
echo "Para iniciarlos:"
echo "  sudo systemctl start uvgcollections"
echo "  sudo systemctl start uvg-rfid"