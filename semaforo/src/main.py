import os
import sys

# Suprime mensagens do Qt/OpenCV
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts=false"

import cv2

# Ajusta o sys.path para reconhecer a raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.traffic_light import TrafficLightDetector


# raiz projeto
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)

# imagem
img_path = os.path.join(
    BASE_DIR,
    'assets',
    'images',
    '2.jpg'
)
#caminhoi da imagem /media/josevaldo/E02A-3159/BCC/8_sem/PI/projeto_integrador/projeto-pdi-2026/semaforo/assets/images/2.jpg


img = cv2.imread(img_path)

if img is None:
    raise FileNotFoundError(f'Imagem não encontrada: {img_path}')


# ROI MANUAL
# x, y, largura, altura
# Ajustado para as dimensões reais da imagem (238x212)
roi = (0, 0, img.shape[1], img.shape[0])
print('roi:', roi)

detector = TrafficLightDetector()

result = detector.detect(img, roi)

state = result["state"]

# desenha ROI
x, y, w, h = roi

'''cv2.rectangle(
    img,
    (x, y),
    (x+w, y+h),
    (255, 0, 0),
    2
)
'''
'''# texto
cv2.putText(
    img,
    f'{state}',
    (10, 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)
'''
print("Estado detectado:", state)
print("Pixels vermelhos:", result["red_pixels"])
print("Pixels amarelos:", result["yellow_pixels"])
print("Pixels verdes:", result["green_pixels"])

'''# exibição
cv2.imshow("Traffic Light", img)

cv2.imshow("Red Mask", result["red_mask"])
cv2.imshow("Yellow Mask", result["yellow_mask"])
cv2.imshow("Green Mask", result["green_mask"])
'''
# =========================
# CONVERTE MÁSCARAS PARA BGR
# =========================

red_mask_bgr = cv2.cvtColor(
    result["red_mask"],
    cv2.COLOR_GRAY2BGR
)

yellow_mask_bgr = cv2.cvtColor(
    result["yellow_mask"],
    cv2.COLOR_GRAY2BGR
)

green_mask_bgr = cv2.cvtColor(
    result["green_mask"],
    cv2.COLOR_GRAY2BGR
)

# =========================
# COLORAÇÃO DAS MÁSCARAS
# =========================

# vermelho
red_mask_bgr[:, :, 2] = result["red_mask"]

# amarelo
yellow_mask_bgr[:, :, 1] = result["yellow_mask"]
yellow_mask_bgr[:, :, 2] = result["yellow_mask"]

# verde
green_mask_bgr[:, :, 1] = result["green_mask"]

# =========================
# REDIMENSIONAMENTO
# =========================

height = 300
width = 300

img_resize = cv2.resize(img, (width, height))
red_resize = cv2.resize(red_mask_bgr, (width, height))
yellow_resize = cv2.resize(yellow_mask_bgr, (width, height))
green_resize = cv2.resize(green_mask_bgr, (width, height))

# =========================
# TÍTULOS
# =========================

font = cv2.FONT_HERSHEY_SIMPLEX

cv2.putText(
    img_resize,
    f"Original - {state}",
    (10, 30),
    font,
    0.8,
    (0, 255, 0),
    2
)

cv2.putText(
    red_resize,
    "Red Mask",
    (10, 30),
    font,
    0.8,
    (0, 0, 255),
    2
)

cv2.putText(
    yellow_resize,
    "Yellow Mask",
    (10, 30),
    font,
    0.8,
    (0, 255, 255),
    2
)

cv2.putText(
    green_resize,
    "Green Mask",
    (10, 30),
    font,
    0.8,
    (0, 255, 0),
    2
)

# =========================
# PAINEL
# =========================

top = cv2.hconcat([
    img_resize,
    red_resize
])

bottom = cv2.hconcat([
    yellow_resize,
    green_resize
])

panel = cv2.vconcat([
    top,
    bottom
])

# =========================
# EXIBIÇÃO
# =========================

cv2.imshow("Painel Debug HSV", panel)

cv2.waitKey(0)
cv2.destroyAllWindows()
