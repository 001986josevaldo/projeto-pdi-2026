import cv2
import numpy as np


class Dashboard:

    def build(
        self,
        frame,
        state,
        violations,
        fps,
        logs
    ):

        h, w = frame.shape[:2]

        right_panel = np.zeros((h, 350, 3), dtype=np.uint8)

        # título
        cv2.putText(
            right_panel,
            "SMART CITY PANEL",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

        # estado
        color = (255,255,255)
        bg_color = (50, 50, 50)  # fundo padrão

        if state == "RED":
            color = (0,0,255)
            #bg_color = (0, 0, 120)

        elif state == "GREEN":
            color = (0,255,0)
            #bg_color = (0, 100, 0)


        elif state == "YELLOW":
            color = (0,255,255)
            #bg_color = (0, 100, 100)

        # retângulo de fundo colorido atrás do texto
        cv2.rectangle(right_panel, (10, 78), (340, 115), bg_color, -1)
        
        # "Sinal:" sempre branco
        cv2.putText(
            right_panel,
            "Sinal: ",
            (20, 108),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )
        # somente o estado muda de cor
        cv2.putText(
            right_panel,
            f" {state}",
            (95, 108),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )

        # infrações
        cv2.putText(
            right_panel,
            f"VIOLATIONS: {violations}",
            (20,160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        # FPS
        cv2.putText(
            right_panel,
            f"FPS: {int(fps)}",
            (20,220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,0),
            2
        )

        # logs
        cv2.putText(
            right_panel,
            "LAST EVENTS:",
            (20,300),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,255),
            2
        )

        y = 340

        for log in logs[-5:]:

            cv2.putText(
                right_panel,
                log,
                (20,y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255,255,255),
                1
            )

            y += 30

        return cv2.hconcat([frame, right_panel])
    