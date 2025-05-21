from pathlib import Path
from Classes.inicializador_sistema import InicializadorSistema
from Classes.gerenciador_validator import GerenciadorValidator
from Classes.gerador_relatorio import GeradorRelatorios
from Classes.executor_teste import ExecutorTestes
from Classes.Exceptions import ExcecaoTemplate
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
    def __init__(self, pathFut):
        if not GerenciadorTestes._instance:
            GerenciadorTestes._instance = self
            self.pathFut = pathFut
            self.inicializador = None
    # Retorna o objeto singleton da classe
    @staticmethod
    def get_instance(pathFut=None):
        with GerenciadorTestes._lock:
            if GerenciadorTestes._instance is None:
                if pathFut is None:
                    raise ValueError("Caminho da pasta do projeto deve ser providenciada na primeira execução")
                GerenciadorTestes._instance = GerenciadorTestes(pathFut)
        return GerenciadorTestes._instance


    def iniciarSistema(self):
        """
        Garantir o funcionamento do sistema (e do objeto de InicializadorSistema)

        Returns:
            self.inicializador (InicializadorSistema): Objeto que será salvo para GerenciadorTestes

        Raises:
            SystemExit: Algum erro impediu a criação do self.inicializador, o que impediria o programa de funcionar
        """
        if self.inicializador is None:
            logger.info("Criando instancia de InicializadorSistema para GerenciadorTestes")
            try:
                self.inicializador = InicializadorSistema(self.pathFut)
            except FileNotFoundError as e:
                logger.fatal(e)
                sys.exit(e)
        return self.inicializador


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
            inicializadorSistema = self.iniciarSistema()
            requestsTimeout = int(inicializadorSistema("requests_timeout"))
            
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


    def criaArquivoYamlTeste(self, dadosArquivo:dict=None, caminhoArquivo=None):
        """
        Cria um arquivo .yaml (preenchido ou não) que segue o nosso template para caso de teste
        Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
        
        Args:
            dadosArquivo (dict): dict com os dados a serem inseridos no arquivo (opcional)
            caminhoArquivo: Caminho onde o arquivo será criado/escrito (opcional)
        
        Raises:
            PermissionError: Programa não tem permissão para a criação/escrita do arquivo
            ...
        """
        if not caminhoArquivo:  # Se o nome não é especificado => template
            caminhoArquivo = "template.yaml"
        logger.info(f"Arquivo de teste criado em {caminhoArquivo}")
        if not dadosArquivo:  # Sem informações especificadas => template
            logger.info("Template de um arquivo de teste criado") 
            dadosArquivo = {
                "test_id": '',
                "description": '',
                "igs": '',
                "profiles": '',
                "resources": '',
                "caminho_instancia": '',
                "status": '',
                "error": '',
                "warning": '',
                "fatal": '',
                "information": '',
                "invariantes": '',
            }

        templateYaml = f"""test_id: {dadosArquivo.get('test_id', '')} # (Obrigatório) Identificador único para cada teste (string).
description: {dadosArquivo.get('description', '')} # (Recomendado) Descricao (string).
context: # Definição do contexto de validação.
    igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
        - {dadosArquivo.get('igs', '')} # IDs ou url dos IGs (Apenas 1 por linha).
    profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
        - {dadosArquivo.get('profiles', '')} # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
    resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
        - {dadosArquivo.get('resources', '')} # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
caminho_instancia: {dadosArquivo.get('caminho_instancia', '')} #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
    status: {dadosArquivo.get('status', '')}  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
    error: [{dadosArquivo.get('error', '')}]  #  (Obrigatório) Lista de erros esperados (lista de string).
    warning: [{dadosArquivo.get('warning', '')}]  #  (Obrigatório) Lista de avisos esperados (lista de string).
    fatal: [{dadosArquivo.get('fatal', '')}] #  #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
    information: [{dadosArquivo.get('information', '')}]  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
    invariantes: {dadosArquivo.get('invariantes', '')} # (Opcional)"""
        try:
            with open(caminhoArquivo, "w", encoding="utf-8") as file:  # Se caminhoArquivo já existia ele é sobrescrito
                file.write(templateYaml)
        except PermissionError as e:
            logger.error("Programa não tem permissão para criar o arquivo de teste requisitado")
            raise e
        except Exception as e:
            raise e  # improvável


    def definirPastaValidator(self) -> Path:
        """
        Determinar a pasta que os arquivos do validator serão salvos

        Returns:
            O caminho (Path) da pasta para os arquivos do validator
        """
        iniciadorSistema = self.iniciarSistema()
        flagSalvarOutput = iniciadorSistema.returnValorSettings('armazenar_saida_validator').lower() in ["true", "1", "yes"]
        if flagSalvarOutput:  # Pasta permanente
            pastaRelatorio = Path.cwd() / "resultados-fut"
        else:  # Pasta temporária (Apagada após a criação do relatório final)
            pastaRelatorio = Path.cwd() / ".temp-fut"
        pastaRelatorio.mkdir(exist_ok=True)  # Garantir que a pasta existe
        return pastaRelatorio


    def atualizarExecucaoValidator(self, inicializadorSistema:InicializadorSistema):
        """
        Usado em execução, garantir que o validator esteja atualizado

        Args:
            inicializadorSistema (InicializadorSistema): Objeto de InicializadorSistema que é usado para endereçamento
        
        Raises:
            SystemExit: Caso que o validator é inválido
            ...
        """
        # Garantir que o validator esteja atualizado
        atualizarValidator = GerenciadorValidator(self.pathFut)
        try:
            atualizarValidator.atualizarValidatorCli(inicializadorSistema.pathValidator)
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
        executorDeTestes = ExecutorTestes(self.pathFut)  
        logger.info("Lista de testes a serem examinadas criada")
        if not args:  # Garantir que há uma lista
            args = []
        #print(executorDeTestes.gerarListaArquivosTeste(args))
        return executorDeTestes.gerarListaArquivosTeste(args)


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
        instanciaExecutorTestes = ExecutorTestes(self.pathFut)
        with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
            for resultado in executor.map(instanciaExecutorTestes.validarArquivoTeste, listaArquivosTestar):
                yield resultado


    def iniciarCriacaoRelatorio(self, resultadosValidacao:list, versaoRelatorio:str):
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
            geradorRelatorio.gerarRelatorioJson()  # Arquivo .json sempre é criado
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
        try:
            inicializadorSistema = self.iniciarSistema()
        except FileNotFoundError as e:
            logger.fatal(e)
            sys.exit(e)  # Sem esses arquivos o sistema não consegue rodar

        self.atualizarExecucaoValidator(inicializadorSistema)

        # Determinar número de threads
        numThreads = int(inicializadorSistema.returnValorSettings('max_threads'))  # Pela settings
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

                self.iniciarCriacaoRelatorio(resultadosValidacao, versaoRelatorio)  # (endTestes-startTestes) # Eventualmente enviar para o relatório

                # print("Arquivos encontrados:", listArquivosValidar)  # debug
                # print("Relatório de testes:", resultadosValidacao)  # debug

