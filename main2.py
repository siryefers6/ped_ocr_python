import re, platform
import cv2
import pytesseract
from functions import archivo_mas_reciente_carpeta, guardar_subir_github
import time

# Marca el inicio del tiempo
start_time = time.time()

if platform.system() == "Windows":
    # Solo se ejecuta si el sistema operativo es Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    video_path = 'pedidos.mp4'
else:
    video_path = archivo_mas_reciente_carpeta('/sdcard/DCIM/Camera')


# Configuración de Tesseract
config = r'--oem 3 --psm 11 outputbase digits'


# Crear un objeto de captura de video
cap = cv2.VideoCapture(video_path)

# Verificar si el video se ha abierto correctamente
if not cap.isOpened():
    print("Error al abrir el archivo de video")
    
    # Limpiar el contenido del archivo archivo_actual.txt
    with open('archivo_actual.txt', 'w') as f:
        f.write('')
        
    exit()

# Obtener el número total de cuadros en el video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

frame_interval = 8  # Leer cada 8 cuadros
frame_count = 0

numeros_pedidos = []

print(f'ARCHIVO DETECTADO: {video_path}')

while frame_count < total_frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Obtener las dimensiones de la imagen
    height, width = gray.shape

    # Definir los porcentajes de recorte de la parte superior e inferior
    recorte_superior = 0.3  # 25% de la parte superior
    recorte_inferior = 0.05  # 25% de la parte inferior

    # Calcular las coordenadas para recortar la parte central
    start_row = int(height * recorte_superior)  # Inicio del recorte
    end_row = int(height * (1 - recorte_inferior))  # Fin del recorte

    # Recortar la imagen para conservar solo la parte central
    center_section = gray[start_row:end_row, :]
    
    # Aplicar un filtro de desenfoque gaussiano para suavizar la imagen
    imagen_blur = cv2.GaussianBlur(center_section , (3, 3), 0)

    # Aplicar binarización Otsu para segmentar el texto del fondo
    _, imagen_bin = cv2.threshold(imagen_blur, 170, 255, cv2.THRESH_TRUNC)

    if platform.system() == "Windows":
        # Mostrar la imagen binarizada
        cv2.imshow('Imagen Binarizada', imagen_bin)
        # Opción para detener el video cuando se presiona una tecla
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    text = pytesseract.image_to_string(imagen_bin, config=config)

    match = re.findall(r"3[0123]\d{6}", text)
    number = ""
    if match:
        if len(match) > 1:
            number = match[-1]
        else:
            number = match[0]
        if number not in numeros_pedidos:
            print(f"Pedido: {number}")
            numeros_pedidos.append(number)

    frame_count += frame_interval

lista_pedidos = ""
for num in numeros_pedidos:
    lista_pedidos += num + '\n\n'

# Liberar el objeto de captura y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()

# Guardar lista en archivo README.md y subir al repositorio
if len(numeros_pedidos) > 1:
    guardar_subir_github(string_a_almacenar=lista_pedidos, path_archivo_destino='README.md')

print(f'Pedidos detectados: {len(numeros_pedidos)}')
print()

# Marca el final del tiempo
end_time = time.time()

# Calcula el tiempo de ejecución
execution_time = end_time - start_time

print(f"Tiempo de ejecución: {execution_time} segundos")