import requests
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ArquivoDownloader:
    """Responsável por fazer download de arquivos via URL"""
    
    # Construtor
    def __init__(self, timeout_default: int = 30):
        self.timeout_default = timeout_default
    

    def baixar_arquivo(self, url: str, endereco_arquivo: str, timeout: int = None, max_tentativas: int = 3):
        """
        Faz download de um arquivo a partir de uma URL
        
        Args:
            url (str): URL de download do arquivo
            endereco_arquivo (str): Endereço onde o arquivo será salvo
            timeout (int): Tempo máximo para o download
            max_tentativas (int): Número de tentativas de download
        """
        if not timeout:
            timeout = self.timeout_default
            
        num_tentativas = 0
        while num_tentativas < max_tentativas:
            try:
                logger.info(f"Tentando fazer o download de {endereco_arquivo}")
                response = requests.get(url, stream=True, timeout=timeout)
                response.raise_for_status()

                endereco_arquivo = Path(endereco_arquivo)
                with endereco_arquivo.open("wb") as arquivo_baixado:
                    for chunk in response.iter_content(chunk_size=8192):
                        arquivo_baixado.write(chunk)
                logger.info("Download feito com sucesso")
                return 

            except Exception as e:
                num_tentativas += 1
                if num_tentativas < max_tentativas:
                    logger.warning(f"Erro na tentativa {num_tentativas} de download para {url}")
                    print(f"\rErro na tentativa {num_tentativas} de download, reiniciando...")
                    time.sleep(3)
                else:
                    logger.error(f"Falha ao tentar fazer o download de {url} após {max_tentativas} tentativas. Erro: {str(e)}")
                    raise e