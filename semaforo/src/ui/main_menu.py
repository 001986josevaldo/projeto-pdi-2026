import cv2
import numpy as np


class MainMenu:

    def __init__(self):

        self.option = None

    def show(self):

        width = 700
        height = 400

        menu = np.zeros((height, width, 3), dtype=np.uint8)

        cv2.putText(
            menu,
            "SMART TRAFFIC SYSTEM",
            (120, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0,255,0),
            3
        )

        cv2.rectangle(menu, (100,150), (300,250), (255,0,0), -1)

        cv2.putText(
            menu,
            "1 - WEBCAM",
            (120,210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.rectangle(menu, (400,150), (600,250), (0,255,255), -1)

        cv2.putText(
            menu,
            "2 - IMAGE",
            (440,210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,0,0),
            2
        )

        while True:

            cv2.imshow("Main Menu", menu)

            key = cv2.waitKey(1)

            if key == ord('1'):
                self.option = "webcam"
                break

            elif key == ord('2'):
                self.option = "image"
                break

        cv2.destroyWindow("Main Menu")

        return self.option