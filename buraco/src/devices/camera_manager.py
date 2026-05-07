import cv2


class CameraManager:

    def __init__(self, max_search=4):

        self.max_search = max_search

        self.cap = None

        self.sources = []

        self.current_source = None

    # -------------------------------------------------
    # Detecta câmeras disponíveis
    # -------------------------------------------------
    def detect_sources(self):

        self.sources = []

        for index in range(self.max_search):

            cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

            if cap.isOpened():

                ret, frame = cap.read()

                if ret and frame is not None:

                    self.sources.append({
                        'index': index,
                        'name': f'Câmera {index}'
                    })

                cap.release()

        #print(f"Câmeras detectadas: {self.sources}")

        return self.sources

    # -------------------------------------------------
    # Abre câmera
    # -------------------------------------------------
    def open_camera(self, source):

        self.release()

        self.cap = cv2.VideoCapture(
            source['index'],
            cv2.CAP_V4L2
        )

        if not self.cap.isOpened():

            self.cap = None

            return False

        # Configurações
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.current_source = source

        return True

    # -------------------------------------------------
    # Webcam padrão
    # -------------------------------------------------
    def open_default_camera(self):

        self.detect_sources()

        if not self.sources:
            return False

        return self.open_camera(self.sources[0])

    # -------------------------------------------------
    # Alterna câmera
    # -------------------------------------------------
    def switch_camera(self):

        if not self.sources:

            self.detect_sources()

        if not self.sources:
            return False

        if self.current_source is None:

            return self.open_camera(self.sources[0])

        current_index = next(
            (
                i for i, source in enumerate(self.sources)
                if source['index'] == self.current_source['index']
            ),
            0
        )

        next_index = (current_index + 1) % len(self.sources)

        return self.open_camera(self.sources[next_index])

    # -------------------------------------------------
    # Lê frame
    # -------------------------------------------------
    def read(self):

        if self.cap is None:
            return False, None

        return self.cap.read()

    # -------------------------------------------------
    # Verifica status
    # -------------------------------------------------
    def is_opened(self):

        return self.cap is not None and self.cap.isOpened()

    # -------------------------------------------------
    # Libera câmera
    # -------------------------------------------------
    def release(self):

        if self.cap:

            self.cap.release()

            self.cap = None