#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
    echo "Uso:"
    echo "  $0 <ruta-usb>"
    echo
    echo "Ejemplo:"
    echo "  $0 /media/usuario/RESPALDOS"
    exit 1
fi

USB_PATH="$1"

SCRIPT_DIR="$(
    cd "$(dirname "$0")"
    pwd
)"

REPO_ROOT="$(
    cd "$SCRIPT_DIR/../.."
    pwd
)"

BACKUP_DIR="$REPO_ROOT/backups"

if [ ! -d "$USB_PATH" ]; then
    echo "Error: la ruta de la USB no existe:"
    echo "  $USB_PATH"
    exit 1
fi

LATEST_BACKUP="$(
    find "$BACKUP_DIR" \
        -maxdepth 1 \
        -type f \
        -name "uvg_collections_*.dump" \
        -printf "%T@ %p\n" \
        | sort -nr \
        | head -n 1 \
        | cut -d' ' -f2-
)"

if [ -z "$LATEST_BACKUP" ]; then
    echo "Error: no se encontraron respaldos en:"
    echo "  $BACKUP_DIR"
    exit 1
fi

DESTINATION="$USB_PATH/UVG_Collections_Backups"

mkdir -p "$DESTINATION"

echo "Copiando respaldo externo..."
echo
echo "Origen:"
echo "  $LATEST_BACKUP"
echo
echo "Destino:"
echo "  $DESTINATION"
echo

cp \
    --preserve=timestamps \
    "$LATEST_BACKUP" \
    "$DESTINATION/"

sync

COPIED_FILE="$DESTINATION/$(basename "$LATEST_BACKUP")"

echo "Verificando copia..."

if cmp -s "$LATEST_BACKUP" "$COPIED_FILE"; then

    echo
    echo "Respaldo externo completado correctamente."
    echo
    echo "Archivo:"
    echo "  $COPIED_FILE"

else

    echo
    echo "Error: la copia no coincide con el respaldo original."
    exit 1

fi