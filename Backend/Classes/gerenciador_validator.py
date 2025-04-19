from pathlib import Path
from Classes.inicializador_sistema import InicializadorSistema
import time
import subprocess
import requests, zipfile
from asyncio import sleep

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
                GerenciadorTestes.get_instance().baixaArquivoUrl(linkDownloadValidator, pathValidator)
            except Exception as e:
                raise e

    # Ideia: Instala ou atualiza o validator_cli.jar 
    def atualizarValidatorCli(self, pathValidator = None):
        # Não foi especificado, usar nosso validator_cli
        if not pathValidator:
            pathValidator = self.pathValidator

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
                raise e

            # 2º Consulta o GitHub pela última versão
            maxTentativas = 3
            numTentativas = 0
            while numTentativas < maxTentativas:
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
                    if numTentativas < maxTentativas:
                        print(f"Erro na tentativa {numTentativas+1} de conexão a plataforma, reiniciando...")
                        sleep(3)
                    else:
                        raise e

            # 3º Compara as versões e atualiza se necessário
            if (versaoBaixada and versaoGit) and (versaoBaixada != versaoGit):
                try:
                    caminhoValidatorTemp = pathValidator.with_name("NOVOvalidator_cli.jar")
                    GerenciadorTestes.get_instance().baixaArquivoUrl(linkDownloadValidator, caminhoValidatorTemp)
                except Exception as e:
                    raise e

                if caminhoValidatorTemp.exists():
                    pathValidator.unlink()  # Remove o arquivo antigo
                    caminhoValidatorTemp.rename(pathValidator)
        else:
            # Se o validator não estiver instalado, faz a instalação inicial
            self.instalaValidatorCli(pathValidator)

    # Ideia: Executa a validação do arquivo FHIR usando o validator_cli.jar.
    def validarArquivoFhir(self, arquivoValidar: Path, args=None):  
        arquivoValidar = arquivoValidar.expanduser()
        if not arquivoValidar.is_absolute():
            arquivoValidar = Path.cwd() / arquivoValidar

        # ENVIAR PARA gerenciador_testes ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        tempoTimeout = int(self.returnValorSettings('timeout'))
        flagSalvarOutput = self.returnValorSettings('flagArmazenarSaidaValidator').lower() in ["true", "1", "yes"]
        if flagSalvarOutput: # Pasta permanente
            pastaRelatorio = Path.cwd() / "resultados-fut"
        else: # Pasta temporária (Apagada após a criação do relatório final)
            pastaRelatorio = Path.cwd() / ".temp-fut"
        pastaRelatorio.mkdir(exist_ok=True)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
                #print(resultado.stdout)
                #print(resultado.stderr)
                return [caminhoRelatorio, (end - start)]
            else:
                raise FileNotFoundError(f"Arquivo de entrada não foi encontrado: {arquivoValidar}")
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(f"Timeout na validação de: {arquivoValidar}") from e
        except Exception as e:
            raise e