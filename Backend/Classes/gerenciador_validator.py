from pathlib import Path
from json import dump
from Classes.inicializador_sistema import InicializadorSistema
from Classes.Exceptions import ExcecaoTemplate
import time
import subprocess
import requests
import zipfile
import logging
logger = logging.getLogger(__name__)

linkDownloadValidator = "https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"

class GerenciadorValidator(InicializadorSistema):
    # Construtor
    def __init__(self, pathFut):
        super().__init__(pathFut)


    @classmethod
    def instalaValidatorCli(cls, pathValidator:Path):
        """
        Faz a instalação inicial do validator_cli

        Args:
            pathValidator (Path): O caminho para o endereço do validator_cli
        
        raises:
            requests.exceptions.ConnectionError: Erro de conexão com o site
            ...
        """
        from Classes.gerenciador_testes import GerenciadorTestes
        if not pathValidator.exists(): # Evitar sobrescrita
            try:
                logger.info("Fazendo download do validator_cli")
                # Dando 10 minutos para terminar o download (~.25mb/s)
                GerenciadorTestes.get_instance().baixarArquivoUrl(linkDownloadValidator, pathValidator, requestsTimeout=600) 
            except Exception as e:
                logger.fatal(f"Erro ao instalar o validator_cli: {e}")
                raise e
    

    @classmethod
    def verificaVersaoValidator(cls, pathValidator:Path):
        """
        Retorna a versão do validator
        
        Args:
            pathValidator (Path): Caminho onde o validator é salvo
        
        Returns:
            Versão do validator OU None(caso de erro)
        """
        try:
            with zipfile.ZipFile(pathValidator, 'r') as jar:
                with jar.open('fhir-build.properties') as manifest:
                    for linha in manifest:
                        linhaLegivel = linha.decode(errors="ignore").strip()
                        if "orgfhir.version" in linhaLegivel:
                            versaoBaixada = linhaLegivel.split("orgfhir.version=")[1]
                            return versaoBaixada
        except Exception as e:
            return None


    def atualizarValidatorCli(self, pathValidator:Path = None):
        """
        Tenta atualizar o validator (baixa ele se não for encontrado)

        Args:
            pathValidator (Path): Caminho do validator a ser atualizado (Opcional)
        
        Raises:
            requests.exceptions.Timeout: Tempo de execução superou o limite estabelecido em settings.ini
            requests.exceptions.ConnectionError: Erro de conexão com o site
            ...
        """
        # Não foi especificado, usar nosso validator_cli
        if not pathValidator:
            pathValidator = self.pathValidator
        logger.info("Buscando atualizações do validator_cli")

        # Ver o tempo máximo para buscas
        requestsTimeout = int(self.returnValorSettings("requests_timeout"))

        from Classes.gerenciador_testes import GerenciadorTestes
        # Verificando se o validator já existe
        if pathValidator.exists(): 
            # 1º Verifica a versão do arquivo baixado
            try:
                versaoBaixada = self.verificaVersaoValidator(pathValidator)
            except Exception as e:
                raise ExcecaoTemplate("Arquivo validator_cli inválido", e)
             
            # 2º Consulta o GitHub pela última versão
            logger.info("Buscando ultima versao no git")
            versaoGit = None
            maxTentativas = 3
            numTentativas = 0
            while numTentativas <= maxTentativas:
                try:
                    apiUrl = "https://api.github.com/repos/hapifhir/org.hl7.fhir.core/releases/latest"
                    response = requests.get(apiUrl, timeout=requestsTimeout)
                    if response.status_code == 200:
                        dadosGit = response.json()
                        versaoGit = dadosGit.get('tag_name')
                    else:
                        return response.status_code
                except Exception as e:
                    numTentativas += 1 # Contabilizar tentativa
                    if numTentativas <= maxTentativas:
                        logger.warning(f"Erro na tentativa {numTentativas} de conexão com o git do validato_cli")
                        print(f"Erro na tentativa {numTentativas} de conexão a plataforma, reiniciando...")
                        time.sleep(3)
                    else:
                        logger.warning(f"Erro ao conectar com o github do validator_cli: {e}")
                        print(f"Não foi posssível atualizar o validator_cli, executando os testes com a versão instalada '{versaoBaixada}'")
                        raise e

            # 3º Compara as versões e atualiza se necessário
            logger.info("Tentando comparar versoes do validator")
            print(versaoBaixada, versaoGit)
            if (versaoBaixada and versaoGit) and (versaoBaixada != versaoGit):
                try:
                    caminhoValidatorTemp = pathValidator.with_name("temp_validator_cli.jar")
                    self.instalaValidatorCli(caminhoValidatorTemp)
                    logger.info("Download da versão mais recente do validator_cli feita")
                except Exception as e:
                    logger.error(f"Erro ao instalar a versão mais nova do validator: {e}")
                    raise e

                if caminhoValidatorTemp.exists(): # Por segurança
                    logger.info("Atualizando o validator_cli")
                    pathValidator.unlink()  # Remove o arquivo antigo
                    caminhoValidatorTemp.rename(pathValidator)
            else:
                logger.info("Verificação de atualização finalizada")
        else:
            logger.info("Nenhuma instancia de validator_cli encontrada, iniciando o download")
            # Se o validator não estiver instalado, faz a instalação inicial
            self.instalaValidatorCli(pathValidator)


    def validarArquivoFhir(self, arquivoValidar: Path, args:list=None):  
        """
        Executa a validação do arquivo FHIR usando o validator_cli.jar.

        Args:
            arquivoValidar (Path): Arquivo que será validado pelo validator_cli (definido em settings.ini)
            args (list): Define argumentos extras a serem usados na validação (opcional)
        
        Returns:
            [Caminho do relatório criado (JSON), Tempo de execução do teste (em segundos)]
        
        Raises:
            FileNotFoundError: Não conseguiu encontrar o arquivo a ser testado
            ...
        """
        arquivoValidar = arquivoValidar.expanduser()
        if not arquivoValidar.is_absolute():
            arquivoValidar = Path.cwd() / arquivoValidar

        tempoTimeout = int(self.returnValorSettings('timeout'))
        from Classes.gerenciador_testes import GerenciadorTestes # Evitar import cíclico, não mover esse import
        pastaRelatorio = GerenciadorTestes.get_instance().definirPastaValidator()

        try:
            if arquivoValidar.exists():
                nomeRelatorio = arquivoValidar.with_suffix(".json").name
                caminhoRelatorio = pastaRelatorio / nomeRelatorio
                comando = [
                    "java", "-jar", str(self.pathValidator.resolve()),
                    str(arquivoValidar.resolve()),
                    "-output", str(caminhoRelatorio.resolve()),
                    "-version", "4.0.1"
                ]
                if args:
                    comando += args if isinstance(args, list) else [args] # Por segurança
                #print(comando)
                start = time.time()
                resultado = subprocess.run(comando, capture_output=True, text=True, timeout=tempoTimeout)
                end = time.time()
                #print(resultado) # debug
                #print(resultado.stdout) # debug
                #print(resultado.stderr) # debug
                if not caminhoRelatorio.exists():
                    diconario = { 'issue': [{ 'severity': 'fatal', 'code': 'non-existent', 'details' : {'text': "non-existent ig or resource or profile"}, 'expression':  [] }] }
                    with open(caminhoRelatorio, mode="w", encoding="utf8") as arquivo:
                        dump(diconario, arquivo, indent=4, ensure_ascii=False)
                return [caminhoRelatorio, (end - start)]
            else:
                logger.warning(f"Erro ao encontrar o arquivo a ser validado: {arquivoValidar}")
                raise FileNotFoundError(f"Arquivo de entrada não foi encontrado: {arquivoValidar}")
        except subprocess.TimeoutExpired as e:
            logger.warning(f"Timeout na verificação de {arquivoValidar}")
            # Criar o JSON manualmente para registrar o timeout
            diconario = { 'issue': [{ 'severity': 'fatal', 'code': 'non-existent', 'details' : {'text': f"attempt to validate the file timed out after {tempoTimeout} seconds"}, 'expression':  [] }] }
            with open(caminhoRelatorio, mode="w", encoding="utf8") as arquivo:
                dump(diconario, arquivo, indent=4, ensure_ascii=False)
                return [caminhoRelatorio, tempoTimeout]
        except Exception as e:
            logger.error(f"Erro durante a validação do arquivo FHIR: {e}")
            raise e
