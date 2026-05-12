import cv2


class Anonymizer:

    def blur_region(self, frame, x, y, w, h):

        roi = frame[y:y+h, x:x+w]

        blur = cv2.GaussianBlur(roi, (51, 51), 30)

        frame[y:y+h, x:x+w] = blur

        return frame