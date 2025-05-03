from pathlib import Path
import logging
logger = logging.getLogger(__name__)

class InicializadorSistema:
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

    # Ideia: Faz a requisição do valor de uma configuração (em settings.ini) e seu valor é retornado como str ou None(caso de erro)
    def returnValorSettings(self, settingsBuscada):
        # Ler o arquivo de configuracoes
        import configparser
        settings = configparser.ConfigParser()
        settings.read(self.pathSettings)
        settingsBuscada = str(settingsBuscada)

        # Buscar a configuração requisitada
        for secao in settings.sections():
            if settingsBuscada in settings[secao]:
                return settings[secao][settingsBuscada]
        
        # Caso de erro (configuração não foi encontrada)
        return None

    # Ideia: Permite o usuário alterar o valor de uma configuração do settings.ini
    def alterarValorSetting(self, configuracaoSerAlterada, novoValor):
        novoValor = str(novoValor) # Por segurança, adicionar previsibilidade
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
        if configuracaoSerAlterada.lower() == "caminho_validator":
            if novoValor != "reset":
                caminhoArquivo = Path(novoValor)
                if not caminhoArquivo.is_absolute:
                    caminhoArquivo = Path.cwd() + caminhoArquivo
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
            if novoValor.lower() in ["true", "1", "yes", "sim"]:
                novoValor = "True"
            else:
                novoValor = "False"
            flagAlteracaoValida = True
        
        # Adicionando alguns tratamentos especiais:
        # Tempo baixo demais
        if configuracaoSerAlterada.lower() == 'timeout':
            if novoValor < 15:
                flagAlteracaoValida = False
                raise ValueError("A configuração de timeout necessita de pelo menos 15 segundos para garantir execução.")
        # Número de threads tem que ser natural*
        if configuracaoSerAlterada.lower() == "max_threads":
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
            with open(self.pathSettings, 'w') as configfile:
                settings.write(configfile)
        
        return flagAlteracaoValida

    # Ideia: Garantir que o Path do validator seja válido (pode ser o padrão ou o do usuário)
    def _resolveValidatorPath(self) -> Path:
        # Ler e limpar o caminho do validator
        pathValidator = str(self.returnValorSettings('caminho_validator')).split('#')[0].strip()
        pathValidator = Path(pathValidator)

        # Não é absoluto => validator_cli padrão, endereçar com a pasta do nosso projeto
        if not pathValidator.is_absolute():
            pathValidator = self.pathFut / pathValidator
            # Garante que o valitor_cli esteja instalado
            from Classes.gerenciador_validator import GerenciadorValidator  
            try:
                GerenciadorValidator.instalaValidatorCli(pathValidator)
            except Exception as e:
                import sys
                logger.fatal("Erro ao instalar o validator_cli padrão")
                sys.exit("Erro ao instalar o validator_cli padrão")
        
        return pathValidator