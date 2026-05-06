import cv2
import numpy as np

class Heatmap:
    def __init__(self, shape):
        self.map = np.zeros(shape[:2], dtype=np.uint8)

    def update(self, contours):
        for cnt in contours:
            cv2.drawContours(self.map, [cnt], -1, 255, -1)

    def get_colormap(self):
        return cv2.applyColorMap(self.map, cv2.COLORMAP_JET)