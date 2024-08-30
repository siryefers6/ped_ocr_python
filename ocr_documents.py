import re
import cv2
import pytesseract
import platform
from functions import archivo_mas_reciente_carpeta, guardar_subir_github


if platform.system() == "Windows":
    # Solo se ejecuta si el sistema operativo es Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image_path = 'doc.jpg'
else:
    image_path = archivo_mas_reciente_carpeta('/sdcard/DCIM/Camera')


# Cargar la imagen en escala de grises
imagen = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Aplicar un filtro de desenfoque gaussiano para suavizar la imagen
imagen_blur = cv2.GaussianBlur(imagen, (5, 5), 0)

# Aplicar la técnica de morfología para obtener el fondo
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
background = cv2.morphologyEx(imagen_blur, cv2.MORPH_DILATE, kernel)

# Restar el fondo de la imagen original para obtener la imagen sin sombras
imagen_sin_sombra = cv2.absdiff(imagen_blur, background)

# Invertir la imagen para hacer el texto blanco sobre fondo negro
imagen_invertida = cv2.bitwise_not(imagen_sin_sombra)

# Aplicar binarización Otsu para segmentar el texto del fondo
_, imagen_bin = cv2.threshold(imagen_invertida, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Realizar el reconocimiento de texto con Tesseract
text = pytesseract.image_to_string(imagen_bin, config=r'--oem 3 --psm 6')
text = re.sub(r"[^A-Z0-9\.\,\/\%\@\n ]", "", text)

lines = text.split('\n')
text_complete = ''
for line in lines:
    if line != '':
        text_complete += line.replace("@", "0") + '\n\n'

print(text_complete)

# Guardar texto en archivo README.md y subir al repositorio
guardar_subir_github(string_a_almacenar=text_complete, path_archivo_destino='README.md')
