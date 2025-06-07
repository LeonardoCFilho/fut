from Backend.Classes.controlador_configuracao import ControladorConfiguracao # Usado para encontrar o validator
from Backend.Classes.gerenciador_validator import GerenciadorValidator # Usado para garantir existencia do validator
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

class GestorCaminho:
    # Construtor
    def __init__(self, pathFut:Path):
        """
        Inicializa o gerenciador do validator a partir de um ConfigManager.

        Args:
            pathFut (Path): O caminho da pasta do projeto
        
        Raises:
            FileNotFoundError: Se o arquivo validator_cli.jar ou settings.ini não forem encontrados.
        """
        ## Diretorio principal
        self.pathFut = pathFut

        ## Arquivos
        self.pathSettings = pathFut / "Arquivos" / "settings.ini"
        if not self.pathSettings.exists():
            sys.exit("Arquivo de configuraões não encontrado, verifique se ele não foi renomeado ou movido!")
        
        ### Usado para as funções
        self.controladorConfiguracao = ControladorConfiguracao(self.pathSettings)

        self.pathValidator = self._resolveValidatorPath()

        self.pathSchema = pathFut / "Arquivos" / "schema_arquivo_de_teste.json"

        ## Pastas
        self.pathDirTestes = pathFut / "Arquivos" / "Testes"

        self.pathPastaValidator = self._definirPastaValidator()

        

    def _resolveValidatorPath(self) -> Path:
        """
        Resolve o caminho do validator_cli.jar, verifica se está instalado,
        tenta instalar se necessário e valida sua versão.

        Returns:
            Path: Path do validator_cli.jar válido.
        
        Raises:
            SystemExit: Se não for possível instalar ou validar o validator_cli.jar.
        """
        logger.debug(f"Resolvendo caminho do validator: pathValidator")
        pathValidatorStr = str(self.controladorConfiguracao.returnValorSettings('caminho_validator')).split('#')[0].strip()

        if pathValidatorStr == "reset": # Validator padrão
            pathValidator = self.pathFut / "Arquivos" / "validator_cli.jar"
        else: # Validator customizado
            # Caminho salvo no arquivo é sempre absoluto
            pathValidator = Path(pathValidatorStr)

        _instanciaGerenciadorValidator = GerenciadorValidator(pathValidator)
        if not pathValidator.exists():
            try:
                _instanciaGerenciadorValidator.instalaValidatorCli()
            except Exception:
                logger.fatal("Erro ao instalar o validator_cli padrão")
                sys.exit("Erro ao instalar o validator_cli padrão")

        if not _instanciaGerenciadorValidator.verificaVersaoValidator():
            logger.fatal("Validator_cli utilizado não é válido")
            sys.exit("Validator_cli utilizado não é válido")

        return pathValidator


    def _definirPastaValidator(self) -> Path:
        """
        Determinar a pasta que os arquivos do validator serão salvos

        Returns:
            O caminho (Path) da pasta para os arquivos do validator
        """
        flagSalvarOutput = self.controladorConfiguracao.returnValorSettings('armazenar_saida_validator').lower() in ["true", "1", "yes"]
        if flagSalvarOutput:  # Pasta permanente
            pastaRelatorio = Path.cwd() / "resultados-fut"
        else:  # Pasta temporária (Apagada após a criação do relatório final)
            pastaRelatorio = Path.cwd() / ".temp-fut"
        pastaRelatorio.mkdir(exist_ok=True)  # Garantir que a pasta existe
        return pastaRelatorio