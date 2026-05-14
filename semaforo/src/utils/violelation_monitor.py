import cv2
import numpy as np
import csv
import hashlib
import os
from datetime import datetime


class ViolationMonitor:
    """
    Monitora infrações de semáforo vermelho.

    Fluxo:
      1. Ativa subtração de fundo (MOG2) quando state == RED
      2. Detecta veículos cruzando a linha de retenção virtual
      3. Captura frame, borra placas/rostos (LGPD)
      4. Registra em CSV com timestamp, hash e coordenadas
    """

    def __init__(
        self,
        output_dir: str = "violations",
        retention_line_y: int = None,
        csv_path: str = "violations/log.csv",
        min_contour_area: int = 1500,
    ):
        self.output_dir   = output_dir
        self.csv_path     = csv_path
        self.min_area     = min_contour_area
        self.line_y       = retention_line_y   # None = definido no 1º frame

        self._active      = False              # True somente no RED
        self._subtractor  = None
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._violation_count = 0
        self._tracked_ids: dict[int, dict] = {}   # contour_id → estado

        os.makedirs(output_dir, exist_ok=True)
        self._init_csv()

    # ------------------------------------------------------------------ #
    #  API pública                                                         #
    # ------------------------------------------------------------------ #

    def update(self, frame: np.ndarray, state: str) -> dict:
        """
        Chame a cada frame.

        Parâmetros
        ----------
        frame : np.ndarray   BGR frame da câmera
        state : str          "RED" | "GREEN" | "YELLOW" | "UNKNOWN"

        Retorno
        -------
        dict com:
            annotated_frame  : frame BGR com anotações
            violations       : total acumulado de infrações
            new_violation    : True se houve nova infração neste frame
            boxes            : lista de (x,y,w,h) dos veículos detectados
        """
        result = {
            "annotated_frame": frame.copy(),
            "violations":      self._violation_count,
            "new_violation":   False,
            "boxes":           [],
        }

        if state == "RED":
            if not self._active:
                self._activate(frame)
            result = self._process(frame, result)
        else:
            if self._active:
                self._deactivate()

        return result

    @property
    def violation_count(self) -> int:
        return self._violation_count

    # ------------------------------------------------------------------ #
    #  Ativação / desativação                                              #
    # ------------------------------------------------------------------ #

    def _activate(self, frame: np.ndarray):
        self._active     = True
        self._subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=50, detectShadows=True
        )
        # Aquece o modelo com o frame atual
        self._subtractor.apply(frame)

        if self.line_y is None:
            h = frame.shape[0]
            self.line_y = int(h * 0.60)   # 60 % da altura por padrão

    def _deactivate(self):
        self._active      = False
        self._subtractor  = None
        self._tracked_ids.clear()

    # ------------------------------------------------------------------ #
    #  Processamento principal                                             #
    # ------------------------------------------------------------------ #

    def _process(self, frame: np.ndarray, result: dict) -> dict:
        annotated = result["annotated_frame"]
        h, w      = frame.shape[:2]

        # -- linha de retenção virtual ------------------------------------
        cv2.line(annotated, (0, self.line_y), (w, self.line_y), (0, 0, 255), 2)
        cv2.putText(
            annotated, "RETENCAO",
            (10, self.line_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 1
        )

        # -- subtração de fundo -------------------------------------------
        fg_mask = self._subtractor.apply(frame)

        # Remove sombras (valor 127) e ruído
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        kernel    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask   = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN,  kernel)
        fg_mask   = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        # -- contornos / veículos -----------------------------------------
        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = []
        new_violation = False

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            boxes.append((x, y, bw, bh))
            bottom_y = y + bh

            # Verifica cruzamento da linha de retenção
            crossed = bottom_y >= self.line_y

            if crossed:
                # Desenha bounding box vermelha
                cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 0, 255), 2)
                cv2.putText(
                    annotated, "INFRACAO",
                    (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
                )

                # Evita duplicatas: só registra se ainda não foi rastreado
                cid = self._contour_id(x, y, bw, bh)
                if cid not in self._tracked_ids:
                    self._tracked_ids[cid] = {"registered": True}
                    self._register_violation(frame, x, y, bw, bh)
                    new_violation            = True
                    self._violation_count   += 1
            else:
                # Bounding box amarela para veículo em movimento
                cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 255), 1)

        result["annotated_frame"] = annotated
        result["violations"]      = self._violation_count
        result["new_violation"]   = new_violation
        result["boxes"]           = boxes
        return result

    # ------------------------------------------------------------------ #
    #  Registro de infração (captura + LGPD + CSV)                        #
    # ------------------------------------------------------------------ #

    def _register_violation(
        self, frame: np.ndarray,
        x: int, y: int, bw: int, bh: int
    ):
        timestamp  = datetime.now()
        ts_str     = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        coord_str  = f"{x},{y},{bw},{bh}"

        # Anonimiza placa e rosto no frame completo antes de salvar
        anon_frame = self._anonymize(frame.copy())

        img_name   = f"violation_{ts_str}.jpg"
        img_path   = os.path.join(self.output_dir, img_name)
        cv2.imwrite(img_path, anon_frame)

        plate_hash = self._hash_coord(coord_str, ts_str)

        self._write_csv(
            timestamp  = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            event_type = "infracao",
            coord      = coord_str,
            plate_hash = plate_hash,
            img_file   = img_name,
        )

    # ------------------------------------------------------------------ #
    #  LGPD – anonimização                                                 #
    # ------------------------------------------------------------------ #

    def _anonymize(self, frame: np.ndarray) -> np.ndarray:
        """Borra rostos e região de placa (parte inferior dos bounding boxes)."""
        gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces  = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        for (fx, fy, fw, fh) in faces:
            frame = self._blur_region(frame, fx, fy, fw, fh)

        # Borra faixa inferior de cada contorno (região provável de placa)
        fg_mask = self._subtractor.apply(frame, learningRate=0)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        cnts, _   = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for cnt in cnts:
            if cv2.contourArea(cnt) < self.min_area:
                continue
            px, py, pw, ph = cv2.boundingRect(cnt)
            plate_y  = py + int(ph * 0.75)
            plate_h  = int(ph * 0.25)
            frame    = self._blur_region(frame, px, plate_y, pw, plate_h)

        return frame

    @staticmethod
    def _blur_region(
        frame: np.ndarray,
        x: int, y: int, w: int, h: int,
        ksize: int = 31
    ) -> np.ndarray:
        h_f, w_f = frame.shape[:2]
        x1, y1   = max(0, x),     max(0, y)
        x2, y2   = min(w_f, x+w), min(h_f, y+h)
        if x2 <= x1 or y2 <= y1:
            return frame
        roi              = frame[y1:y2, x1:x2]
        frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (ksize, ksize), 0)
        return frame

    # ------------------------------------------------------------------ #
    #  Utilitários                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _contour_id(x: int, y: int, w: int, h: int, grid: int = 40) -> tuple:
        """ID baseado em grade para evitar duplicatas próximas."""
        return (x // grid, y // grid, w // grid, h // grid)

    @staticmethod
    def _hash_coord(coord: str, ts: str) -> str:
        raw = f"{coord}|{ts}".encode()
        return hashlib.sha256(raw).hexdigest()[:12]

    def _init_csv(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["timestamp", "evento", "coordenada", "placa_hash", "imagem"]
                )

    def _write_csv(
        self,
        timestamp: str,
        event_type: str,
        coord: str,
        plate_hash: str,
        img_file: str,
    ):
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                [timestamp, event_type, coord, plate_hash, img_file]
            )