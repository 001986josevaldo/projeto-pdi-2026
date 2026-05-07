import cv2
import numpy as np

class Detection:
    def __init__(self):
        self.kernel = np.ones((5,5), np.uint8)

    def edges(self, img):
        return cv2.Canny(img, 50, 150)

    def clean(self, mask):
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

    def contours(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours