from Backend.Classes.controlador_configuracao import ControladorConfiguracao
from Backend.Classes.validador_arquivo import ValidadorArquivo
from Backend.Classes.configurador_validator import ConfiguradorValidator
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

class GestorCaminho:
    """
    Responsável por gerenciar os caminhos do projeto
    """

    # Constantes
    SETTINGS_FILE = "settings.ini"
    SCHEMA_CONFIGURACOES = "schema_configuracoes.json"
    SCHEMA_FILE_YAML = "schema_arquivo_de_teste.json"
    ARQUIVOS_DIR = "Arquivos"
    PASTA_FRONTEND = "Frontend"
    SCRIPT_FRONTEND = "app.py"


    def __init__(self, path_fut: Path, controlador_configuracao: ControladorConfiguracao = None):
        """
        Inicializa o gerenciador de caminhos

        Args:
            path_fut (Path): O caminho da pasta do projeto
            controlador_configuracao (ControladorConfiguracao): Instância de ControladorConfiguracao (opcional)
        """
        self.path_fut = path_fut
        self._criar_paths()
        self._criar_venv_path()
        self._validar_arquivos()
        self._inicializar_componentes(controlador_configuracao)


    def return_path(self, path_desejado: str) -> Path:
        """
        Retorna o caminho solicitado

        Args:
            path_desejado (str): Nome do path desejado

        Returns:
            Path: O caminho solicitado

        Raises:
            KeyError: Se o path solicitado não for encontrado
        """
        paths = {
            'validator': self.path_validator,
            'script_frontend': self.path_script_frontend,
            'schema_configuracoes': self.path_schema_configuracoes,
            'schema_yaml': self.path_schema_yaml,
            'pasta_validator': self.path_pasta_validator,
            'raiz': self.path_fut,
            'settings': self.path_settings,
            'arquivos': self.path_arquivos,
            'venv': self.path_venv  
        }
        
        if path_desejado not in paths:
            raise KeyError(f"Path '{path_desejado}' não encontrado, verifique a escrita")
        
        return paths[path_desejado]


    def _criar_paths(self):
        """Cria todos os caminhos básicos do projeto"""
        self.path_arquivos = self.path_fut / self.ARQUIVOS_DIR
        self.path_pasta_frontend = self.path_fut / self.PASTA_FRONTEND
        self.path_settings = self.path_arquivos / self.SETTINGS_FILE
        self.path_schema_configuracoes = self.path_arquivos / self.SCHEMA_CONFIGURACOES
        self.path_schema_yaml = self.path_arquivos / self.SCHEMA_FILE_YAML
        self.path_script_frontend = self.path_pasta_frontend / self.SCRIPT_FRONTEND


    def _criar_venv_path(self):
        """Cria o path para o ambiente virtual de acordo com o OS"""
        if sys.platform == "win32":
            self.path_venv = self.path_fut / "venv-fut" / "Scripts" / "activate.bat"
        else:
            self.path_venv = self.path_fut / "venv-fut" / "bin" / "activate"


    def _validar_arquivos(self):
        """Valida a existência dos arquivos essenciais"""
        validador = ValidadorArquivo()
        validador.validar_arquivos_essenciais(
            self.path_settings,
            self.path_schema_configuracoes,
            self.path_schema_yaml
        )


    def _inicializar_componentes(self, controlador_configuracao: ControladorConfiguracao = None):
        """
        Inicializa componentes que dependem de configurações
        
        Args:
            controlador_configuracao (ControladorConfiguracao): Instância do controlador (opcional)
        """
        # Usar ou criar o controlador de configuração
        if controlador_configuracao is not None:
            self.controlador_configuracao = controlador_configuracao
        else:
            self.controlador_configuracao = ControladorConfiguracao(
                self.path_settings, 
                self.path_schema_configuracoes
            )
        
        # Configurar validator usando o ConfiguradorValidator
        configurador_validator = ConfiguradorValidator(
            self.controlador_configuracao, 
            self.path_arquivos
        )
        self.path_validator = configurador_validator.resolver_caminho_validator()
        self.path_pasta_validator = configurador_validator.definir_pasta_validator()