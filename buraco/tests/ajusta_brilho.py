import cv2
import os


def ajustar_brilho(imagem, alpha, beta=0):
    """
    alpha > 1  -> mais clara
    alpha < 1  -> mais escura
    """

    return cv2.convertScaleAbs(imagem, alpha=alpha, beta=beta)


def gerar_variacoes_luz(caminho_imagem):

    img = cv2.imread(caminho_imagem)

    if img is None:
        print("Erro ao carregar imagem")
        return

    # Cria pasta de saída
    output_dir = "tests/images/luz"
    os.makedirs(output_dir, exist_ok=True)

    # Imagem original
    normal_path = os.path.join(output_dir, "normal.jpg")
    cv2.imwrite(normal_path, img)

    # Imagem mais escura
    img_escura = ajustar_brilho(img, alpha=0.5)

    escuro_path = os.path.join(output_dir, "escuro.jpg")
    cv2.imwrite(escuro_path, img_escura)

    # Imagem mais clara
    img_clara = ajustar_brilho(img, alpha=1.5)

    claro_path = os.path.join(output_dir, "claro.jpg")
    cv2.imwrite(claro_path, img_clara)

    print("Imagens geradas com sucesso:")
    print(normal_path)
    print(escuro_path)
    print(claro_path)

    # Visualização opcional
    cv2.imshow("Original", img)
    cv2.imshow("Escura", img_escura)
    cv2.imshow("Clara", img_clara)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":

    gerar_variacoes_luz("/media/josevaldo/E02A-3159/BCC/8_sem/PI/projeto_integrador/projeto-pdi-2026/buraco/assets/samples/images/test/potholes30.png")
    