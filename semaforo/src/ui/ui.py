import os
import cv2
import time
import sys
import tkinter as tk
from tkinter import filedialog

# =========================
# BASE DO PROJETO
# =========================

# ui.py -> sobe dois níveis
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# =========================
# IMPORTS INTERNOS
# =========================

from src.ui.main_menu import MainMenu
from src.ui.calibration import Calibration
from src.ui.dashboard import Dashboard

from src.pipeline.traffic_light import TrafficLightDetector
from src.utils.violelation_monitor import ViolationMonitor
from src.utils.video_converter import VideoConverter


converter = VideoConverter()
# =========================
# MENU INICIAL
# =========================

menu = MainMenu()
#mode = menu.show()

#print("Modo selecionado:", mode)

# =========================
# VARIÁVEIS
# =========================

use_flip = False
frame = None
cap = None

# =========================
# ENTRADA
# =========================
mode = "webcam"  # para desenvolvimento rápido, ignora o menu

if mode == "image":

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Selecione uma imagem ou vídeo",
        filetypes=[
            ("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("Vídeos", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("Todos", "*.*"),
        ]
    )

    if not file_path:
        raise FileNotFoundError("Nenhum arquivo selecionado.")

    ext = os.path.splitext(file_path)[1].lower()

    # =========================
    # VÍDEO
    # =========================

    if ext in (".mp4", ".avi", ".mov", ".mkv", ".webm"):

        mode = "webcam"  # reutiliza o loop principal

        cap = cv2.VideoCapture(file_path)

        if not cap.isOpened():
            raise Exception(f"Erro ao abrir vídeo: {file_path}")

        ret, frame = cap.read()

        if not ret or frame is None:
            raise Exception("Erro ao ler primeiro frame do vídeo.")

    # =========================
    # IMAGEM
    # =========================

    else:

        frame = cv2.imread(file_path)

        if frame is None:
            raise FileNotFoundError(
                f"Erro ao carregar imagem: {file_path}"
            )

# =========================
# WEBCAM
# =========================

elif mode == "webcam":

    use_flip = True

    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        raise Exception("Erro ao abrir webcam.")

    ret, frame = cap.read()

    if not ret or frame is None:
        raise Exception("Erro na captura da webcam.")

    if use_flip:
        frame = cv2.flip(frame, 1)

# =========================
# CALIBRAÇÃO
# =========================

calibration = Calibration()

traffic_roi = calibration.select_traffic_roi(frame)

line_points = calibration.select_retention_line(frame)

print("ROI:", traffic_roi)
print("Linha:", line_points)

# =========================
# DETECTOR
# =========================

detector = TrafficLightDetector()

dashboard = Dashboard()

logs = []

monitor = ViolationMonitor(
    output_dir="violations",
    retention_line_y=None,
    csv_path="violations/log.csv",
    min_contour_area=1500,
)

# =========================
# VIDEO WRITER
# =========================

h, w = frame.shape[:2]

output_path = os.path.join(
    BASE_DIR,
    "violations",
    "output.avi"
)

# garante que a pasta exista
os.makedirs(os.path.dirname(output_path), exist_ok=True)

out = cv2.VideoWriter(
    output_path,
    cv2.VideoWriter_fourcc(*"XVID"),
    30,
    (w + 350, h)
)

# =========================
# JANELA
# =========================

cv2.namedWindow(
    "Smart Traffic System",
    cv2.WINDOW_NORMAL
)

# =========================
# LOOP PRINCIPAL
# =========================

while True:

    start = time.time()

    # =========================
    # CAPTURA
    # =========================

    if mode == "webcam":

        ret, frame = cap.read()

        if not ret or frame is None:
            print("Falha na captura.")
            break

        if use_flip:
            frame = cv2.flip(frame, 1)

    display = frame.copy()

    # =========================
    # DETECÇÃO DO SEMÁFORO
    # =========================

    result = detector.detect(display, traffic_roi)

    state = result["state"]

    # desenha ROI
    x, y, rw, rh = traffic_roi

    cv2.rectangle(
        display,
        (x, y),
        (x + rw, y + rh),
        (255, 0, 0),
        2
    )

    # desenha linha
    cv2.line(
        display,
        line_points[0],
        line_points[1],
        (0, 0, 255),
        3
    )

    # =========================
    # MONITORAMENTO
    # =========================

    mon_result = monitor.update(display, state)

    annotated_frame = mon_result["annotated_frame"]

    violations_total = mon_result["violations"]

    if mon_result["new_violation"]:
        logs.append("[ALERTA] Violação detectada")

    # =========================
    # FPS
    # =========================

    elapsed = time.time() - start

    fps = 1 / elapsed if elapsed > 0 else 0

    # =========================
    # DASHBOARD
    # =========================

    panel = dashboard.build(
        annotated_frame,
        state,
        violations_total,
        fps,
        logs
    )

    # grava vídeo
    out.write(panel)

    # exibe
    cv2.imshow(
        "Smart Traffic System",
        panel
    )

    # =========================
    # CONTROLES
    # =========================

    if mode == "image":
        cv2.waitKey(0)
        break

    key = cv2.waitKey(1)

    if (
        key == 27
        or cv2.getWindowProperty(
            "Smart Traffic System",
            cv2.WND_PROP_VISIBLE
        ) < 1
    ):
        break

# =========================
# FINALIZAÇÃO
# =========================

if cap is not None:
    cap.release()

out.release()

cv2.destroyAllWindows()

print(f"Vídeo salvo em: {output_path}")

converted_video = VideoConverter.convert_to_h264(
    output_path,
    delete_original=True
)