from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ControladorConfiguracao:
    """
    Gerencia a leitura e alteração de configurações do sistema
    a partir do arquivo settings.ini.
    """

    def __init__(self, pathSettings:Path):
        """
        Inicializa o gerenciador de configurações.

        Args:
            pathSettings (Path): Caminho para o arquivo de configurações.
        """
        self.pathSettings = pathSettings


    def returnValorSettings(self, settingsBuscada: str) -> str|None:
        """
        Busca o valor de uma configuração na settings.ini

        Args:
            settingsBuscada (str): Nome da configuração a ser buscada.
        
        Returns:
            Valor da configuração ou None (caso de erro).
        """
        import configparser
        settings = configparser.ConfigParser()
        settings.read(self.pathSettings)
        settingsBuscada = str(settingsBuscada).lower()

        for secao in settings.sections():
            if settingsBuscada in settings[secao]:
                return settings[secao][settingsBuscada]
        return None


    def alterarValorSetting(self, configuracaoSerAlterada: str, novoValor: str) -> bool:
        """
        Altera o valor de uma configuração na settings.ini.

        Args:
            configuracaoSerAlterada (str): Nome da configuração a ser alterada.
            novoValor (str): Novo valor para a configuração.
        
        Returns:
            bool: Indica se a configuração foi alterada com sucesso.
        
        Raises:
            ValueError: Se o novoValor for incompatível com o tipo esperado da configuração.
            FileNotFoundError: Se um caminho especificado para arquivos não existir.
        """
        import configparser
        configuracaoSerAlterada = configuracaoSerAlterada.lower()
        novoValor = str(novoValor).lower()

        dictConfiguracoes = {
            "timeout": int,
            "max_threads": int,
            "caminho_validator": str,
        }
        listaConfiguracoesBool = [
            "armazenar_saida_validator",
        ]

        flagAlteracaoValida = False


        ## Configuração do caminho do validator (Path)
        if configuracaoSerAlterada == "caminho_validator":
            if novoValor != "reset":
                caminhoArquivo = Path(novoValor)
                if not caminhoArquivo.is_absolute():
                    caminhoArquivo = Path.cwd() / caminhoArquivo
                if not caminhoArquivo.exists():
                    raise FileNotFoundError(f"Novo validator_cli não foi encontrado, endereço usado: {caminhoArquivo.resolve()}")
            else:
                novoValor = Path("Backend/validator_cli.jar").as_posix()
            flagAlteracaoValida = True


        ## Configuração com tipo simples (int, str, ...)
        if configuracaoSerAlterada in dictConfiguracoes:
            tipoConfiguracao = dictConfiguracoes[configuracaoSerAlterada]
            try:
                novoValor = tipoConfiguracao(novoValor)
                flagAlteracaoValida = True
            except ValueError:
                raise ValueError(f"Novo valor para configuração inválido! Essa configuração é do tipo {tipoConfiguracao.__name__}.")


        ## Configuração de bool
        if configuracaoSerAlterada in listaConfiguracoesBool:
            if novoValor in ["true", "1", "yes", "sim"]:
                novoValor = "True"
            else:
                novoValor = "False"
            flagAlteracaoValida = True


        ## Rail guard contra valores baixos demais das configuraçãoes
        if configuracaoSerAlterada == 'timeout' and novoValor < 15:
            raise ValueError("A configuração de timeout necessita de pelo menos 15 segundos para garantir execução.")
        if configuracaoSerAlterada == "max_threads" and novoValor < 1:
            raise ValueError("O número de máximo de threads tem que ser maior que 0!")


        ## Utilizando o arquivo de configuração em si
        settings = configparser.ConfigParser()
        settings.read(self.pathSettings)
        if flagAlteracaoValida:
            for secao in settings.sections():
                if configuracaoSerAlterada in settings[secao]:
                    settings[secao][configuracaoSerAlterada] = str(novoValor)
                    logger.info(f"Valor da configuração '{configuracaoSerAlterada}' foi alterado para {novoValor}")

            with open(self.pathSettings, 'w', encoding="utf-8") as configfile:
                settings.write(configfile)

        return flagAlteracaoValida