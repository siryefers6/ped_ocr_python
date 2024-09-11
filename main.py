import re, platform, time
from multiprocessing import Process, Queue
import cv2
import pytesseract
from functions import archivo_mas_reciente_carpeta, guardar_subir_github

# Marca el inicio del tiempo
start_time = time.time()

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
 
def process_video_segment(video_path, start_frame, end_frame, frame_interval, config, output_queue, segment_index):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    results = []

    while start_frame < end_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        # Recorte y preprocesamiento
        recorte_superior = 0.3
        recorte_inferior = 0.05
        start_row = int(height * recorte_superior)
        end_row = int(height * (1 - recorte_inferior))
        center_section = gray[start_row:end_row, :]
        imagen_blur = cv2.GaussianBlur(center_section , (3, 3), 0)
        _, imagen_bin = cv2.threshold(imagen_blur, 170, 255, cv2.THRESH_TRUNC)

        text = pytesseract.image_to_string(imagen_bin, config=config)
        match = re.findall(r"3[0123]\d{6}", text)

        if match:
            number = match[-1] if len(match) > 1 else match[0]
            results.append((start_frame, number))

        start_frame += frame_interval

    cap.release()
    output_queue.put((segment_index, results))

def main():
    print("Detección iniciada...")

    if platform.system() == "Windows":
        video_path = 'pedidos.mp4'
    else:
        video_path = archivo_mas_reciente_carpeta('/sdcard/DCIM/Camera')

    config = r'--oem 3 --psm 11 outputbase digits'
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error al abrir el archivo de video")
        with open('archivo_actual.txt', 'w') as f:
            f.write('')
        exit()

    multiprocesos_activos = 4
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = 6
    cap.release()

    quarter_frame = total_frames // multiprocesos_activos
    output_queue = Queue()
    processes = []

    for i in range(multiprocesos_activos):
        start_frame = i * quarter_frame
        end_frame = (i + 1) * quarter_frame if i != multiprocesos_activos-1 else total_frames
        process = Process(target=process_video_segment, args=(video_path, start_frame, end_frame, frame_interval, config, output_queue, i))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    # Recolectar y unir los resultados
    all_results = []
    while not output_queue.empty():
        segment_index, results = output_queue.get()
        all_results.extend(results)

    # Ordenar los resultados por el índice de frame
    all_results.sort(key=lambda x: x[0])

    # Extraer los números de pedidos en orden de aparición
    final_pedidos = []
    for _, pedido in all_results:
        if pedido not in final_pedidos:
            final_pedidos.append(pedido)

    lista_pedidos = ""
    lista_pedidos_simple = ""
    for num in final_pedidos:
        lista_pedidos += num + '\n\n'
        lista_pedidos_simple += num + '\n'

    print(lista_pedidos_simple)
    print(f'Pedidos detectados: {len(final_pedidos)}')
    print("----------------------------------------------------------\n")

    # Guardar lista en archivo README.md y subir al repositorio
    if len(final_pedidos) > 1:
        guardar_subir_github(string_a_almacenar=lista_pedidos, path_archivo_destino='README.md')

    print(f'Pedidos detectados: {len(final_pedidos)}')
    print("Detección Finalizada.")

if __name__ == '__main__':
    main()
    # Marca el final del tiempo
    end_time = time.time()

    # Calcula el tiempo de ejecución
    execution_time = end_time - start_time

    print(f"Tiempo de ejecución: {execution_time} segundos")
    print("==========================================================\n")
