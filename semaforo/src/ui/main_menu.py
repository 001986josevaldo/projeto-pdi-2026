import cv2
import numpy as np
import sys


class MainMenu:

    def __init__(self):
        self.option = None

    def show(self):

        width  = 700
        height = 400

        def draw_menu(hover=None):
            menu = np.zeros((height, width, 3), dtype=np.uint8)

            cv2.putText(
                menu,
                "SMART TRAFFIC SYSTEM",
                (120, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )

            # botão webcam
            col_webcam = (200, 0, 0) if hover == "webcam" else (255, 0, 0)
            cv2.rectangle(menu, (100, 150), (300, 250), col_webcam, -1)
            cv2.putText(menu, "1 - WEBCAM", (120, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # botão image
            col_image = (0, 200, 200) if hover == "image" else (0, 255, 255)
            cv2.rectangle(menu, (400, 150), (600, 250), col_image, -1)
            cv2.putText(menu, "2 - IMAGE", (440, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            return menu

        hover_state = [None]

        def mouse_callback(event, x, y, flags, param):

            # detecta hover
            over_webcam = 100 <= x <= 300 and 150 <= y <= 250
            over_image  = 400 <= x <= 600 and 150 <= y <= 250

            if event == cv2.EVENT_MOUSEMOVE:
                hover_state[0] = "webcam" if over_webcam else "image" if over_image else None

            elif event == cv2.EVENT_LBUTTONDOWN:
                if over_webcam:
                    self.option = "webcam"
                elif over_image:
                    self.option = "image"

        cv2.namedWindow("Main Menu")
        cv2.setMouseCallback("Main Menu", mouse_callback)

        while True:

            cv2.imshow("Main Menu", draw_menu(hover_state[0]))

            key = cv2.waitKey(1)

            if key == ord('1'):
                self.option = "webcam"

            elif key == ord('2'):
                self.option = "image"

            # fecha pelo X da janela
            if cv2.getWindowProperty("Main Menu", cv2.WND_PROP_VISIBLE) < 1:
                cv2.destroyAllWindows()
                sys.exit(0)

            if self.option is not None:
                break

        cv2.destroyWindow("Main Menu")
        return self.option