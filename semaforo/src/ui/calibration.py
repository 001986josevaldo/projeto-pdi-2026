import cv2
import numpy as np


class Calibration:

    def __init__(self):

        self.points = []

    def select_traffic_roi(self, frame):

        roi = cv2.selectROI(
            "Selecione ROI Semaforo",
            frame,
            showCrosshair=True
        )

        cv2.destroyWindow("Selecione ROI Semaforo")

        return roi

    def select_retention_line(self, frame):

        clone = frame.copy()

        points = []

        def mouse(event, x, y, flags, param):

            if event == cv2.EVENT_LBUTTONDOWN:

                points.append((x,y))

                cv2.circle(clone, (x,y), 5, (0,0,255), -1)

                if len(points) == 2:

                    cv2.line(
                        clone,
                        points[0],
                        points[1],
                        (255,0,0),
                        2
                    )

        cv2.namedWindow("Linha Retencao")

        cv2.setMouseCallback("Linha Retencao", mouse)

        while True:

            cv2.imshow("Linha Retencao", clone)

            key = cv2.waitKey(1)

            if key == 13 and len(points) == 2:
                break

        cv2.destroyWindow("Linha Retencao")

        return points

    def select_perspective_points(self, frame):

        clone = frame.copy()

        points = []

        def mouse(event, x, y, flags, param):

            if event == cv2.EVENT_LBUTTONDOWN:

                points.append((x,y))

                cv2.circle(clone, (x,y), 5, (0,255,0), -1)

        cv2.namedWindow("Bird Eye Calibration")

        cv2.setMouseCallback(
            "Bird Eye Calibration",
            mouse
        )

        while True:

            cv2.imshow(
                "Bird Eye Calibration",
                clone
            )

            key = cv2.waitKey(1)

            if key == 13 and len(points) == 4:
                break

        cv2.destroyWindow(
            "Bird Eye Calibration"
        )

        return np.float32(points)