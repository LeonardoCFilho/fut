from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

class ValidadorArquivo:
    """
    Responsável por validar a existência de arquivos essenciais do sistema
    """
    
    # Construtor
    def __init__(self):
        pass
    
    
    def validar_arquivos_essenciais(self, path_settings: Path, path_schema_configuracoes: Path, path_schema_yaml: Path):
        """
        Verifica a existência dos arquivos essenciais para o funcionamento do sistema
        
        Args:
            path_settings (Path): Caminho do arquivo settings.ini
            path_schema_configuracoes (Path): Caminho do schema de configurações (opcional)
            path_schema_yaml (Path): Caminho do schema YAML (opcional)
        """
        if not path_settings.exists():
            logger.fatal(f"Arquivo de configurações não encontrado: {path_settings}")
            sys.exit(f"Arquivo de configurações não encontrado: {path_settings}")
        
        
        if path_schema_configuracoes and not path_schema_configuracoes.exists():
            logger.warning(f"Schema de configurações não encontrado: {path_schema_configuracoes}")