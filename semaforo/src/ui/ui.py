import os
import cv2
import time
import sys

# Pega o caminho absoluto da pasta 'semaforo' (raiz do projeto)
# Como ui.py está em src/ui/ui.py, precisamos subir dois níveis
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.ui.main_menu import MainMenu
from src.ui.calibration import Calibration
from src.ui.dashboard import Dashboard

from src.pipeline.traffic_light import TrafficLightDetector


# =========================
# MENU INICIAL
# =========================

menu = MainMenu()

mode = menu.show()

print("Modo selecionado:", mode)

# =========================
# ENTRADA
# =========================

frame = None
cap = None

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)

if mode == "image":

    img_path = os.path.join(
        BASE_DIR,
        'assets',
        'images',
        '2.jpg'
    )

    frame = cv2.imread(img_path)

    if frame is None:
        raise FileNotFoundError(img_path)

elif mode == "webcam":

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Erro webcam")

    ret, frame = cap.read()

    if not ret:
        raise Exception("Erro captura webcam")


# =========================
# CALIBRAÇÃO
# =========================

calibration = Calibration()

# ROI do semáforo
traffic_roi = calibration.select_traffic_roi(frame)

# linha retenção
line_points = calibration.select_retention_line(frame)

# bird eye
bird_points = calibration.select_perspective_points(frame)

print("ROI:", traffic_roi)
print("Linha:", line_points)
print("Bird Eye:", bird_points)

# =========================
# DETECTOR
# =========================

detector = TrafficLightDetector()

dashboard = Dashboard()

logs = []

violations = 0

# =========================
# LOOP PRINCIPAL
# =========================

while True:

    start = time.time()

    if mode == "webcam":

        ret, frame = cap.read()

        if not ret:
            print("Falha webcam")
            break

    display = frame.copy()

    # =========================
    # DETECÇÃO SEMÁFORO
    # =========================

    result = detector.detect(
        display,
        traffic_roi
    )

    state = result["state"]

    # =========================
    # DESENHA ROI
    # =========================

    x, y, w, h = traffic_roi

    cv2.rectangle(
        display,
        (x, y),
        (x+w, y+h),
        (255,0,0),
        2
    )

    # =========================
    # DESENHA LINHA
    # =========================

    cv2.line(
        display,
        line_points[0],
        line_points[1],
        (0,0,255),
        3
    )

    # =========================
    # EVENTO FAKE TESTE
    # =========================

    if state == "RED":

        violations += 1

        logs.append(
            f"[ALERTA] Violacao detectada"
        )

    # =========================
    # FPS
    # =========================

    end = time.time()

    fps = 1 / (end - start)

    # =========================
    # DASHBOARD
    # =========================

    panel = dashboard.build(
        display,
        state,
        violations,
        fps,
        logs
    )

    cv2.imshow(
        "Smart Traffic System",
        panel
    )

    key = cv2.waitKey(1)

    if key == 27:
        break

    # imagem estática
    if mode == "image":
        cv2.waitKey(0)
        break

# =========================
# FINALIZAÇÃO
# =========================

if cap is not None:
    cap.release()

cv2.destroyAllWindows()