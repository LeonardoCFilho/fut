from pathlib import Path
class InicializadorSistema:
    def __init__(self, pathFut):
        # Caminho para o nosso projeto
        if not isinstance(pathFut,Path):
            pathFut = Path(pathFut)  
        self.pathFut = pathFut

        # Caminho para o arquivo de configuracoes
        self.pathSettings = self.pathFut / "Backend" / "settings.ini"
        # Caso de erro
        if not self.pathSettings.exists():
            raise FileNotFoundError("Arquivo settings.ini não foi encontrado")
        
        # Caminho para o validator
        self.pathValidator = self._resolveValidatorPath()
        if not self.pathValidator.exists():
            raise FileNotFoundError("validator_cli.jar não foi encontrado! Tente retornar seu valor ao padrão")

    def returnValorSettings(self, settingsBuscada):
        # Ler o arquivo de configuracoes
        import configparser
        settings = configparser.ConfigParser()
        settings.read(self.pathSettings)

        # Buscar a configuração requisitada
        for secao in settings.sections():
            if settingsBuscada in settings[secao]:
                return settings[secao][settingsBuscada]
        
        # Caso de erro
        return None

    def _resolveValidatorPath(self) -> Path:
        # Ler e limpar o caminho do validator
        pathValidator = str(self.returnValorSettings('pathValidator_cli')).split('#')[0].strip()
        pathValidator = Path(pathValidator)

        # Não é absoluto => validator_cli padrão, endereçar com a pasta do nosso projeto
        if not pathValidator.is_absolute():
            pathValidator = self.pathFut / pathValidator
            # Garante que o valitor_cli esteja instalado
            from Classes.gerenciador_validator import GerenciadorValidator  
            GerenciadorValidator.instalaValidatorCli(pathValidator)
        
        return pathValidator