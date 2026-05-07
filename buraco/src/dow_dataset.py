import os
import shutil
import kagglehub

# Diretório base do projeto (volta de src → raiz)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Caminho de destino desejado
DEST_DIR = os.path.join(BASE_DIR, 'assets', 'samples')

# Cria a pasta se não existir
os.makedirs(DEST_DIR, exist_ok=True)

# Faz o download do dataset
path = kagglehub.dataset_download("andrewmvd/pothole-detection")

print("Download feito em:", path)

# Move os arquivos para /assets/samples
for item in os.listdir(path):
    origem = os.path.join(path, item)
    destino = os.path.join(DEST_DIR, item)

    # Evita sobrescrever
    if not os.path.exists(destino):
        shutil.move(origem, destino)

print("Arquivos movidos para:", DEST_DIR)