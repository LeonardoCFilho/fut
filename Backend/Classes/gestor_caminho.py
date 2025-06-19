from Backend.Classes.controlador_configuracao import ControladorConfiguracao
from Backend.Classes.validador_arquivo import ValidadorArquivo
from Backend.Classes.configurador_validator import ConfiguradorValidator
from pathlib import Path
import logging
import shutil
import sys

logger = logging.getLogger(__name__)

class GestorCaminho:
    """
    Responsável por gerenciar os caminhos do projeto
    """

    # Constantes
    SETTINGS_FILE = "settings.ini"
    CSV_TESTES = "historico.csv"
    SCHEMA_CONFIGURACOES = "schema_configuracoes.json"
    SCHEMA_FILE_YAML = "schema_arquivo_de_teste.json"
    ARQUIVOS_DIR = "Arquivos"
    PASTA_FRONTEND = "Frontend"
    SCRIPT_FRONTEND = "app.py"
    APP_NAME = "FutApp"

    # Construtor
    def __init__(self, path_fut: Path, controlador_configuracao: ControladorConfiguracao = None):
        """
        Inicializa o gerenciador de caminhos

        Args:
            path_fut (Path): O caminho da pasta do projeto
            controlador_configuracao (ControladorConfiguracao): Instância de ControladorConfiguracao (opcional)
        """
        # Necessidades do executavel
        self.path_fut = path_fut
        self.flag_eh_executavel = getattr(sys, 'frozen', False)
        self._setup_user_data_dir()
        # Necessidades padrão
        self._criar_paths()
        self._criar_venv_path() # Criado por causa do streamlit
        self._copiar_arquivos_padrão() # necessidade do executavel
        self._validar_arquivos()
        self._inicializar_componentes(controlador_configuracao)


    def _setup_user_data_dir(self):
        """Configura o diretório de dados do usuário baseado no OS"""
        if self.flag_eh_executavel:
            if sys.platform == "win32":
                self.user_data_dir = Path.home() / "AppData" / "Local" / self.APP_NAME
            elif sys.platform == "darwin":  # macOS
                self.user_data_dir = Path.home() / "Library" / "Application Support" / self.APP_NAME
            else:  # Linux e outros Unix-like
                self.user_data_dir = Path.home() / f".{self.APP_NAME.lower()}"
            # Criar o diretório se não existir
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.user_data_dir = self.path_fut # Usar o padrão 


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
            'csv': self.path_csv,
            'validator': self.path_validator,
            'schema_configuracoes': self.path_schema_configuracoes,
            'schema_yaml': self.path_schema_yaml,
            'pasta_validator': self.path_pasta_validator,
            'raiz': self.path_fut,
            'settings': self.path_settings,
            'arquivos': self.path_arquivos,
            'script_frontend': self.path_script_frontend,
            'venv': self.path_venv  
        }
        
        if path_desejado not in paths:
            raise KeyError(f"Path '{path_desejado}' não encontrado, verifique a escrita")
        
        return paths[path_desejado]


    def _criar_paths(self):
        """Cria todos os caminhos básicos do projeto"""
        # Diferente por causa do executavel
        self.path_arquivos = self.user_data_dir / self.ARQUIVOS_DIR
        self.path_arquivos.mkdir(exist_ok=True) # desnecessário na execução do .py (mas não causa erro)
        # Arquivos
        self.path_csv = self.path_arquivos / self.CSV_TESTES
        self.path_schema_configuracoes = self.path_arquivos / self.SCHEMA_CONFIGURACOES
        self.path_schema_yaml = self.path_arquivos / self.SCHEMA_FILE_YAML
        self.path_settings = self.path_arquivos / self.SETTINGS_FILE
        # Endereço do nosso streamlit
        self.path_script_frontend = self.path_fut / self.SCRIPT_FRONTEND


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


    def _copiar_arquivos_padrão(self):
        """Copia arquivos padrão para a pasta do usuário se executando como executável"""
        if not self.flag_eh_executavel:
            return
        
        # Lista de arquivos que devem ser copiados se não existirem na pasta do usuário
        default_files = [
            self.SETTINGS_FILE,
            self.SCHEMA_CONFIGURACOES,
            self.SCHEMA_FILE_YAML
        ]
        
        for filename in default_files:
            user_file_path = self.path_arquivos / filename
            
            # Se o arquivo não existe na pasta do usuário, copiar do bundle
            if not user_file_path.exists():
                try:
                    # Tentar encontrar o arquivo no bundle PyInstaller
                    if hasattr(sys, '_MEIPASS'):
                        bundled_file = Path(sys._MEIPASS) / self.ARQUIVOS_DIR / filename
                        if bundled_file.exists():
                            shutil.copy2(bundled_file, user_file_path)
                            logger.info(f"Arquivo padrão copiado: {filename}")
                except Exception as e:
                    logger.warning(f"Não foi possível copiar arquivo padrão {filename}: {e}")