from Backend.Classes.arquivo_downloader import ArquivoDownloader
from pathlib import Path
import platform
import tarfile
import zipfile
import time
import sys
import re
import logging

logger = logging.getLogger(__name__)

class GerenciadorJava:
    """ 
    Classe responsavel pelo teste e download de uma instancia do JDK
    """
    MAXIMO_TENTATIVAS_PADRAO = 3
    TEMPO_ESPERA_TENTATIVA = 300  # segundos
    
    # Construtor
    def __init__(self, path_arquivos: Path):
        self.path_arquivos = path_arquivos
    
    def _criar_java_path(self):
        """ 
        Cria o caminho do arquivo java comprimido de acordo com o sistema operacional
        """
        
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            java_file = "jdk-windows.zip"
        elif sistema == 'darwin':  # macOS
            java_file = "jdk-macos.tar.gz"
        else:  # Linux
            java_file = "jdk-linux.tar.gz"
        
        self.path_java_compresso =  self.path_arquivos / java_file


    def java_instalado(self) -> bool:
        """
        Baixa o arquivo Java se não existir
        """
        
        self._criar_java_path()
        
        if self.path_java_compresso.exists():
            logger.info("Java ja instalado")
            return True
        
        print("\rFazendo instação inicial do java")
        
        # URLs para download do JDK
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.2%2B13/OpenJDK21U-jdk_x64_windows_hotspot_21.0.2_13.zip"
        elif sistema == 'darwin':  # macOS
            url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.2%2B13/OpenJDK21U-jdk_x64_mac_hotspot_21.0.2_13.tar.gz"
        else:  # Linux
            url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.2%2B13/OpenJDK21U-jdk_x64_linux_hotspot_21.0.2_13.tar.gz"
        
        logger.info(f"Baixando java usando {url}")
        try:
            downloader = ArquivoDownloader(self.TEMPO_ESPERA_TENTATIVA)
            downloader.baixar_arquivo(url, self.path_java_compresso)
            return True
        except Exception as e:
            logger.error(f"Erro ao instalar o java: {e}")
            return False
        
        
    def extrair_java(self):
        """
        Extrai o arquivo Java comprimido
        """
        
        if not hasattr(self, 'path_java_compresso'):
            self._criar_java_path()
        
        if not self.path_java_compresso.exists():
            logger.error("Arquivo Java não encontrado para extração")
            return False
        
        # Diretório de destino (mesmo diretório do arquivo)
        destino = self.path_java_compresso.parent
        
        try:
            sistema = platform.system().lower()
            
            if sistema == 'windows':
                # Extrai arquivo ZIP
                logger.info(f"Extraindo arquivo ZIP: {self.path_java_compresso}")
                with zipfile.ZipFile(self.path_java_compresso, 'r') as zip_ref:
                    zip_ref.extractall(destino)
            else:
                # Extrai arquivo TAR.GZ (Linux/macOS)
                logger.info(f"Extraindo arquivo TAR.GZ: {self.path_java_compresso}")
                with tarfile.open(self.path_java_compresso, 'r:gz') as tar_ref:
                    tar_ref.extractall(destino)
            
            logger.info("Java extraído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao extrair Java: {e}")
            return False

    def obter_java_executavel(self) -> Path|None:
        """
        Retorna o caminho para o executável Java extraído
        """
        if not hasattr(self, 'path_java_compresso'):
            self._criar_java_path()
        
        destino = self.path_arquivos
        sistema = platform.system().lower()
        
        # Procura pela pasta extraída
        if sistema == 'windows':
            # Procura por pastas que começam com 'jdk'
            for pasta in destino.glob('jdk*'):
                if pasta.is_dir():
                    java_exe = pasta / 'bin' / 'java.exe'
                    if java_exe.exists():
                        return java_exe
        else:
            # Linux/macOS
            for pasta in destino.glob('jdk*'):
                if pasta.is_dir():
                    if sistema == 'darwin':  # macOS
                        java_exe = pasta / 'Contents' / 'Home' / 'bin' / 'java'
                    else:  # Linux
                        java_exe = pasta / 'bin' / 'java'
                    
                    if java_exe.exists():
                        return java_exe
        
        logger.error("Executável Java não encontrado após extração")
        return None