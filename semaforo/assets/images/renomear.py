#!/usr/bin/env python3
"""
Script para renomear imagens em ordem numérica no diretório atual.
Suporta formatos comuns: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
"""

import os
import glob
from pathlib import Path

def renomear_imagens(prefixo="imagem", extensao=None, manter_extensao=True, inicio=1):
    """
    Renomeia todas as imagens no diretório atual para ordem numérica.
    
    Args:
        prefixo: Prefixo para os novos nomes (ex: "foto", "img", "2025")
        extensao: Se especificado, filtra por extensão (ex: ".jpg")
        manter_extensao: Mantém a extensão original do arquivo
        inicio: Número inicial para começar a contagem
    """
    
    # Extensões de imagem suportadas
    extensoes_imagem = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.JPG', '.JPEG', '.PNG']
    
    # Coleta todas as imagens do diretório atual
    imagens = []
    
    if extensao:
        # Se uma extensão específica foi fornecida
        extensao = extensao if extensao.startswith('.') else f'.{extensao}'
        imagens = glob.glob(f"*{extensao}")
    else:
        # Procura por todas as extensões de imagem
        for ext in extensoes_imagem:
            imagens.extend(glob.glob(f"*{ext}"))
    
    # Ordena as imagens alfabeticamente
    imagens.sort()
    
    if not imagens:
        print("❌ Nenhuma imagem encontrada no diretório atual!")
        return
    
    print(f"📷 Encontradas {len(imagens)} imagens:")
    for img in imagens:
        print(f"   - {img}")
    
    print("\n⚠️  Preparando para renomear...")
    resposta = input(f"Deseja continuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("❌ Operação cancelada.")
        return
    
    # Renomeia as imagens
    arquivos_renomeados = []
    
    for i, arquivo_antigo in enumerate(imagens, start=inicio):
        # Obtém a extensão do arquivo antigo
        if manter_extensao:
            extensao_arquivo = Path(arquivo_antigo).suffix
        else:
            # Se não manter a extensão, usa uma padrão ou a especificada
            extensao_arquivo = extensao if extensao else Path(arquivo_antigo).suffix
        
        # Cria o novo nome
        novo_nome = f"{prefixo}_{i:03d}{extensao_arquivo}"
        
        # Verifica se o arquivo já existe
        if os.path.exists(novo_nome):
            print(f"⚠️  Aviso: {novo_nome} já existe! Pulando...")
            continue
        
        # Renomeia o arquivo
        try:
            os.rename(arquivo_antigo, novo_nome)
            arquivos_renomeados.append((arquivo_antigo, novo_nome))
            print(f"✅ {arquivo_antigo} → {novo_nome}")
        except Exception as e:
            print(f"❌ Erro ao renomear {arquivo_antigo}: {e}")
    
    # Resumo final
    print(f"\n{'='*50}")
    print(f"📊 Resumo: {len(arquivos_renomeados)} de {len(imagens)} imagens renomeadas com sucesso!")
    
    return arquivos_renomeados

def renomear_por_data(prefixo="imagem"):
    """
    Renomeia imagens baseado na data de modificação (ordem cronológica)
    """
    import time
    
    # Extensões de imagem suportadas
    extensoes_imagem = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.JPG', '.JPEG', '.PNG']
    
    # Coleta imagens com timestamp
    imagens_com_data = []
    
    for ext in extensoes_imagem:
        for arquivo in glob.glob(f"*{ext}"):
            if os.path.isfile(arquivo):
                mtime = os.path.getmtime(arquivo)
                imagens_com_data.append((arquivo, mtime))
    
    # Ordena por data de modificação
    imagens_com_data.sort(key=lambda x: x[1])
    imagens = [img[0] for img in imagens_com_data]
    
    if not imagens:
        print("❌ Nenhuma imagem encontrada!")
        return
    
    print(f"📷 {len(imagens)} imagens serão renomeadas por data de modificação")
    
    for i, arquivo_antigo in enumerate(imagens, start=1):
        extensao = Path(arquivo_antigo).suffix
        novo_nome = f"{prefixo}_{i:03d}{extensao}"
        
        if os.path.exists(novo_nome):
            continue
            
        os.rename(arquivo_antigo, novo_nome)
        print(f"✅ {arquivo_antigo} → {novo_nome}")

def desfazer_renomeacao():
    """
    Tenta desfazer a última renomeação (nomes no padrão prefixo_NNN.ext)
    """
    import re
    
    # Procura arquivos com padrão de numeração
    padrao = re.compile(r'^(.+)_\d{3}\.(.+)$')
    arquivos_renomeados = []
    
    for arquivo in os.listdir('.'):
        match = padrao.match(arquivo)
        if match and os.path.isfile(arquivo):
            arquivos_renomeados.append(arquivo)
    
    if not arquivos_renomeados:
        print("❌ Nenhum arquivo com padrão de renomeação encontrado!")
        return
    
    print("⚠️  Esta operação NÃO pode ser desfeita completamente!")
    resposta = input("Tem certeza que deseja tentar desfazer? (s/N): ").strip().lower()
    
    if resposta != 's':
        return
    
    print("⚠️  Atenção: Só é possível desfazer se você lembrar os nomes originais.")
    print("Esta funcionalidade é limitada. Recomenda-se fazer backup antes de renomear.")

def main():
    """
    Função principal com menu interativo
    """
    print("="*50)
    print("📸 RENOMEADOR DE IMAGENS")
    print("="*50)
    print("Diretório atual:", os.getcwd())
    print("\nOpções:")
    print("1. Renomear todas as imagens (ordem alfabética)")
    print("2. Renomear por data de modificação")
    print("3. Renomear apenas um tipo específico (ex: .jpg)")
    print("4. Ajuda")
    print("5. Sair")
    
    opcao = input("\nEscolha uma opção (1-5): ").strip()
    
    if opcao == "1":
        prefixo = input("Prefixo para as imagens (padrão: imagem): ").strip() or "imagem"
        inicio = int(input("Número inicial (padrão: 1): ").strip() or 1)
        renomear_imagens(prefixo=prefixo, inicio=inicio)
        
    elif opcao == "2":
        prefixo = input("Prefixo para as imagens (padrão: imagem): ").strip() or "imagem"
        renomear_por_data(prefixo=prefixo)
        
    elif opcao == "3":
        ext = input("Extensão para filtrar (ex: jpg, png): ").strip()
        prefixo = input("Prefixo (padrão: imagem): ").strip() or "imagem"
        renomear_imagens(prefixo=prefixo, extensao=ext)
        
    elif opcao == "4":
        print("\n📖 AJUDA:")
        print("- O script renomeia arquivos com extensões de imagem comuns")
        print("- Os novos nomes seguem o padrão: PREFIXO_NNN.ext")
        print("- NNN é um número com 3 dígitos (001, 002, ...)")
        print("- É recomendado fazer backup antes de renomear!")
        print("- Para cancelar, pressione Ctrl+C")
        
    elif opcao == "5":
        print("👋 Saindo...")
        
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()