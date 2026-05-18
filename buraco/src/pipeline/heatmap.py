import cv2
import numpy as np

class Heatmap:
    def __init__(self, shape):
        self.map = np.zeros((240,320), dtype=np.uint8)

    def update(self, contours):
        for cnt in contours:
            scaled = cnt.copy()

            scaled[:, :, 0] = (
                scaled[:, :, 0] * 320 // 640
            )

            scaled[:, :, 1] = (
                scaled[:, :, 1] * 240 // 360
            )

            cv2.drawContours(
                self.map,
                [scaled],
                -1,
                255,
                -1
            )

    def get_colormap(self):
        return cv2.applyColorMap(self.map, cv2.COLORMAP_JET)