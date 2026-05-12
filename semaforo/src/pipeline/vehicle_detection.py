import cv2


class VehicleDetection:

    def __init__(self):

        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )

    def detect(self, frame):

        fgmask = self.bg_subtractor.apply(frame)

        _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        vehicles = []

        for cnt in contours:

            area = cv2.contourArea(cnt)

            if area > 1500:

                x, y, w, h = cv2.boundingRect(cnt)

                vehicles.append((x, y, w, h))

        return vehicles, thresh