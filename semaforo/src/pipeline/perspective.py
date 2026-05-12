import cv2
import numpy as np


class PerspectiveTransformer:

    def __init__(self, src_points, width=600, height=400):

        self.width = width
        self.height = height

        dst_points = np.float32([
            [0, 0],
            [width, 0],
            [0, height],
            [width, height]
        ])

        self.matrix = cv2.getPerspectiveTransform(
            np.float32(src_points),
            dst_points
        )

    def transform(self, frame):

        return cv2.warpPerspective(
            frame,
            self.matrix,
            (self.width, self.height)
        )