import cv2

from semaforo.src.pipeline.traffic_light import TrafficLightDetector
from semaforo.src.pipeline.vehicle_detection import VehicleDetection
from semaforo.src.pipeline.violation import ViolationDetector
from semaforo.src.pipeline.anonymizer import Anonymizer
from semaforo.src.utils.logger import EventLogger


class TrafficPipeline:

    def __init__(self, roi_light, line_y):

        self.light_detector = TrafficLightDetector(roi_light)

        self.vehicle_detector = VehicleDetection()

        self.violation_detector = ViolationDetector(line_y)

        self.anonymizer = Anonymizer()

        self.logger = EventLogger()

    def process(self, frame):

        state = self.light_detector.detect_state(frame)

        vehicles, mask = self.vehicle_detector.detect(frame)

        violations = self.violation_detector.check_violation(
            vehicles,
            state
        )

        for (x, y, w, h) in vehicles:

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        for (x, y, w, h) in violations:

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 3)

            self.logger.log(
                "infracao",
                state,
                (x, y)
            )

            frame = self.anonymizer.blur_region(
                frame,
                x,
                y,
                w,
                h
            )

        cv2.putText(
            frame,
            f"Estado: {state}",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Infracoes: {self.violation_detector.total_violations}",
            (20,80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,255),
            2
        )

        return frame, mask