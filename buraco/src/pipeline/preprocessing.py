import cv2

class Preprocessing:
    def __init__(self, blur_kernel=(5,5)):
        self.blur_kernel = blur_kernel

    def apply(self, img):

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Equalização melhora robustez à luz
        equalized = cv2.equalizeHist(gray)

        blur = cv2.GaussianBlur(equalized, self.blur_kernel, 0)

        return blur

    def to_hsv_mask(self, img):

        _, mask = cv2.threshold(
            img,
            70,
            255,
            cv2.THRESH_BINARY_INV
        )

        return mask