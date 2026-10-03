#!/bin/bash

set -e

DATABASE_NAME="uvg_collections"

if [ "$#" -ne 1 ]; then
    echo "Uso:"
    echo "  sudo $0 <archivo-backup.dump>"
    echo
    echo "Ejemplo:"
    echo "  sudo $0 backups/uvg_collections_2026-10-03_05-30-10.dump"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: no existe el archivo:"
    echo "  $BACKUP_FILE"
    exit 1
fi

echo "Restauracion de PostgreSQL"
echo
echo "Base de datos: $DATABASE_NAME"
echo "Backup:        $BACKUP_FILE"
echo
echo "ADVERTENCIA:"
echo "La base de datos '$DATABASE_NAME' sera reemplazada."
echo

read -r -p "Escribe RESTAURAR para continuar: " CONFIRMATION

if [ "$CONFIRMATION" != "RESTAURAR" ]; then
    echo
    echo "Restauracion cancelada."
    exit 1
fi

echo
echo "Deteniendo servicios..."

systemctl stop uvg-rfid.service
systemctl stop uvgcollections.service

echo "Eliminando base de datos existente..."

sudo -u postgres dropdb \
    --if-exists \
    "$DATABASE_NAME"

echo "Creando base de datos..."

sudo -u postgres createdb \
    "$DATABASE_NAME"

echo "Restaurando respaldo..."

sudo -u postgres pg_restore \
    --dbname="$DATABASE_NAME" \
    < "$BACKUP_FILE"

echo
echo "Restauracion completada."
echo

echo "Iniciando servicios..."

systemctl start uvgcollections.service
systemctl start uvg-rfid.service

echo
echo "Estado de los servicios:"
echo

systemctl is-active uvgcollections.service
systemctl is-active uvg-rfid.service

echo
echo "Base de datos restaurada correctamente."