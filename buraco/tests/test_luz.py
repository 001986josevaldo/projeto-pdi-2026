import cv2
import os

from src.pipeline.pipeline import PotholePipeline


def ajustar_brilho(img, alpha):

    return cv2.convertScaleAbs(img, alpha=alpha, beta=0)


def executar_teste_luz():

    pasta = "tests/images/luz"

    imagens = [
        "normal.jpg",
        "escuro.jpg",
        "claro.jpg"
    ]

    for nome in imagens:

        caminho = os.path.join(pasta, nome)

        img = cv2.imread(caminho)

        if img is None:
            print(f"Erro ao carregar {nome}")
            continue

        pipeline = PotholePipeline(img.shape)

        results, heatmap = pipeline.process(img)

        print(f"\nImagem: {nome}")
        print(f"Buracos detectados: {len(results)}")

        for r in results:
            print(r)

        cv2.imshow(nome, heatmap)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    executar_teste_luz()