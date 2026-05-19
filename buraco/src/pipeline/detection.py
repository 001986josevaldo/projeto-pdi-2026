import cv2
import numpy as np

class Detection:
    def __init__(self):
        # Kernel maior para fechamento (conectar bordas)
        self.kernel_close = np.ones((5, 5), np.uint8)
        # Kernel menor para abertura (remover ruído pontual)
        self.kernel_open = np.ones((3, 3), np.uint8)

    def edges(self, img):
        """
        Detecção de bordas pelo algoritmo de Canny.
        Limiares 50/150 (razão 1:3).
        Entrada: imagem cinza suavizada (saída de Preprocessing.apply).
        """
        return cv2.Canny(img, 50, 150)

    def clean(self, mask):
        """
        Limpeza morfológica:
        1) Abertura: remove ruído pontual.
        2) Fechamento: conecta bordas fragmentadas.
        """
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  self.kernel_open)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, self.kernel_close)
        return closed

    def contours(self, mask):
        """
        Extrai contornos externos e remove contornos aninhados.

        Processo:
        1) Extrai todos os contornos externos com RETR_EXTERNAL.
        2) Ordena do maior para o menor (por área).
        3) Para cada contorno, verifica se o seu centroide está dentro
           do bounding box de algum contorno maior já aceito.
           - Se estiver → é um buraco dentro de um buraco → descarta.
           - Se não estiver → aceita o contorno.

        Isso evita que a UI mostre um buraco pequeno detectado dentro
        de um buraco grande já anotado.
        """
        raw_contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not raw_contours:
            return []

        # Ordena do maior para o menor por área
        sorted_contours = sorted(
            raw_contours,
            key=cv2.contourArea,
            reverse=True
        )

        accepted = []          # contornos que passaram no filtro
        accepted_rects = []    # bounding boxes dos aceitos (x, y, x2, y2)

        for cnt in sorted_contours:
            # Centroide do contorno atual
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Verifica se o centroide cai dentro de algum bounding box já aceito
            inside = False
            for (rx, ry, rx2, ry2) in accepted_rects:
                if rx <= cx <= rx2 and ry <= cy <= ry2:
                    inside = True
                    break

            if inside:
                continue  # descarta: está dentro de um buraco maior

            # Aceita e registra o bounding box para comparações futuras
            x, y, w, h = cv2.boundingRect(cnt)
            accepted.append(cnt)
            accepted_rects.append((x, y, x + w, y + h))

        return accepted