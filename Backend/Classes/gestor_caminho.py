from Backend.Classes.controlador_configuracao import ControladorConfiguracao # Usado para encontrar o validator
from Backend.Classes.gerenciador_validator import GerenciadorValidator # Usado para garantir existencia do validator
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

class GestorCaminho:
    """
    Classe que gerencia os endereços usados no projeto e garante a existencia de arquivos vitais
    """

    # Contantes
    SETTINGS_FILE = "settings.ini"
    VALIDATOR_FILE = "validator_cli.jar"
    SCHEMA_FILE_YAML = "schema_arquivo_de_teste.json"
    ARQUIVOS_DIR = "Arquivos"
    TEMP_DIR = ".temp-fut"
    RESULTS_DIR = "resultados-fut"

    # Construtor
    def __init__(self, path_fut: Path, controlador_configuracao: ControladorConfiguracao = None):
        """
        Inicializa o gerenciador do validator a partir de um ConfigManager.

        Args:
            path_fut (Path): O caminho da pasta do projeto
            controlador_configuracao (ControladorConfiguracao): instancia de ControladorConfiguracao que será usado pelo GestorCaminho (opcional)
        
        Raises:
            FileNotFoundError: Se o arquivo validator_cli.jar não for encontrado.
            SystemExit: Arquivos essenciais não foram encontrados
        """
        self.path_fut = path_fut
        self._criar_paths()
        self._inicializar_componentes(controlador_configuracao)
        self._paths = self._criar_dict_paths()


    def return_path(self, path_desejado: str) -> Path:
        """
        Retorna o caminho solicitado a partir do dicionário de paths.

        Args:
            path_desejado (str): Nome do path desejado

        Returns:
            Path: O caminho solicitado

        Raises:
            KeyError: Se o path solicitado não for encontrado
        """
        if path_desejado not in self._paths:
            raise KeyError(f"Path '{path_desejado}' não encontrado, verifique a escrita")
        
        return self._paths[path_desejado]


    def _criar_paths(self):
        """
        Cria todos os caminhos fornecidos por essa classe e garante a existencia dos arquivos
        """
        self.path_arquivos = self.path_fut / self.ARQUIVOS_DIR
        self.path_settings = self.path_arquivos / self.SETTINGS_FILE
        self.path_schema = self.path_arquivos / self.SCHEMA_FILE_YAML
        self._validar_arquivos_essenciais()


    def _validar_arquivos_essenciais(self):
        """
        Verifica a existencia dos arquivos essenciais para o funcionamento do sistema
        """
        if not self.path_settings.exists():
            logger.fatal(f"Arquivo de configurações não encontrado: {self.path_settings}")
            sys.exit(f"Arquivo de configurações não encontrado: {self.path_settings}")
        #...


    def _inicializar_componentes(self, controlador_configuracao: ControladorConfiguracao = None):
        """
        Inicializa componentes que dependem de funções e/ou do settings.ini
        
        Args:
            controlador_configuracao (ControladorConfiguracao): instancia de ControladorConfiguracao que será usado pelo GestorCaminho (opcional)
        
        Raises:
            SystemExit: Erro na inicialização do validator_cli
        """
        try:
            # Usar ou criar o controladorConfiguracao
            if controlador_configuracao is not None:
                self.controlador_configuracao = controlador_configuracao
            else:
                self.controlador_configuracao = ControladorConfiguracao(self.path_settings)
                
            self.path_validator = self._resolve_validator_path()
            self.path_pasta_validator = self._definir_pasta_validator()
        except Exception as e:
            logger.fatal(f"Erro na inicialização: {e}")
            sys.exit(f"Erro na inicialização: {e}")


    def _criar_dict_paths(self) -> dict:
        """
        Cria e retorna um dicionário com todos os paths utilizados pelo sistema.

        Returns:
            dict: Dicionário contendo os paths do sistema
        """
        return {
            'validator': self.path_validator,
            'schema_yaml': self.path_schema,
            'pasta_validator': self.path_pasta_validator,
            'raiz': self.path_fut,
            'settings': self.path_settings,
            'arquivos': self.path_arquivos,
        }


    def _resolve_validator_path(self) -> Path:
        """
        Resolve o caminho do validator_cli.jar, verifica se está instalado,
        tenta instalar se necessário e valida sua versão.

        Returns:
            Path: Path do validator_cli.jar válido.
        
        Raises:
            SystemExit: Se não for possível instalar ou validar o validator_cli.jar.
        """
        logger.debug(f"Resolvendo caminho do validator: path_validator")
        path_validator_str = self.controlador_configuracao.returnValorSettings('caminho_validator')

        if path_validator_str == "reset": # Validator padrão
            path_validator = self.path_arquivos / self.VALIDATOR_FILE
        else: # Validator customizado
            # Caminho salvo no arquivo é sempre absoluto
            path_validator = Path(path_validator_str)
        
        return self._setup_validator(path_validator)


    def _setup_validator(self, path_validator: Path) -> Path:
        """
        Configura e valida o validator_cli, instalando se necessário.

        Args:
            path_validator (Path): Caminho do validator_cli.jar

        Returns:
            Path: Caminho do validator_cli.jar validado

        Raises:
            SystemExit: Se não for possível instalar ou validar o validator_cli
        """
        gerenciador_validator = GerenciadorValidator(path_validator)
        if not path_validator.exists():
            try:
                gerenciador_validator.instalaValidatorCli()
            except Exception as e:
                logger.fatal(f"Erro ao instalar o validator_cli padrão: {e}")
                sys.exit("Erro ao instalar o validator_cli padrão")

        if not gerenciador_validator.verificaVersaoValidator():
            logger.fatal("Validator_cli utilizado não é válido")
            sys.exit("Validator_cli utilizado não é válido")

        logger.debug(f"validator_cli pronto em: {path_validator}")
        return path_validator


    def _definir_pasta_validator(self) -> Path:
        """
        Determinar a pasta que os arquivos do validator serão salvos

        Returns:
            Path: O caminho (Path) da pasta para os arquivos do validator
        """
        flag_salvar_output = self.controlador_configuracao.returnValorSettings('armazenar_saida_validator').lower() in ["true", "1", "yes"]
        if flag_salvar_output:  # Pasta permanente
            pasta_relatorio = Path.cwd() / "resultados-fut"
        else:  # Pasta temporária (Apagada após a criação do relatório final)
            pasta_relatorio = Path.cwd() / ".temp-fut"
        pasta_relatorio.mkdir(exist_ok=True)  # Garantir que a pasta existe
        return pasta_relatorio