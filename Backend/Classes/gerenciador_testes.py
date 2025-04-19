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
        raise ValueError()
      GerenciadorTestes(pathFut)
    return GerenciadorTestes._instance

    # Ideia: Cria um arquivo .yaml que segue o nosso template para caso de teste
    # P.s.: Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
  def criaTemplateYaml(self):
    templeteYaml = """test_id:  # (Obrigatório) Identificador único para cada teste (string).
description:  # (Recomendado) Descricao (string).
context: # Definição do contexto de validação.
  igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
    -  # IDs ou url dos IGs (Apenas 1 por linha).
  profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
    -  # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
  resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
    -  # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
caminho_instancia:  #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
  status: success  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
  error: []  #  (Obrigatório) Lista de erros esperados (lista de string).
  warning: []  #  (Obrigatório) Lista de avisos esperados (lista de string).
  fatal: [] #  #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
  information: []  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
  invariantes:  # (Opcional)"""
    with open("template.yaml", "w", encoding="utf-8") as file:
        file.write(templeteYaml)

  def iniciarSistema(self, args:list, versaoRelatorio = 'JSON'):
    from pathlib import Path

    # Criar o inicializador do sistema
    from Classes.inicializador_sistema import InicializadorSistema
    try:
      inicializadorSistema = InicializadorSistema(self.pathFut)
    except FileNotFoundError:
       # Descrever quais arquivos
       raise FileNotFoundError("Arquivos essenciais não encontrados")

    # Fazer a leitura dos argumentos recebidos
    from Classes.executor_teste import ExecutorTestes
    executorDeTestes = ExecutorTestes(self.pathFut)  
    try:
      if not args: # Garantir que há uma list
        args = []
      listArquivosValidar = executorDeTestes.listarArquivosValidar(args)
    except Exception as e:
      raise e

    # Determinar número de threads
    # Pela settings
    import os
    numThreads = int(inicializadorSistema.returnValorSettings('threads'))
    numThreads = min(numThreads, os.cpu_count())

    # Função para as threads
    def validarArquivo(arquivoValidar):
      executor = ExecutorTestes(self.pathFut)
      return executor.validarArquivoTeste(arquivoValidar)

    # Iniciar a validação
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
      resultadosValidacao = list(executor.map(validarArquivo, listArquivosValidar))

    #print("Arquivos encontrados:", listArquivosValidar)
    #print("Relatório de testes:", resultadosValidacao)

    # Criar o relatório
    from Classes.gerador_relatorio import GeradorRelatorios
    geradorRelatorio = GeradorRelatorios(resultadosValidacao)
    if versaoRelatorio.lower() == "json":
      geradorRelatorio.gerarRelatorioJson()
    #elif versaoRelatorio.lower() == "html":
    #  geradorRelatorio.gerarRelatorioHtml()