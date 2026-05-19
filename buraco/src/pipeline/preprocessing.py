import cv2
import numpy as np

class Preprocessing:
    def __init__(self, blur_kernel=(5, 5)):
        self.blur_kernel = blur_kernel

    def apply(self, img):
        """
        Pré-processamento para Canny:
        - Converte para escala de cinza
        - Blur gaussiano para reduzir ruído de alta frequência
        """
        if len(img.shape) == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        blur = cv2.GaussianBlur(gray, self.blur_kernel, 0)
        return blur

    def to_hsv_mask(self, img):
        """
        Gera máscara binária de regiões escuras (asfalto degradado/buracos).

        Usa limiar de Otsu com teto máximo (110) para não confundir sombras
        com buracos reais.

        IMPORTANTE — prevenção de buracos dentro de buracos:
        Aplica MORPH_CLOSE com kernel grande (11x11) para fechar os furos
        internos da máscara ANTES de chegar na detecção de contornos.
        Sem isso, regiões claras dentro de um buraco geram contornos
        "filhos" que parecem buracos menores separados.
        """
        if len(img.shape) == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Limiar automático por Otsu, com teto máximo para regiões escuras
        otsu_thresh, _ = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        thr = min(otsu_thresh, 110)

        # Máscara binária invertida: escuro (buraco) → branco (255)
        _, mask = cv2.threshold(gray, thr, 255, cv2.THRESH_BINARY_INV)

        # Fecha furos internos da máscara com kernel grande
        # Sem isso, texturas claras dentro do buraco criam sub-contornos
        kernel_fill = np.ones((11, 11), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_fill)

        return mask