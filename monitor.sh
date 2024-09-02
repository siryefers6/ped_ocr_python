#!/bin/bash

# Ruta de la carpeta a monitorear
DIRECTORIO="$(dirname "$(realpath "$0")")"
DIRECTORIO_OCR="/sdcard/DCIM/Camera"

# Archivo que guarda el nombre del último archivo más reciente
ARCHIVO_ACTUAL="$DIRECTORIO/archivo_actual.txt"

# Intervalo de tiempo entre verificaciones (en segundos)
INTERVALO=3

# Bucle infinito para monitorear cambios
while true; do
    # Detectar el archivo más reciente en la carpeta
    ARCHIVO_MAS_RECIENTE=$(ls -t "$DIRECTORIO_OCR" | head -n 1)

    # Verificar si el archivo más reciente ha cambiado
    if [ -f "$ARCHIVO_ACTUAL" ]; then
        ULTIMO_ARCHIVO=$(cat "$ARCHIVO_ACTUAL")
    else
        ULTIMO_ARCHIVO=""
    fi

    # Si el archivo más reciente es diferente al guardado, actualizar y ejecutar el script Python correspondiente
    if [ "$ARCHIVO_MAS_RECIENTE" != "$ULTIMO_ARCHIVO" ]; then
        echo "$ARCHIVO_MAS_RECIENTE" > "$ARCHIVO_ACTUAL"
        
        # Obtener la extensión del archivo más reciente
        EXTENSION="${ARCHIVO_MAS_RECIENTE##*.}"
        
        # Ejecutar el script Python según la extensión del archivo
        if [ "$EXTENSION" == "mp4" ]; then
            python3 "$DIRECTORIO/main.py"
        elif [ "$EXTENSION" == "jpg" ] || [ "$EXTENSION" == "png" ]; then
            python3 "$DIRECTORIO/ocr_documents.py"
        fi
    fi

    # Esperar antes de la próxima verificación
    sleep $INTERVALO
done
