from pathlib import Path
from json import dump
from Classes.inicializador_sistema import InicializadorSistema
from Classes.Exceptions import ExcecaoTemplate
import time
import subprocess
import requests, zipfile
import time
import logging
logger = logging.getLogger(__name__)

linkDownloadValidator = "https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"

class GerenciadorValidator(InicializadorSistema):
    # Construtor
    def __init__(self, pathFut):
        super().__init__(pathFut)

    # Ideia: Faz a instalação inicial do validator_cli
    @classmethod
    def instalaValidatorCli(cls, pathValidator):
        from Classes.gerenciador_testes import GerenciadorTestes
        if not pathValidator.exists(): # Evitar sobrescrita
            try:
                logger.info("Fazendo download do validator_cli")
                GerenciadorTestes.get_instance().baixaArquivoUrl(linkDownloadValidator, pathValidator)
            except Exception as e:
                logger.fatal(f"Erro ao instalar o validator_cli: {e}")
                raise e

    # Ideia: Instala ou atualiza o validator_cli.jar 
    def atualizarValidatorCli(self, pathValidator = None):
        # Não foi especificado, usar nosso validator_cli
        if not pathValidator:
            pathValidator = self.pathValidator
        logger.info("Buscando atualizações do validator_cli")

        from Classes.gerenciador_testes import GerenciadorTestes
        # Verificando se o validator já existe
        if pathValidator.exists(): 
            versaoBaixada = None
            versaoGit = None 

            # 1º Verifica a versão do arquivo baixado
            try:
                with zipfile.ZipFile(pathValidator, 'r') as jar:
                    with jar.open('fhir-build.properties') as manifest:
                        for linha in manifest:
                            linhaLegivel = linha.decode(errors="ignore").strip()
                            if "orgfhir.version" in linhaLegivel:
                                versaoBaixada = linhaLegivel.split("orgfhir.version=")[1]
            except Exception as e:
                raise ExcecaoTemplate("Arquivo validator_cli inválido", e)

            # 2º Consulta o GitHub pela última versão
            maxTentativas = 3
            numTentativas = 0
            while numTentativas <= maxTentativas:
                try:
                    apiUrl = "https://api.github.com/repos/hapifhir/org.hl7.fhir.core/releases/latest"
                    response = requests.get(apiUrl)
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
            if (versaoBaixada and versaoGit) and (versaoBaixada != versaoGit):
                try:
                    caminhoValidatorTemp = pathValidator.with_name("NOVOvalidator_cli.jar")
                    GerenciadorTestes.get_instance().baixaArquivoUrl(linkDownloadValidator, caminhoValidatorTemp)
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
            logger.info("Nenhuma instancia de validator_cli encontrada, fazendo o download")
            # Se o validator não estiver instalado, faz a instalação inicial
            self.instalaValidatorCli(pathValidator)

    # Ideia: Executa a validação do arquivo FHIR usando o validator_cli.jar.
    def validarArquivoFhir(self, arquivoValidar: Path, args=None):  
        arquivoValidar = arquivoValidar.expanduser()
        if not arquivoValidar.is_absolute():
            arquivoValidar = Path.cwd() / arquivoValidar

        tempoTimeout = int(self.returnValorSettings('timeout'))
        from Classes.gerenciador_testes import GerenciadorTestes # Evitar import cíclico, não mover esse import
        pastaRelatorio = GerenciadorTestes.get_instance().definePastaValidator()

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
                    comando += args if isinstance(args, list) else [args]
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
            raise subprocess.TimeoutExpired(f"Timeout na validação de: {arquivoValidar}") from e
        except Exception as e:
            logger.error(f"Erro durante a validação do arquivo FHIR: {e}")
            raise e
