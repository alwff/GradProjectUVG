#!/bin/bash

set -e

DATABASE_NAME="uvg_collections"

REPO_ROOT="$(
    cd "$(dirname "$0")/../.."
    pwd
)"

BACKUP_DIR="$REPO_ROOT/backups"

TIMESTAMP="$(
    date +"%Y-%m-%d_%H-%M-%S"
)"

BACKUP_FILE="$BACKUP_DIR/${DATABASE_NAME}_${TIMESTAMP}.dump"

mkdir -p "$BACKUP_DIR"

echo "Creando respaldo de PostgreSQL..."
echo
echo "Base de datos: $DATABASE_NAME"
echo "Destino:       $BACKUP_FILE"
echo

sudo -u postgres pg_dump \
    --format=custom \
    --file="$BACKUP_FILE" \
    "$DATABASE_NAME"

sudo chown \
    "$(id -un):$(id -gn)" \
    "$BACKUP_FILE"

chmod 600 "$BACKUP_FILE"

echo
echo "Respaldo completado."
echo
echo "Archivo:"
echo "  $BACKUP_FILE"
echo
echo "Tamano:"
du -h "$BACKUP_FILE"