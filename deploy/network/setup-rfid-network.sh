#!/bin/bash

set -e

PROFILE_NAME="RFID"
RFID_SERVER_IP="192.168.1.23/24"

if [ "$#" -ne 1 ]; then
    echo "Uso:"
    echo "  sudo $0 <interfaz-ethernet>"
    echo
    echo "Ejemplo:"
    echo "  sudo $0 eno1"
    exit 1
fi

INTERFACE="$1"

echo "Configurando red Ethernet para RFID..."
echo
echo "Interfaz: $INTERFACE"
echo "Perfil:   $PROFILE_NAME"
echo "IP:       $RFID_SERVER_IP"
echo

if ! ip link show "$INTERFACE" > /dev/null 2>&1; then
    echo "Error: la interfaz '$INTERFACE' no existe."
    echo
    echo "Interfaces disponibles:"
    ip -br link
    exit 1
fi

if nmcli connection show "$PROFILE_NAME" > /dev/null 2>&1; then

    echo "El perfil '$PROFILE_NAME' ya existe."
    echo "Actualizando configuracion..."

    nmcli connection modify "$PROFILE_NAME" \
        connection.interface-name "$INTERFACE" \
        ipv4.method manual \
        ipv4.addresses "$RFID_SERVER_IP" \
        ipv4.gateway "" \
        ipv4.dns "" \
        ipv4.never-default yes \
        connection.autoconnect yes

else

    echo "Creando perfil '$PROFILE_NAME'..."

    nmcli connection add \
        type ethernet \
        ifname "$INTERFACE" \
        con-name "$PROFILE_NAME" \
        ipv4.method manual \
        ipv4.addresses "$RFID_SERVER_IP"

    nmcli connection modify "$PROFILE_NAME" \
        ipv4.gateway "" \
        ipv4.dns "" \
        ipv4.never-default yes \
        connection.autoconnect yes

fi

echo
echo "Activando perfil..."

nmcli connection up "$PROFILE_NAME"

echo
echo "Configuracion completada."
echo
echo "Estado de la interfaz:"
ip -br addr show "$INTERFACE"
echo
echo "Ruta hacia el lector RFID:"
ip route get 192.168.1.116git status