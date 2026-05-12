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
img_path = os.path.join(
    BASE_DIR,
    'assets',
    'images',
    'img_001.jpeg'
)

img = cv2.imread(img_path)

if img is None:
    raise FileNotFoundError(f'Imagem não encontrada: {img_path}')

# ROI MANUAL
roi = (80, 20, 80, 170)
x, y, w, h = roi

roi_img = img[y:y+h, x:x+w]

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

print(f"\nHSV shape: {hsv.shape}")
print(f"HSV min/max H: {hsv[:,:,0].min()}/{hsv[:,:,0].max()}")
print(f"HSV min/max S: {hsv[:,:,1].min()}/{hsv[:,:,1].max()}")
print(f"HSV min/max V: {hsv[:,:,2].min()}/{hsv[:,:,2].max()}")

# Mostrar histogramas
print("\n=== Histogramas ===")
for i, color in enumerate(['H', 'S', 'V']):
    hist = cv2.calcHist([hsv], [i], None, [256], [0, 256])
    non_zero = np.count_nonzero(hist)
    print(f"{color}: {non_zero} valores não-zero, máximo: {hist.max():.0f}")

# Testar ranges atuais
from semaforo.src.pipeline.traffic_light import TrafficLightDetector

detector = TrafficLightDetector()

print("\n=== Ranges Atuais ===")
print(f"Red1: {detector.lower_red1} - {detector.upper_red1}")
print(f"Red2: {detector.lower_red2} - {detector.upper_red2}")
print(f"Yellow: {detector.lower_yellow} - {detector.upper_yellow}")
print(f"Green: {detector.lower_green} - {detector.upper_green}")

# Testar máscaras
red_mask = cv2.inRange(hsv, detector.lower_red1, detector.upper_red1)
red_mask += cv2.inRange(hsv, detector.lower_red2, detector.upper_red2)
yellow_mask = cv2.inRange(hsv, detector.lower_yellow, detector.upper_yellow)
green_mask = cv2.inRange(hsv, detector.lower_green, detector.upper_green)

print(f"\nPixels encontrados:")
print(f"Red: {cv2.countNonZero(red_mask)}")
print(f"Yellow: {cv2.countNonZero(yellow_mask)}")
print(f"Green: {cv2.countNonZero(green_mask)}")

# Mostrar imagem e máscaras
cv2.imshow("ROI Original", roi_img)
cv2.imshow("Red Mask", red_mask)
cv2.imshow("Yellow Mask", yellow_mask)
cv2.imshow("Green Mask", green_mask)

cv2.waitKey(0)
cv2.destroyAllWindows()
