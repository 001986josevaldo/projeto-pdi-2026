import cv2
import numpy as np


class TrafficLightDetector:

    def __init__(self):

        # Vermelho: ranges mais restritos e saturação/valor mínimos mais altos
        # Range 1: H 0-8 (vermelho puro, evita laranja que começa em ~10)
        self.lower_red1 = np.array([0, 120, 100])   # S mín 120, V mín 100
        self.upper_red1 = np.array([8, 255, 255])

        # Range 2: H 172-180 (vermelho pelo outro lado, evita magenta/rosa)
        self.lower_red2 = np.array([172, 120, 100])
        self.upper_red2 = np.array([180, 255, 255])

        # Amarelo: H 18-38, saturação alta para não pegar branco/bege
        self.lower_yellow = np.array([18, 120, 100])
        self.upper_yellow = np.array([38, 255, 255])

        # Verde: H 40-90, evita sobreposição com amarelo
        self.lower_green = np.array([40, 60, 60])
        self.upper_green = np.array([90, 255, 255])

    def _exclude_white(self, hsv):
        """Máscara para excluir pixels brancos/acinzentados (baixa saturação)."""
        # Branco: S < 60 e V > 180
        white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 60, 255]))
        return white_mask

    def _exclude_blue(self, hsv):
        """Máscara para excluir pixels azuis (H 90-135)."""
        return cv2.inRange(hsv, np.array([90, 60, 60]), np.array([135, 255, 255]))

    def _exclude_orange(self, hsv):
        """Máscara para excluir laranja (H 9-17) que não é vermelho nem amarelo."""
        return cv2.inRange(hsv, np.array([9, 100, 100]), np.array([17, 255, 255]))

    def detect(self, image, roi):

        x, y, w, h = roi
        roi_img = image[y:y+h, x:x+w]

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

        # Pré-processamento
        roi_img = cv2.bilateralFilter(roi_img, 9, 75, 75)

        lab = cv2.cvtColor(roi_img, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(l_channel)
        roi_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)

        # Máscaras de exclusão
        white_mask  = self._exclude_white(hsv)
        blue_mask   = self._exclude_blue(hsv)
        orange_mask = self._exclude_orange(hsv)

        # Área a ignorar: branco + azul + laranja
        exclusion_mask = cv2.bitwise_or(white_mask, blue_mask)
        exclusion_mask = cv2.bitwise_or(exclusion_mask, orange_mask)
        keep_mask = cv2.bitwise_not(exclusion_mask)  # pixels válidos

        # Máscaras de cor
        red_mask = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        red_mask = cv2.add(red_mask, cv2.inRange(hsv, self.lower_red2, self.upper_red2))

        yellow_mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        green_mask  = cv2.inRange(hsv, self.lower_green,  self.upper_green)

        # Aplicar exclusão nas máscaras
        red_mask    = cv2.bitwise_and(red_mask,    keep_mask)
        yellow_mask = cv2.bitwise_and(yellow_mask, keep_mask)
        green_mask  = cv2.bitwise_and(green_mask,  keep_mask)

        # Morfologia
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        for mask in (red_mask, yellow_mask, green_mask):
            cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, dst=mask)
            cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, dst=mask)

        red_pixels    = cv2.countNonZero(red_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        green_pixels  = cv2.countNonZero(green_mask)

        # Limiar proporcional à área da ROI (2% da área mínima)
        min_pixels = max(50, int(w * h * 0.02))

        state = "UNKNOWN"
        counts = {"RED": red_pixels, "YELLOW": yellow_pixels, "GREEN": green_pixels}
        dominant = max(counts, key=counts.get)

        if counts[dominant] >= min_pixels:
            state = dominant

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