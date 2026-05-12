import os
from PIL import Image

def redimensionar_na_subpasta():
    subpasta = "processadas"
    extensao_final = ".jpg"
    formatos_suportados = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    if not os.path.exists(subpasta):
        os.makedirs(subpasta)

    arquivos = [f for f in os.listdir('.') if f.lower().endswith(formatos_suportados)]
    
    if not arquivos:
        print("Nenhuma imagem encontrada.")
        return

    # --- 1. Calcular a Média ---
    larguras, alturas = [], []
    for arq in arquivos:
        try:
            with Image.open(arq) as img:
                w, h = img.size
                larguras.append(w)
                alturas.append(h)
        except: continue
    
    media_w = int(sum(larguras) / len(larguras))
    media_h = int(sum(alturas) / len(alturas))
    tamanho_alvo = (media_w, media_h)
    
    print(f"Redimensionando para o limite de {media_w}x{media_h}...")

    # --- 2. Redimensionar e Salvar ---
    arquivos.sort()
    for i, nome_antigo in enumerate(arquivos, start=1):
        try:
            with Image.open(nome_antigo) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # O thumbnail reduz a imagem para caber no tamanho_alvo 
                # mantendo a proporção, sem preencher o que sobrar.
                img.thumbnail(tamanho_alvo, Image.Resampling.LANCZOS)
                
                novo_nome = f"{i}{extensao_final}"
                caminho_final = os.path.join(subpasta, novo_nome)
                
                img.save(caminho_final, "JPEG")
                print(f"Redimensionado: {nome_antigo} -> {caminho_final} ({img.size[0]}x{img.size[1]})")
                
        except Exception as e:
            print(f"Erro em {nome_antigo}: {e}")

if __name__ == "__main__":
    redimensionar_na_subpasta()