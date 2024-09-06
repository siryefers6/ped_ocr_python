import subprocess
from pathlib import Path


def archivo_mas_reciente_carpeta(carpeta):
    # Convertir la ruta a un objeto Path
    carpeta_path = Path(carpeta)

    # Obtener todos los archivos en la carpeta
    archivos = list(carpeta_path.glob('*'))

    # Filtrar solo los archivos (excluye directorios)
    archivos = [archivo for archivo in archivos if archivo.is_file()]

    # Verificar si hay archivos en la carpeta
    if not archivos:
        raise FileNotFoundError("No se encontraron archivos en la carpeta especificada.")

    # Obtener el archivo más reciente
    archivo_mas_reciente = max(archivos, key=lambda x: x.stat().st_mtime)

    return archivo_mas_reciente


def guardar_subir_github(string_a_almacenar: str, path_archivo_destino: str):
    # Convertir la ruta a un objeto Path
    path_archivo = Path(path_archivo_destino)

    # Escribir el string en el archivo
    with open(path_archivo, "w", encoding="utf-8") as file:
        file.write(string_a_almacenar)

    print(f"Texto extraído y guardado en {path_archivo}")

    # Comando para añadir cambios al último commit y forzar el push
    command = "git add . && git commit -m 'actualizado' && git push"

    # Ejecutar el comando
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Obtener la salida y los errores
    stdout, stderr = process.communicate()

    # Mostrar resultados
    if process.returncode == 0:
        print("Comando ejecutado con éxito:")
        print(stdout.decode())
    else:
        print("Error al ejecutar el comando:")
        print(stderr.decode())
