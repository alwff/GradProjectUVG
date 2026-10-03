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
    exit 1
fi

INSTALL_USER="$SUDO_USER"

USER_HOME="$(
    getent passwd "$INSTALL_USER" \
    | cut -d: -f6
)"

SCRIPT_DIR="$(
    cd "$(dirname "$0")"
    pwd
)"

NGROK_BIN="/usr/local/bin/ngrok"

NGROK_CONFIG_DIR="$USER_HOME/.config/ngrok"
NGROK_CONFIG="$NGROK_CONFIG_DIR/ngrok.yml"

SERVICE_TEMPLATE="$SCRIPT_DIR/ngrok.service"
SERVICE_TARGET="/etc/systemd/system/ngrok.service"

echo "Instalando configuracion de ngrok..."
echo
echo "Usuario:       $INSTALL_USER"
echo "Home:          $USER_HOME"
echo "Configuracion: $NGROK_CONFIG"
echo

if [ ! -x "$NGROK_BIN" ]; then
    echo "Error: ngrok no esta instalado en:"
    echo "  $NGROK_BIN"
    echo
    echo "Instala ngrok antes de continuar."
    exit 1
fi

if [ ! -f "$NGROK_CONFIG" ]; then
    echo "Error: no existe:"
    echo "  $NGROK_CONFIG"
    echo
    echo "Utiliza como referencia:"
    echo "  deploy/ngrok/ngrok.yml.example"
    exit 1
fi

if [ ! -f "$SERVICE_TEMPLATE" ]; then
    echo "Error: no existe:"
    echo "  $SERVICE_TEMPLATE"
    exit 1
fi

echo "Validando configuracion..."

sudo -u "$INSTALL_USER" \
    "$NGROK_BIN" config check

echo
echo "Generando ngrok.service..."

sed \
    -e "s|^User=.*|User=$INSTALL_USER|" \
    -e "s|^WorkingDirectory=.*|WorkingDirectory=$USER_HOME|" \
    "$SERVICE_TEMPLATE" \
    > "$SERVICE_TARGET"

echo "Recargando systemd..."

systemctl daemon-reload

echo "Habilitando ngrok..."

systemctl enable ngrok.service

echo
echo "Instalacion completada."
echo
echo "Para iniciar ngrok:"
echo "  sudo systemctl start ngrok"
echo
echo "Para comprobarlo:"
echo "  sudo systemctl status ngrok --no-pager"