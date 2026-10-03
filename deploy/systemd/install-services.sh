#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con sudo."
    echo
    echo "Uso:"
    echo "  sudo $0"
    exit 1
fi

if [ -z "$SUDO_USER" ]; then
    echo "Error: no fue posible identificar al usuario."
    echo "Ejecuta el script utilizando sudo."
    exit 1
fi

INSTALL_USER="$SUDO_USER"

INSTALL_GROUP="$(
    id -gn "$INSTALL_USER"
)"

SCRIPT_DIR="$(
    cd "$(dirname "$0")"
    pwd
)"

REPO_ROOT="$(
    cd "$SCRIPT_DIR/../.."
    pwd
)"

APP_DIR="$REPO_ROOT/FlaskUVGProjectV1"
VENV_DIR="$APP_DIR/venv"

UVGCOLLECTIONS_TEMPLATE="$SCRIPT_DIR/uvgcollections.service"
RFID_TEMPLATE="$SCRIPT_DIR/uvg-rfid.service"

UVGCOLLECTIONS_TARGET="/etc/systemd/system/uvgcollections.service"
RFID_TARGET="/etc/systemd/system/uvg-rfid.service"

echo "Instalando servicios de UVG Collections..."
echo
echo "Usuario:     $INSTALL_USER"
echo "Grupo:       $INSTALL_GROUP"
echo "Repositorio: $REPO_ROOT"
echo "Aplicacion:  $APP_DIR"
echo "Entorno:     $VENV_DIR"
echo

if [ ! -d "$APP_DIR" ]; then
    echo "Error: no existe:"
    echo "  $APP_DIR"
    exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Error: no existe un entorno virtual valido en:"
    echo "  $VENV_DIR"
    echo
    echo "Crea primero el entorno virtual e instala las dependencias."
    exit 1
fi

if [ ! -x "$VENV_DIR/bin/gunicorn" ]; then
    echo "Error: Gunicorn no esta instalado en el entorno virtual."
    exit 1
fi

if [ ! -f /etc/uvgcollections.env ]; then
    echo "Error: no existe /etc/uvgcollections.env"
    echo
    echo "Utiliza como referencia:"
    echo "  deploy/env/uvgcollections.env.example"
    exit 1
fi

if [ ! -f "$UVGCOLLECTIONS_TEMPLATE" ]; then
    echo "Error: no se encontro:"
    echo "  $UVGCOLLECTIONS_TEMPLATE"
    exit 1
fi

if [ ! -f "$RFID_TEMPLATE" ]; then
    echo "Error: no se encontro:"
    echo "  $RFID_TEMPLATE"
    exit 1
fi

echo "Generando uvgcollections.service..."

sed \
    -e "s|^User=.*|User=$INSTALL_USER|" \
    -e "s|^Group=.*|Group=$INSTALL_GROUP|" \
    -e "s|^WorkingDirectory=.*|WorkingDirectory=$APP_DIR|" \
    -e "s|^Environment=\"PATH=.*\"|Environment=\"PATH=$VENV_DIR/bin\"|" \
    -e "s|^ExecStart=.*/venv/bin/gunicorn|ExecStart=$VENV_DIR/bin/gunicorn|" \
    "$UVGCOLLECTIONS_TEMPLATE" \
    > "$UVGCOLLECTIONS_TARGET"

echo "Generando uvg-rfid.service..."

sed \
    -e "s|^User=.*|User=$INSTALL_USER|" \
    -e "s|^Group=.*|Group=$INSTALL_GROUP|" \
    -e "s|^WorkingDirectory=.*|WorkingDirectory=$APP_DIR|" \
    -e "s|^Environment=\"PATH=.*\"|Environment=\"PATH=$VENV_DIR/bin\"|" \
    -e "s|^ExecStart=.*/venv/bin/python|ExecStart=$VENV_DIR/bin/python|" \
    "$RFID_TEMPLATE" \
    > "$RFID_TARGET"

echo "Recargando systemd..."

systemctl daemon-reload

echo "Habilitando servicios..."

systemctl enable uvgcollections.service
systemctl enable uvg-rfid.service

echo
echo "Instalacion completada."
echo
echo "Los servicios fueron adaptados automaticamente a:"
echo "  Usuario: $INSTALL_USER"
echo "  Ruta:    $REPO_ROOT"
echo
echo "Para iniciarlos:"
echo "  sudo systemctl start uvgcollections"
echo "  sudo systemctl start uvg-rfid"