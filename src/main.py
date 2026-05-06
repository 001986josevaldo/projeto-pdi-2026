import os
import cv2
from src.pipeline.pipeline import PotholePipeline

# pega raiz do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# monta caminho correto
img_path = os.path.join(BASE_DIR, 'assets', 'samples', 'images', 'potholes19.png')

img = cv2.imread(img_path)

# validação obrigatória (evita crash na banca)
if img is None:
    raise FileNotFoundError(f"Imagem não encontrada: {img_path}")

pipeline = PotholePipeline(img.shape)

results, heatmap = pipeline.process(img)

for (x,y,w,h,sev) in results:
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.putText(img, sev, (x,y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

cv2.imshow("Deteccao", img)
cv2.imshow("Heatmap", heatmap)

cv2.waitKey(0)
cv2.destroyAllWindows()