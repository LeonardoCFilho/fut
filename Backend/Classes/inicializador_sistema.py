from pathlib import Path
import sys
import logging
logger = logging.getLogger(__name__)

class InicializadorSistema:
    # Construtor
    def __init__(self, pathFut):
        # Caminho para o nosso projeto
        if not isinstance(pathFut,Path):
            pathFut = Path(pathFut)  
        self.pathFut = pathFut

        # Caminho para o arquivo de configuracoes
        self.pathSettings = self.pathFut / "Arquivos" / "settings.ini"
        # Caso de erro
        if not self.pathSettings.exists():
            raise FileNotFoundError("settings.ini")
        
        # Caminho para o validator
        self.pathValidator = self._resolveValidatorPath()
        if not self.pathValidator.exists():
            raise FileNotFoundError("validator_cli.jar")


    def returnValorSettings(self, settingsBuscada:str):
        """
        Busca o valor de uma configuração na settings.ini

        Args:
            settingsBuscada (str): Nome da configuração a ser buscada
        
        Returns:
            Valor da configuração ou None(caso de erro)
        """
        # Ler o arquivo de configuracoes
        import configparser
        settings = configparser.ConfigParser()
        settings.read(self.pathSettings)
        settingsBuscada = str(settingsBuscada).lower()

        # Buscar a configuração requisitada
        for secao in settings.sections():
            if settingsBuscada in settings[secao]:
                return settings[secao][settingsBuscada]
        
        # Caso de erro (configuração não foi encontrada)
        return None


    def alterarValorSetting(self, configuracaoSerAlterada:str, novoValor:str):
        """
        Altera o valor de uma configuração na settings.ini

        Args:
            configuracaoSerAlterada (str): Nome da configuração a ser alterada
            novoValor (str): Novo valor para a configuração
        
        Returns:
            booleano informando se a configuração foi alterada ou não
        
        Raises:
            ValueError: novoValor é incompatível com o tipo de configuracaoSerAlterada
        """
        # Por segurança, adicionar previsibilidade extra
        novoValor = str(novoValor).lower()
        configuracaoSerAlterada = configuracaoSerAlterada.lower()
        # Possiveis configurações
        dictConfiguracoes = {
            "timeout": int,
            "max_threads": int,
            "caminho_validator": str,
        }
        listaConfiguracoesBool = [
            "armazenar_saida_validator",
        ]

        # Flag para alterar (ou não) o valor em settings.ini
        flagAlteracaoValida = False

        # caminho_validator tem tratamento especial (existencia ou não do arquivo)
        if configuracaoSerAlterada == "caminho_validator":
            if novoValor != "reset":
                caminhoArquivo = Path(novoValor)
                if not caminhoArquivo.is_absolute():
                    caminhoArquivo = Path.cwd() / caminhoArquivo
                if not caminhoArquivo.exists():
                    raise FileNotFoundError(f"Novo validator_cli não foi encontrado, endereço usado: {caminhoArquivo.resolve()}")
                #print(novoValor)
            else:
                novoValor = Path("Backend/validator_cli.jar").as_posix()
            flagAlteracaoValida = True

        # Checar se a configuração é válida, se não tentar alterar
        if configuracaoSerAlterada in dictConfiguracoes:
            tipoConfiguracao = dictConfiguracoes[configuracaoSerAlterada]
            #print(f"Configuração: {configuracaoSerAlterada}, Valor Novo: {novoValor}, Tipo Esperado: {tipoConfiguracao}") # debug
            if not isinstance(novoValor, dictConfiguracoes[configuracaoSerAlterada]):
                try:
                    #print("editandoTiṕo:"+novoValor)
                    novoValor = tipoConfiguracao(novoValor)
                    flagAlteracaoValida = True
                except ValueError:
                    raise ValueError(f"Novo valor para configuração inválido! Essa configuração é do tipo {tipoConfiguracao.__name__}.")
        
        # Configuração booleana tem tratamento especial
        if configuracaoSerAlterada in listaConfiguracoesBool:
            if novoValor in ["true", "1", "yes", "sim"]:
                novoValor = "True"
            else:
                novoValor = "False"
            flagAlteracaoValida = True
        
        # Adicionando alguns tratamentos especiais:
        # Tempo baixo demais
        if configuracaoSerAlterada == 'timeout':
            if novoValor < 15:
                flagAlteracaoValida = False
                raise ValueError("A configuração de timeout necessita de pelo menos 15 segundos para garantir execução.")
        # Número de threads tem que ser natural*
        if configuracaoSerAlterada == "max_threads":
            if novoValor < 1: 
                flagAlteracaoValida = False
                raise ValueError("O número de máximo de threads tem que ser maior que 0!")

        # Ler o arquivo de configuracoes
        import configparser
        settings = configparser.ConfigParser()
        settings.read(self.pathSettings)

        # Buscar a configuração requisitada (se válido)
        if flagAlteracaoValida:
            for secao in settings.sections():
                if configuracaoSerAlterada in settings[secao]:
                    settings[secao][configuracaoSerAlterada] = str(novoValor)
                    logger.info(f"Valor da configuração '{configuracaoSerAlterada}' foi alterado para {novoValor}")

            # Sobrescrever o arquivo para alterar mudanças
            with open(self.pathSettings, 'w', encoding="utf-8") as configfile:
                settings.write(configfile)
        
        return flagAlteracaoValida


    def _resolveValidatorPath(self) -> Path:
        """
        Garantir que o Path do validator seja válido (pode ser o padrão ou o do usuário)
        Feita para ser usada apenas por InicializadorSistema

        Returns:
            O caminho do validator a ser usado (Path)
        
        Raises:
            SystemExit: Se o validator não existe, não pode ser instalado ou é invalido
        """
        # Ler e limpar o caminho do validator
        pathValidator = str(self.returnValorSettings('caminho_validator')).split('#')[0].strip()
        pathValidator = Path(pathValidator)

        # Não é absoluto => validator_cli padrão, endereçar com a pasta do nosso projeto
        if not pathValidator.is_absolute():
            pathValidator = self.pathFut / pathValidator

        ## Verificando o validator
        from Backend.Classes.gerenciador_validator import GerenciadorValidator  
        # Garante que o valitor_cli esteja instalado
        if not pathValidator.exists():
            try:
                GerenciadorValidator.instalaValidatorCli(pathValidator)
            except Exception as e:
                logger.fatal("Erro ao instalar o validator_cli padrão")
                sys.exit("Erro ao instalar o validator_cli padrão") # Sem esses arquivos o sistema não consegue rodar
        
        # Garantir que é válido
        if not GerenciadorValidator.verificaVersaoValidator(pathValidator):
            # Validator não é válido
            logger.fatal("Validator_cli utilizado não é válido")
            sys.exit("Validator_cli utilizado não é válido") # Sem esses arquivos o sistema não consegue rodar
        
        return pathValidator