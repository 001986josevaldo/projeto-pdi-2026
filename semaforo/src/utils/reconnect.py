import cv2
import time


class CameraReconnect:

    def connect_camera(self, index=0):

        while True:

            cap = cv2.VideoCapture(index)

            if cap.isOpened():

                print("Camera conectada.")

                return cap

            print("Tentando reconectar camera...")

            time.sleep(2)