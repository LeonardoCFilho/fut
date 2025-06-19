from Backend.Classes.controlador_configuracao import ControladorConfiguracao
from Backend.Classes.gerenciador_validator import GerenciadorValidator
from Backend.Classes.arquivo_downloader import ArquivoDownloader
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

class ConfiguradorValidator:
    """
    Responsável por configurar e gerenciar o validator_cli
    """
    
    # Constantes
    VALIDATOR_FILE = "validator_cli.jar"
    TEMP_DIR = ".temp-fut"
    RESULTS_DIR = "resultados-fut"
    
    # Construtor
    def __init__(self, controlador_configuracao: ControladorConfiguracao, path_arquivos: Path):
        """
        Inicializa o configurador do validator
        
        Args:
            controlador_configuracao (ControladorConfiguracao): Instância do controlador de configuração
            path_arquivos (Path): Caminho da pasta de arquivos
        """
        self.controlador_configuracao = controlador_configuracao
        self.path_arquivos = path_arquivos
    

    def resolver_caminho_validator(self) -> Path:
        """
        Resolve o caminho do validator_cli.jar e configura o GerenciadorValidator

        Returns:
            Path: Path do validator_cli.jar válido.
        
        Raises:
            SystemExit: Se não for possível configurar o validator_cli.jar.
        """
        logger.debug("Resolvendo caminho do validator")
        
        path_validator_str = self.controlador_configuracao.obter_configuracao_segura('caminho_validator', "default")

        if path_validator_str == "default":
            path_validator = self.path_arquivos / self.VALIDATOR_FILE
        else:
            path_validator = Path(path_validator_str)
            if not path_validator.is_absolute():
                path_validator = Path.cwd() / path_validator
        
        return self._configurar_validator(path_validator)
    

    def definir_pasta_validator(self) -> Path:
        """
        Determina a pasta onde os arquivos do validator serão salvos

        Returns:
            Path: O caminho da pasta para os arquivos do validator
        """
        flag_salvar_output = self.controlador_configuracao.obter_configuracao_segura('armazenar_saida_validator', False)

        if flag_salvar_output:
            pasta_relatorio = Path.cwd() / self.RESULTS_DIR
            logger.debug("Usando pasta permanente para resultados do validator")
        else:
            pasta_relatorio = Path.cwd() / self.TEMP_DIR
            logger.debug("Usando pasta temporária para resultados do validator")
            
        pasta_relatorio.mkdir(exist_ok=True)
        return pasta_relatorio
    
    
    def _configurar_validator(self, path_validator: Path) -> Path:
        """
        Configura o validator_cli usando GerenciadorValidator

        Args:
            path_validator (Path): Caminho do validator_cli.jar

        Returns:
            Path: Caminho do validator_cli.jar configurado

        Raises:
            SystemExit: Se não for possível configurar o validator_cli
        """
        try:
            gerenciador_validator = GerenciadorValidator(path_validator)
            
            # Usar a funcionalidade segura do GerenciadorValidator
            timeout = self.controlador_configuracao.obter_configuracao_segura('requests_timeout', 300)
            downloader = ArquivoDownloader(timeout)
            
            if not gerenciador_validator.atualizar_validator_cli_seguro(timeout, downloader):
                logger.fatal("Erro ao configurar o validator_cli")
                sys.exit("Erro ao configurar o validator_cli")
            
            # Verificar se o validator está funcional
            versao = GerenciadorValidator.verificar_versao_validator(path_validator)
            if not versao:
                logger.fatal("Validator_cli configurado não é válido")
                sys.exit("Validator_cli configurado não é válido")
            
            logger.debug(f"validator_cli configurado com versão {versao} em: {path_validator}")
            return path_validator
            
        except Exception as e:
            logger.fatal(f"Erro ao configurar validator_cli: {e}")
            sys.exit(f"Erro ao configurar validator_cli: {e}")

