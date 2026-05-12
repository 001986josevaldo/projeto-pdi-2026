import os

def organizar_e_padronizar():
    # Defina aqui a extensão que você deseja para TODOS os arquivos
    extensao_final = ".jpg" 
    
    # Extensões que o script vai procurar para renomear
    formatos_suportados = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    
    # Lista e ordena os arquivos
    arquivos = [f for f in os.listdir('.') if f.lower().endswith(formatos_suportados)]
    arquivos.sort()

    if not arquivos:
        print("Nenhuma imagem encontrada.")
        return

    for i, nome_antigo in enumerate(arquivos, start=1):
        # Cria o novo nome com a extensão fixa
        novo_nome = f"{i}{extensao_final}"
        
        try:
            os.rename(nome_antigo, novo_nome)
            print(f"Sucesso: {nome_antigo} -> {novo_nome}")
        except Exception as e:
            print(f"Erro ao processar {nome_antigo}: {e}")

    print(f"\nFeito! Todas as imagens agora são {extensao_final}")

if __name__ == "__main__":
    organizar_e_padronizar()