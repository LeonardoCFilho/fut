from pathlib import Path
from Backend.Classes.inicializador_sistema import InicializadorSistema
from Backend.Classes.gerenciador_validator import GerenciadorValidator
from Backend.Classes.gerador_relatorio import GeradorRelatorios
from Backend.Classes.executor_teste import ExecutorTestes
from Backend.Classes.Exceptions import ExcecaoTemplate
import os
import threading
import concurrent.futures
import requests
import sys
import time
import logging

logger = logging.getLogger(__name__)

# Singleton
class GerenciadorTestes:
    _instance = None
    _lock = threading.Lock()  
    # Construtor
    def __init__(self, pathFut:Path, inicializador = None, execTestes = None, gerenValidator = None):
        if not GerenciadorTestes._instance:
            GerenciadorTestes._instance = self
            self.pathFut = pathFut
            self.inicializador = inicializador or InicializadorSistema(pathFut)
            self.execTestes = execTestes or ExecutorTestes(pathFut)
            self.gerenValidator = gerenValidator or GerenciadorValidator(pathFut)
    # Retorna o objeto singleton da classe
    @staticmethod
    def get_instance(pathFut:Path=None, inicializador = None, execTestes = None, gerenValidator = None):
        with GerenciadorTestes._lock:
            if GerenciadorTestes._instance is None:
                if pathFut is None or not (pathFut.exists() and pathFut.is_dir()): # Garantir que existe e é uma pasta
                    raise ValueError("Caminho da pasta do projeto deve ser providenciada na primeira execução")
                GerenciadorTestes._instance = GerenciadorTestes(pathFut, inicializador, execTestes, gerenValidator)
        return GerenciadorTestes._instance


    def baixarArquivoUrl(self, url:str, enderecoArquivo, requestsTimeout:int=None, maxTentativas:int=3):
        """
        Faz download de um arquivo a partir de uma URL para o caminho especificado.
        P.s.: Especificar o tipo de arquivo no nome do arquivo

        Args:
            url (str): URL de download do arquivo
            enderecoArquivo: Endereço onde o arquivo será salvo (e o tipo do arquivo)
            requestsTimeout (int): Tempo máximo, em segundos, para o download terminar
            maxTentativas (int): O número de tentativas de download a serem feitas (padrão é 3)
        
        Raises:
            requests.exceptions.Timeout: Tempo de execução superou o limite estabelecido em settings.ini
            requests.exceptions.ConnectionError: Erro de conexão com o site
            ...
        """
        
        if not requestsTimeout:
            requestsTimeout = int(self.inicializador("requests_timeout"))
            
        numTentativas = 0
        while numTentativas < maxTentativas:
            try:
                logger.info(f"Tentando fazer o download de {enderecoArquivo}")
                # Iniciando request
                response = requests.get(url, stream=True, timeout=requestsTimeout)
                response.raise_for_status()  # Lança exceção em caso de erro

                # Iniciando download
                enderecoArquivo = Path(enderecoArquivo)
                with enderecoArquivo.open("wb", encoding="utf-8") as arquivo_baixado:
                    for chunk in response.iter_content(chunk_size=8192):
                        arquivo_baixado.write(chunk)
                logger.info("Download feito com sucesso")
                return 

            # Caso de erro, adicionar logs
            except Exception as e:
                numTentativas += 1 # Contabilizar tentativa
                if numTentativas < maxTentativas:
                    logger.warning(f"Erro na tentativa {numTentativas} de download para {url}")
                    print(f"Erro na tentativa {numTentativas} de download, reiniciando...")
                    time.sleep(3)
                else:
                    logger.error(f"Falha ao tentar fazer o download de {url} após {maxTentativas} tentativas. Erro: {str(e)}")
                    raise e


    def definirPastaValidator(self) -> Path:
        """
        Determinar a pasta que os arquivos do validator serão salvos

        Returns:
            O caminho (Path) da pasta para os arquivos do validator
        """
        iniciadorSistema = self.inicializador
        flagSalvarOutput = iniciadorSistema.returnValorSettings('armazenar_saida_validator').lower() in ["true", "1", "yes"]
        if flagSalvarOutput:  # Pasta permanente
            pastaRelatorio = Path.cwd() / "resultados-fut"
        else:  # Pasta temporária (Apagada após a criação do relatório final)
            pastaRelatorio = Path.cwd() / ".temp-fut"
        pastaRelatorio.mkdir(exist_ok=True)  # Garantir que a pasta existe
        return pastaRelatorio


    def atualizarExecucaoValidator(self):
        """
        Usado em execução, para garantir que o validator esteja atualizado
        
        Raises:
            SystemExit: Caso que o validator é inválido
            ...
        """
        # Garantir que o validator esteja atualizado
        try:
            self.gerenValidator.atualizarValidatorCli(self.inicializador.pathValidator)
        except ExcecaoTemplate as e:
            logger.fatal(f"O arquivo do validator_cli é inválido: {e}")
            sys.exit("Arquivo validator_cli é inválido, verifique seu download ou considere utilizar o validator padrão")
        except requests.exceptions.ConnectionError as e:
            pass  # Já está registrado no log e não é um erro crítico
        except Exception as e:
            logger.error(f"Erro ao atualizar o validator: {e}")  # Programa continua executando, mas não usar a versão mais recente do validator


    def prepararExecucaoTestes(self, args):
        """
        Limpeza e preparo da entrada para os testes serem feitos

        Args: 
            args: Argumentos de entrada para a criação a lista de testes a serem validados
        
        Returns:
            Lista com endereços dos arquivos de testes a serem testados (pode ser vazia)
        """
        # Fazer a leitura dos argumentos recebidos 
        logger.info("Lista de testes a serem examinadas criada")
        if not args:  # Garantir que há uma lista
            args = []
        #print(executorDeTestes.gerarListaArquivosTeste(args))
        return self.execTestes.gerarListaArquivosTeste(args)


    def executarThreadsTeste(self, listaArquivosTestar:list, numThreads:int):
        """
        Execução dos testes que o usuário solicitou + uso de threads

        args:
            listaArquivosTestar (list): Lista com os endereços dos arquivos de testes
            numThreads (int): O número máximo de threads que o programa usará
        
        Returns:
            Entregas graduais do tipo dict
        """
        # Iniciar a validação
        logger.info("Iniciando a execução dos testes requisitados")
        with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
            for resultado in executor.map(self.execTestes.validarArquivoTeste, listaArquivosTestar):
                yield resultado


    def iniciarCriacaoRelatorio(self, resultadosValidacao:list, versaoRelatorio:str, tempo_execucao_total:float):
        """
        Criar o relatório de acordo com a escolha do usuário (JSON ou HTML)

        Args:
            resultadosValidacao (list): Lista dos resultados (dict) dos testes
            versaoRelatorio (str): Versão do relatório que será feita (JSON ou HTML)
        
        Raises:
            PermissionError: Programa não tem permissão para criar/escrever o arquivo
            ...
        """
        # Criar o relatório
        logger.info(f"Iniciando a criação do relatório, relatório selecionado é do tipo {versaoRelatorio}")
        geradorRelatorio = GeradorRelatorios(resultadosValidacao)
        try:
            geradorRelatorio.gerarRelatorioJson(tempo_execucao_total=tempo_execucao_total)  # Arquivo .json sempre é criado
            # if versaoRelatorio.lower() == "json":
            #     print("Relatório JSON criado!") 
            # if versaoRelatorio.lower() == "html":
            #     geradorRelatorio.gerarRelatorioHtml()
        except Exception as e:
            logger.error(f"Erro ao criar o relatório: {e}")  # Por segurança


    def executarTestesCompleto(self, args: list, versaoRelatorio:str, entregaGradual:bool=False):
        """
        Controlar o fluxo para a execução dos testes

        Args:
            args (list): Argumentos que serão usados para criar a lista de testes 
            versaoRelatorio (str): Versão do relatório que será feita (JSON ou HTML)
            entregaGradual (bool): Se a entrega dos resultados será gradual OU súbita
        
        Returns:
            Listas [resultado, porcentagem finalizada] gradualmente OU nada
        
        Raises:
            SystemExit: Se arquivos essenciais não foram encontrados/válidos
            ValueError: Quando o args não consegue criar uma lista de testes válida
        """
        self.atualizarExecucaoValidator()

        # Determinar número de threads
        numThreads = int(self.inicializador.returnValorSettings('max_threads'))  # Pela settings
        numThreads = min(numThreads, max(1, (os.cpu_count() - 2)))  # Não todas as threads

        # Criar a lista de testes a serem executados
        listaArquivosTestar = self.prepararExecucaoTestes(args)

        if len(listaArquivosTestar) == 0:
            logger.info("Nenhum caso de teste válido encontrado")
            raise ValueError("Nenhum arquivo de teste encontrado.")
        else:
            try:
                # Caso válido de teste
                startTestes = time.time()
                resultadosValidacao = []
                for resultado in self.executarThreadsTeste(listaArquivosTestar, numThreads):
                    resultadosValidacao.append(resultado)
                    # Entregas graduais
                    if entregaGradual:
                        yield [resultado, round((len(resultadosValidacao) / len(listaArquivosTestar)), 4)]
                endTestes = time.time()
            except Exception as e:
                logger.error(f"Erro ao rodar os testes em threads: {e}")
                raise e
            else:
                # Sucesso na execução dos testes
                logger.info("Testes listados completos")
                print("Testes finalizados!")

                # print(resultadosValidacao)  # debug

                self.iniciarCriacaoRelatorio(resultadosValidacao, versaoRelatorio, endTestes-startTestes)  # (endTestes-startTestes) # Eventualmente enviar para o relatório

                # print("Arquivos encontrados:", listArquivosValidar)  # debug
                # print("Relatório de testes:", resultadosValidacao)  # debug

