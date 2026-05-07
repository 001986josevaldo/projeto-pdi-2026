import cv2

class Preprocessing:
    def __init__(self, blur_kernel=(5,5)):
        self.blur_kernel = blur_kernel

    def apply(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, self.blur_kernel, 0)
        return blur

    def to_hsv_mask(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = (0, 0, 0)
        upper = (180, 255, 80)
        mask = cv2.inRange(hsv, lower, upper)
        return mask