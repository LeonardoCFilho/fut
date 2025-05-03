from pathlib import Path
from Classes.inicializador_sistema import InicializadorSistema
from Classes.gerador_relatorio import GeradorRelatorios
from Classes.executor_teste import ExecutorTestes
from Classes.gerenciador_validator import GerenciadorValidator
from Classes.Exceptions import ExcecaoTemplate
import os
import concurrent.futures
import requests
import sys
import time
import logging
logger = logging.getLogger(__name__)

# Singleton
class GerenciadorTestes:
  _instance = None
  # Construtor
  def __init__(self, pathFut):
    if not GerenciadorTestes._instance:
      GerenciadorTestes._instance = self
      self.pathFut = pathFut
  # Retorna o objeto singleton da classe
  @staticmethod
  def get_instance(pathFut=None):
    if GerenciadorTestes._instance is None:
      if pathFut is None:
        raise ValueError("Caminho da pasta do projeto deve ser providenciada na primeira execução")
      GerenciadorTestes._instance = GerenciadorTestes(pathFut)
    return GerenciadorTestes._instance

  # Ideia: Faz download de um arquivo a partir de uma URL para o caminho especificado.
  # P.s.: Especificar o tipo de arquivo no nome do arquivo
  def baixaArquivoUrl(self, url, enderecoArquivo, maxTentativas = 3):
    numTentativas = 0
    while numTentativas < maxTentativas:
      try:
        logger.info(f"Tentando fazer o download de {enderecoArquivo}")
        # Iniciando request
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Lança exceção em caso de erro
  
        # Iniciando download
        enderecoArquivo = Path(enderecoArquivo)
        with enderecoArquivo.open("wb") as arquivo_baixado:
          for chunk in response.iter_content(chunk_size=8192):
            arquivo_baixado.write(chunk)
        logger.info("Download feito com sucesso")
        return 
  
      # Caso de erro, adicionar logs
      except Exception as e:
        numTentativas += 1 # Contabilizar tentativa
        if numTentativas < maxTentativas:
          logger.warning(f"Erro na tentativa {numTentativas+1} de download para {url}")
          print(f"Erro na tentativa {numTentativas+1} de download, reiniciando...")
          time.sleep(3)
        else:
          logger.error(f"Falha ao tentar fazer o download de {url} após {maxTentativas} tentativas. Erro: {str(e)}")
          raise e
                
    # Ideia: Cria um arquivo .yaml que segue o nosso template para caso de teste
    # P.s.: Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
  
  def criaYamlTeste(self, dadosArquivo = None, caminhoArquivo = None):
    logger.info(f"Arquivo de teste criado em {caminhoArquivo}")
    if not dadosArquivo:
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
    templeteYaml = f"""test_id: {dadosArquivo['test_id']} # (Obrigatório) Identificador único para cada teste (string).
description: {dadosArquivo['description']} # (Recomendado) Descricao (string).
context: # Definição do contexto de validação.
  igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
    - {dadosArquivo['igs']} # IDs ou url dos IGs (Apenas 1 por linha).
  profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
    - {dadosArquivo['profiles']} # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
  resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
    - {dadosArquivo['resources']} # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
caminho_instancia: {dadosArquivo['caminho_instancia']} #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
  status: {dadosArquivo['status']}  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
  error: [{dadosArquivo['error']}]  #  (Obrigatório) Lista de erros esperados (lista de string).
  warning: [{dadosArquivo['warning']}]  #  (Obrigatório) Lista de avisos esperados (lista de string).
  fatal: [{dadosArquivo['fatal']}] #  #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
  information: [{dadosArquivo['information']}]  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
  invariantes: {dadosArquivo['invariantes']} # (Opcional)"""
    if caminhoArquivo:
      with open(caminhoArquivo, "w", encoding="utf-8") as file:
        file.write(templeteYaml)
    else: 
      with open("template.yaml", "w", encoding="utf-8") as file:
        file.write(templeteYaml)

  def iniciarSistema(self):
    # Criar o inicializador do sistema
    try:
      logger.info("Preparando para a execução de testes")
      return InicializadorSistema(self.pathFut)
    except FileNotFoundError as e:
       logger.fatal(f"Arquivos essencial '{e.args[0]}' não foi encontrado")
       raise FileNotFoundError(f"Arquivos essencial '{e.args[0]}' não foi encontrado")

  def prepararExecucaoTestes(self,args):
    # Fazer a leitura dos argumentos recebidos
    executorDeTestes = ExecutorTestes(self.pathFut)  
    logger.info("Lista de testes a serem examinadas criada")
    if not args: # Garantir que há uma list
      args = []
    #print(executorDeTestes.listarArquivosValidar(args))
    return executorDeTestes.listarArquivosValidar(args)

  def iniciarCriacaoRelatorio(self, resultadosValidacao, versaoRelatorio):
    # Criar o relatório
    logger.info(f"Iniciando a criação do relatório, relatório selecionado é do tipo {versaoRelatorio}")
    geradorRelatorio = GeradorRelatorios(resultadosValidacao)
    geradorRelatorio.gerarRelatorioJson() # Arquivo .json sempre é criado
    #if versaoRelatorio.lower() == "json":
    #  print("Relatório JSON criado!") 
    #if versaoRelatorio.lower() == "html":
    #  geradorRelatorio.gerarRelatorioHtml()

  def executarThreadsTeste(self, args, numThreads):
    # Função para as threads
    def validarArquivo(arquivoValidar):
      executorTesteThreads = ExecutorTestes(self.pathFut)
      return executorTesteThreads.validarArquivoTeste(arquivoValidar)

    # Iniciar a validação
    logger.info("Iniciando a execução dos testes requisitados")
    with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
      return list(executor.map(validarArquivo, self.prepararExecucaoTestes(args)))


  def executarTestes(self, args:list, versaoRelatorio = 'JSON'):
    inicializadorSistema = self.iniciarSistema()

    # Garantir que o validator esteja atualizado
    atualizarValidator = GerenciadorValidator(self.pathFut)
    try:
      atualizarValidator.atualizarValidatorCli(inicializadorSistema.pathValidator)
    except ExcecaoTemplate as e:
      logger.fatal(f"O arquivo do validator_cli é inválido: {e}")
      sys.exit("Arquivo validator_cli é inválido, verifique seu download ou considere utilizar o validator padrão")
    except requests.exceptions.ConnectionError as e:
      pass # Já está registrado no log e não é um erro crítico
    except Exception as e:
      logger.error(f"Erro ao atualizar o validator: {e}") # Programa continua executando, mas não usar a versçao mais recente do validator

    # Determinar número de threads
    numThreads = int(inicializadorSistema.returnValorSettings('max_threads')) # Pela settings
    numThreads = min(numThreads, os.cpu_count()) # Não criar mais threads que o computador tem
    
    startTestes = time.time()
    resultadosValidacao = self.executarThreadsTeste(args, numThreads)
    endTestes = time.time()
    
    logger.info("Testes listados completos")
    print("Testes finalizados!")

    self.iniciarCriacaoRelatorio(resultadosValidacao, versaoRelatorio) 

    #print("Arquivos encontrados:", listArquivosValidar) # debug
    #print("Relatório de testes:", resultadosValidacao) # debug