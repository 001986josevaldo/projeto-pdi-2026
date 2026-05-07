"""
Script de Download - Traffic Light Detection Dataset
======================================================
Dataset: wjybuqi/traffic-light-detection-dataset
Fonte: Kaggle (via kagglehub)

Requisitos:
    pip install kagglehub

Autenticação Kaggle (escolha uma das opções):
    Opção 1: Arquivo ~/.kaggle/kaggle.json com {"username":"...","key":"..."}
    Opção 2: Variáveis de ambiente KAGGLE_USERNAME e KAGGLE_KEY
    Opção 3: Login interativo via kagglehub.login()
"""

import os
import sys
import logging
from pathlib import Path

# ──────────────────────────────────────────────
# Configuração de logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Verificação de dependências
# ──────────────────────────────────────────────
def check_dependencies() -> None:
    """Verifica se kagglehub está instalado."""
    try:
        import kagglehub  # noqa: F401
        logger.info("✅ kagglehub encontrado.")
    except ImportError:
        logger.error("❌ kagglehub não está instalado.")
        logger.error("   Execute: pip install kagglehub")
        sys.exit(1)


# ──────────────────────────────────────────────
# Verificação de credenciais Kaggle
# ──────────────────────────────────────────────
def check_kaggle_credentials() -> bool:
    """
    Verifica se as credenciais do Kaggle estão configuradas.
    Retorna True se encontradas, False caso contrário.
    """
    # Opção 1: variáveis de ambiente
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        logger.info("✅ Credenciais Kaggle encontradas via variáveis de ambiente.")
        return True

    # Opção 2: arquivo kaggle.json
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        logger.info(f"✅ Credenciais Kaggle encontradas em: {kaggle_json}")
        return True

    logger.warning("⚠️  Credenciais Kaggle não encontradas automaticamente.")
    logger.warning("   Configure via um dos métodos abaixo:")
    logger.warning("   1. Crie ~/.kaggle/kaggle.json com {\"username\":\"...\",\"key\":\"...\"}")
    logger.warning("   2. Exporte KAGGLE_USERNAME e KAGGLE_KEY como variáveis de ambiente")
    logger.warning("   3. Execute kagglehub.login() antes do download")
    return False


# ──────────────────────────────────────────────
# Download do dataset
# ──────────────────────────────────────────────
def download_dataset(
    dataset_handle: str = "wjybuqi/traffic-light-detection-dataset",
    force_download: bool = False,
) -> Path:
    """
    Faz o download do dataset do Kaggle usando kagglehub.

    Parâmetros:
        dataset_handle  : identificador do dataset no Kaggle (<usuario>/<nome>)
        force_download  : se True, baixa novamente mesmo que já exista em cache

    Retorna:
        Path para o diretório local com os arquivos do dataset
    """
    import kagglehub

    logger.info(f"📦 Iniciando download do dataset: {dataset_handle}")
    logger.info("   (O kagglehub faz cache automático — downloads repetidos são rápidos)")

    try:
        path = kagglehub.dataset_download(
            dataset_handle,
            force_download=force_download,
        )
        dataset_path = Path(path)
        logger.info(f"✅ Download concluído!")
        logger.info(f"   📂 Caminho local: {dataset_path}")
        return dataset_path

    except Exception as exc:
        logger.error(f"❌ Falha no download: {exc}")
        logger.error("   Verifique sua conexão e credenciais Kaggle.")
        raise


# ──────────────────────────────────────────────
# Exibição do conteúdo baixado
# ──────────────────────────────────────────────
def list_dataset_contents(dataset_path: Path, max_files: int = 50) -> None:
    """Lista os arquivos e pastas do dataset baixado."""
    logger.info("\n📋 Conteúdo do dataset:")
    logger.info("─" * 60)

    all_items = sorted(dataset_path.rglob("*"))
    files = [p for p in all_items if p.is_file()]
    dirs  = [p for p in all_items if p.is_dir()]

    logger.info(f"   Diretórios : {len(dirs)}")
    logger.info(f"   Arquivos   : {len(files)}")

    # Tamanho total
    total_bytes = sum(f.stat().st_size for f in files)
    total_mb = total_bytes / (1024 ** 2)
    logger.info(f"   Tamanho total: {total_mb:.1f} MB")
    logger.info("─" * 60)

    # Lista até max_files arquivos
    for i, file in enumerate(files[:max_files]):
        rel = file.relative_to(dataset_path)
        size_kb = file.stat().st_size / 1024
        logger.info(f"   {str(rel):<55} {size_kb:>8.1f} KB")

    if len(files) > max_files:
        logger.info(f"   ... e mais {len(files) - max_files} arquivos.")

    logger.info("─" * 60)


# ──────────────────────────────────────────────
# Ponto de entrada
# ──────────────────────────────────────────────
def main() -> None:
    logger.info("=" * 60)
    logger.info("  Traffic Light Detection Dataset — Downloader")
    logger.info("=" * 60)

    # 1. Checar dependências
    check_dependencies()

    # 2. Checar credenciais (aviso apenas; kagglehub pode pedir interativamente)
    check_kaggle_credentials()

    # 3. Fazer o download
    dataset_path = download_dataset(
        dataset_handle="wjybuqi/traffic-light-detection-dataset",
        force_download=False,   # mude para True para forçar re-download
    )

    # 4. Listar conteúdo
    list_dataset_contents(dataset_path)

    logger.info("\n🎉 Pronto! Use o caminho abaixo no seu projeto:")
    logger.info(f"   path = \"{dataset_path}\"")


if __name__ == "__main__":
    main()