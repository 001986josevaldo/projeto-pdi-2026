import cv2
import numpy as np

import matplotlib.pyplot as plt

# Exemplo de fluxo inicial
img = cv2.imread('/media/josevaldo/E02A-3159/BCC/8_sem/PI/projeto_integrador/projeto-pdi-2026/assets/samples/images/potholes0.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150) # Detecção de Bordas (Canny) exigida [6]



# Converter de BGR para RGB para exibição correta
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Criar uma visualização lado a lado (Original vs Bordas)
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.title('Imagem Original')
plt.imshow(img_rgb)
plt.axis('off')

plt.subplot(1, 2, 2)
plt.title('Bordas (Canny)')
plt.imshow(edges, cmap='gray')
plt.axis('off')

plt.show()