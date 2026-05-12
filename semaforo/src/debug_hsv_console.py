import os
import sys
import cv2
import numpy as np

# Ajusta o sys.path para reconhecer a raiz do projeto
PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
if PROJ_ROOT not in sys.path:
    sys.path.insert(0, PROJ_ROOT)

# raiz semaforo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

# imagem
img_path = os.path.join(BASE_DIR, 'assets', 'images', 'img_001.jpeg')

img = cv2.imread(img_path)

if img is None:
    raise FileNotFoundError(f'Imagem não encontrada: {img_path}')

print(f"Imagem carregada: {img_path}")
print(f"Shape: {img.shape} (H, W, C)")

# ROI
roi = (80, 20, 80, 170)
x, y, w, h = roi

roi_img = img[y:y+h, x:x+w]

print(f"\nROI: {roi}")
print(f"ROI shape: {roi_img.shape}")
print(f"ROI non-zero pixels: {np.count_nonzero(roi_img)}")

# Pré-processamento
roi_img = cv2.bilateralFilter(roi_img, 9, 75, 75)

lab = cv2.cvtColor(roi_img, cv2.COLOR_BGR2LAB)
l_channel = lab[:,:,0]
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
l_channel = clahe.apply(l_channel)
lab[:,:,0] = l_channel
roi_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)

print(f"\nHSV ranges:")
print(f"  H: {hsv[:,:,0].min()} - {hsv[:,:,0].max()}")
print(f"  S: {hsv[:,:,1].min()} - {hsv[:,:,1].max()}")
print(f"  V: {hsv[:,:,2].min()} - {hsv[:,:,2].max()}")

# Testar ranges atuais
from semaforo.src.pipeline.traffic_light import TrafficLightDetector

detector = TrafficLightDetector()

print(f"\n=== Ranges Atuais do Detector ===")
print(f"Red1:   H{detector.lower_red1[0]:3d}-{detector.upper_red1[0]:3d} S{detector.lower_red1[1]:3d}-{detector.upper_red1[1]:3d} V{detector.lower_red1[2]:3d}-{detector.upper_red1[2]:3d}")
print(f"Red2:   H{detector.lower_red2[0]:3d}-{detector.upper_red2[0]:3d} S{detector.lower_red2[1]:3d}-{detector.upper_red2[1]:3d} V{detector.lower_red2[2]:3d}-{detector.upper_red2[2]:3d}")
print(f"Yellow: H{detector.lower_yellow[0]:3d}-{detector.upper_yellow[0]:3d} S{detector.lower_yellow[1]:3d}-{detector.upper_yellow[1]:3d} V{detector.lower_yellow[2]:3d}-{detector.upper_yellow[2]:3d}")
print(f"Green:  H{detector.lower_green[0]:3d}-{detector.upper_green[0]:3d} S{detector.lower_green[1]:3d}-{detector.upper_green[1]:3d} V{detector.lower_green[2]:3d}-{detector.upper_green[2]:3d}")

# Testar máscaras
red_mask = cv2.inRange(hsv, detector.lower_red1, detector.upper_red1)
red_mask += cv2.inRange(hsv, detector.lower_red2, detector.upper_red2)
yellow_mask = cv2.inRange(hsv, detector.lower_yellow, detector.upper_yellow)
green_mask = cv2.inRange(hsv, detector.lower_green, detector.upper_green)

red_pixels = cv2.countNonZero(red_mask)
yellow_pixels = cv2.countNonZero(yellow_mask)
green_pixels = cv2.countNonZero(green_mask)

print(f"\n=== Pixels Detectados ===")
print(f"Red:    {red_pixels}")
print(f"Yellow: {yellow_pixels}")
print(f"Green:  {green_pixels}")

min_pixels = (h * w) * 0.01
print(f"\nLimiar mínimo (1% de {h*w}): {min_pixels:.0f}")

# Testar com ranges expandidos
print(f"\n=== Testando ranges expandidos ===")

# Expandir ranges
lower_red1_exp = np.array([0, 30, 30])
upper_red1_exp = np.array([15, 255, 255])
lower_red2_exp = np.array([165, 30, 30])
upper_red2_exp = np.array([180, 255, 255])

lower_yellow_exp = np.array([10, 40, 40])
upper_yellow_exp = np.array([50, 255, 255])

lower_green_exp = np.array([30, 30, 30])
upper_green_exp = np.array([100, 255, 255])

red_mask_exp = cv2.inRange(hsv, lower_red1_exp, upper_red1_exp)
red_mask_exp += cv2.inRange(hsv, lower_red2_exp, upper_red2_exp)
yellow_mask_exp = cv2.inRange(hsv, lower_yellow_exp, upper_yellow_exp)
green_mask_exp = cv2.inRange(hsv, lower_green_exp, upper_green_exp)

print(f"Red (expanded):    {cv2.countNonZero(red_mask_exp)}")
print(f"Yellow (expanded): {cv2.countNonZero(yellow_mask_exp)}")
print(f"Green (expanded):  {cv2.countNonZero(green_mask_exp)}")
