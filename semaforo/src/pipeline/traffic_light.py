import cv2
import numpy as np


class TrafficLightDetector:

    def __init__(self):

        # Vermelho (dois ranges devido ao wrapping do HSV em 180°)
        # Range 1: H 0-12
        self.lower_red1 = np.array([0, 50, 50])
        self.upper_red1 = np.array([12, 255, 255])
        
        # Range 2: H 168-180
        self.lower_red2 = np.array([168, 50, 50])
        self.upper_red2 = np.array([180, 255, 255])

        # Amarelo/Laranja: H 15-45
        self.lower_yellow = np.array([15, 60, 60])
        self.upper_yellow = np.array([45, 255, 255])

        # Verde: H 35-95
        self.lower_green = np.array([35, 40, 40])
        self.upper_green = np.array([95, 255, 255])

    def detect(self, image, roi):

        x, y, w, h = roi

        roi_img = image[y:y+h, x:x+w]

        # Validação: verifica se roi_img não está vazio
        if roi_img is None or roi_img.size == 0:
            empty_mask = np.zeros((h, w), dtype=np.uint8)
            return {
                "state": "UNKNOWN",
                "roi": roi,
                "red_pixels": 0,
                "yellow_pixels": 0,
                "green_pixels": 0,
                "red_mask": empty_mask,
                "yellow_mask": empty_mask,
                "green_mask": empty_mask
            }

        # Pré-processamento: denoise e melhorar contraste
        roi_img = cv2.bilateralFilter(roi_img, 9, 75, 75)
       

        # Aumentar contraste usando CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(roi_img, cv2.COLOR_BGR2LAB)
        l_channel = lab[:,:,0]
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_channel = clahe.apply(l_channel)
        lab[:,:,0] = l_channel
        roi_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)

        # máscaras
        red_mask = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        red_mask += cv2.inRange(hsv, self.lower_red2, self.upper_red2)

        yellow_mask = cv2.inRange(hsv,
                                  self.lower_yellow,
                                  self.upper_yellow)

        green_mask = cv2.inRange(hsv,
                                 self.lower_green,
                                 self.upper_green)

        # Operações morfológicas para limpar ruído
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        
        yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
        yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
        
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

        # contagem pixels
        red_pixels = cv2.countNonZero(red_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        green_pixels = cv2.countNonZero(green_mask)

        # Limiar mínimo para evitar ruído (1% da área da ROI)
        min_pixels = 50
        
        state = "UNKNOWN"

        if red_pixels > min_pixels and red_pixels > yellow_pixels and red_pixels > green_pixels:
            state = "RED"

        elif yellow_pixels > min_pixels and yellow_pixels > red_pixels and yellow_pixels > green_pixels:
            state = "YELLOW"

        elif green_pixels > min_pixels and green_pixels > red_pixels and green_pixels > yellow_pixels:
            state = "GREEN"

        return {
            "state": state,
            "roi": roi,
            "red_pixels": red_pixels,
            "yellow_pixels": yellow_pixels,
            "green_pixels": green_pixels,
            "red_mask": red_mask,
            "yellow_mask": yellow_mask,
            "green_mask": green_mask
        }