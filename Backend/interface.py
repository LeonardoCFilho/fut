"""
Interface feita para armazenar funções usadas pelo terminal e pela interface gráfica
"""
from Backend.Classes.gerenciador_testes import GerenciadorTestes
from pathlib import Path
import logging 
import sys
logger = logging.getLogger(__name__)


## Endereçamento
def acharCaminhoProjeto() -> Path:
    """
    Encontra o caminho do diretório do projeto onde o nome do diretório contém 'fut'.
    
    Returns:
        Path: O caminho do diretório do projeto.

    Raises:
        SystemExit: Se o diretório do projeto não for encontrado dentro do número máximo de iterações definidas.
    """
    maxIteracoes = 10
    numIteracoes = 0
    pathFut = Path(__file__)  # Diretório do arquivo atual
    while "fut" not in pathFut.name:  # Subir um nível se o diretório atual não for 'fut'
        pathFut = pathFut.parent
        numIteracoes +=1 
        if numIteracoes >= maxIteracoes:
            sys.exit("Problemas ao encontrar a pasta do projeto, renomeie-a para 'fut' ou 'fut-main'")
    return pathFut


def listarArquivosYaml(args=None):
    """
    Lista arquivos yaml ou na pasta atual ou de acrodo com args

    Args: 
        args: Argumentos de entrada para a criação a lista de testes a serem validados
        
    Returns:
        Lista com endereços dos arquivos de testes a serem testados (pode ser vazia)
    """
    return GerenciadorTestes.get_instance().prepararExecucaoTestes(args)


## Configurações
def obterValorConfiguracao(settingsBuscada:str):
    """
    Solicita o valor da configuração procurada
    
    Args:
        settingsBuscada (str): O nome da configuração buscada
    
    Returns:
        O valor da configuração OU None(caso de erro)
    """
    return GerenciadorTestes.get_instance().inicializador.returnValorSettings(settingsBuscada)


def atualizarValorConfiguracao(configuracaoSerAlterada:str, novoValor):
    """
    Solicita a alteração do valor de uma configuração
    
    Args:
        configuracaoSerAlterada (str): Nome da configuração a ser alterada
        novoValor: Novo valor desejado para a configuração
    
    Returns:
        Mensagem de sucesso OU mensagem de erro com justificativa"""
    try:
        GerenciadorTestes.get_instance().inicializador.alterarValorSetting(configuracaoSerAlterada, novoValor)
        return f"Configuração alterada com sucesso!"
    except Exception as e:
        return f"Erro ao alterar a configuração '{configuracaoSerAlterada}': {str(e)}"


## Testes
def iniciarExecucaoTestes(args, tipoRelatorio:str='JSON', entregaGradual:bool=False):
    """
    Recebe os args e tenta fazer o teste com eles
    
    Args:
        args: Os argumentos determinando os testes a serem feitos
        tipoRelatorio (str): Tipo do relatório que será feito (JSON ou HTML)
        entregaGradual (bool): Determina se a entrega será gradual OU súbita
    
    Returns:
        Gradual: n listas do tipo: [dict com informações do teste, porcentagem de testes finalizados]
        OU
        Súbita:  list com todos os valores (Súbito)
    
    Raises:
        ValueError: Quando a lista de testes criada com o 'args' é vazia
        ...
    """
    try: 
        logger.info("Teste de arquivos inicializado")
        gerenciadorTestes = GerenciadorTestes.get_instance()
        if entregaGradual: # Lidar com as entregas no frontend
            for resultado in gerenciadorTestes.executarTestesCompleto(args, tipoRelatorio, entregaGradual):
                yield resultado # é uma list, contém: dict com os dados do teste, % de testes finalizados
        else:
            list(gerenciadorTestes.executarTestesCompleto(args, tipoRelatorio, entregaGradual))

    except Exception as e:
        raise(e)


## Arquivos de teste
def gerarArquivoTeste(dictInformacoesTeste:dict = None, caminhoArquivo = None):
    """
    Cria um arquivo .yaml (preenchido ou não) que segue o nosso template para caso de teste
    Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
    
    Args:
        dictInformacoesTeste (dict): dict com os dados a serem inseridos no arquivo (opcional)
        caminhoArquivo: Caminho onde o arquivo será criado/escrito (opcional)
    
    Raises:
        PermissionError: Programa não tem permissão para a criação/escrita do arquivo
        ...
    """
    if not caminhoArquivo:  # Se o nome não é especificado => template
        caminhoArquivo = "template.yaml"
    logger.info(f"Arquivo de teste criado em {caminhoArquivo}")
    if not dictInformacoesTeste:  # Sem informações especificadas => template
        logger.info("Template de um arquivo de teste criado") 
        dictInformacoesTeste = {
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

        templateYaml = f"""test_id: {dictInformacoesTeste.get('test_id', '')} # (Obrigatório) Identificador único para cada teste (string).
description: {dictInformacoesTeste.get('description', '')} # (Recomendado) Descricao (string).
context: # Definição do contexto de validação.
    igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
        - {dictInformacoesTeste.get('igs', '')} # IDs ou url dos IGs (Apenas 1 por linha).
    profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
        - {dictInformacoesTeste.get('profiles', '')} # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
    resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
        - {dictInformacoesTeste.get('resources', '')} # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
caminho_instancia: {dictInformacoesTeste.get('caminho_instancia', '')} #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
    status: {dictInformacoesTeste.get('status', '')}  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
    error: [{dictInformacoesTeste.get('error', '')}]  #  (Obrigatório) Lista de erros esperados (lista de string).
    warning: [{dictInformacoesTeste.get('warning', '')}]  #  (Obrigatório) Lista de avisos esperados (lista de string).
    fatal: [{dictInformacoesTeste.get('fatal', '')}] #  #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
    information: [{dictInformacoesTeste.get('information', '')}]  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
    invariantes: {dictInformacoesTeste.get('invariantes', '')} # (Opcional)"""
    try:
        with open(caminhoArquivo, "w", encoding="utf-8") as file:  # Se caminhoArquivo já existia ele é sobrescrito
            file.write(templateYaml)
    except PermissionError as e:
        logger.error("Programa não tem permissão para criar o arquivo de teste requisitado")
        raise e
    except Exception as e:
        raise e  # improvável



## Dialogos
def obterDialogo(dialogoDesejado: str):
    """
    Armazena e retorna dialogos estilizados a serem usados
    
    Args:
        dialogoDesejado (str): Chave do dialogo a ser retornado
    
    Returns:
        str do dialogo ou None(caso de erro)
    """
    from colorama import Fore, Style, init
    # Variáveis para formatação de texto no terminal
    textoNegrito = Style.BRIGHT
    textoSublinhado = "\033[4m"
    textoHyperlink = "\033[4;34m"
    coresTerminal = {
        'vermelho': Fore.RED,
        'azul': Fore.BLUE,
        'ciano': Fore.CYAN,
        'magenta': Fore.MAGENTA,
    }
    fimTextoColorido = Style.RESET_ALL

    # Criando o dict com os dialogos
    dialogos = {}
    dialogos['help'] = f"""\n\n{textoNegrito}Ajuda:{fimTextoColorido}
Sistema de teste unitário para arquivos FHIR (versão 4.0.1)

{textoSublinhado}Leitura de casos de teste{fimTextoColorido}:
Sem argumentos, o comando fut executa todos os testes definidos por arquivos .yaml no diretório corrente.
Indicando arquivos específicos como fut teste/x.yml y.yml, ele executa o teste do arquivo em teste/x.yml e o teste do arquivo y.yml no diretório atual.
Usando curingas, por exemplo, fut patient-*.yml, ele executa todos os testes cujos nomes iniciam com patient- e terminam com .yml.

{textoSublinhado}Comandos{fimTextoColorido}:
{coresTerminal['ciano']}--help       {fimTextoColorido}\t\tAbri o menu atual e exibe mais informações sobre o programa
{coresTerminal['ciano']}gui          {fimTextoColorido}\t\tInicializa a interface gráfica (Ainda não foi implementada)
{coresTerminal['ciano']}template     {fimTextoColorido}\t\tGera um arquivo .yaml que segue o template de arquivos de teste
{coresTerminal['ciano']}configuracoes{fimTextoColorido}\t\tPermite a edição de configurações globais do sistema

Mais detalhes em: {textoHyperlink}https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md{fimTextoColorido}"""
    
    dialogos['configuracoes'] = f"""As configurações disponíveis para o Sistema de teste unitário para arquivos FHIR são as seguintes:

1. {textoSublinhado}[hardware]{fimTextoColorido}
 - {coresTerminal['ciano']}timeout (int):{fimTextoColorido} Define o tempo limite, em segundos, para a execução de cada teste. Exemplo de valor: `600` (10 minutos).
 - {coresTerminal['ciano']}max_threads (int):{fimTextoColorido} Especifica o número máximo de threads a serem usadas para executar os testes paralelamente. Exemplo de valor: `4`.

2. {textoSublinhado}[enderecamento]{fimTextoColorido}
 - {coresTerminal['ciano']}caminho_validator (str):{fimTextoColorido} Caminho personalizado para o arquivo `validator_cli.jar`, caso seja necessário sobrescrever o caminho padrão. Exemplo de valor: `~/Downloads/validator_cli.jar`.
 - {coresTerminal['ciano']}armazenar_saida_validator (bool):{fimTextoColorido} Indica se a saída do validador deve ser armazenada. Valores aceitos: `True` (armazenar saída) ou `False` (não armazenar). Exemplo de valor: `False`.

Essas configurações podem ser editadas com o comando `fut configuracoes <nome da configuração> <novo valor>`, permitindo ajustar o comportamento global do sistema conforme suas necessidades. Certifique-se de que os valores correspondam aos tipos esperados para garantir a atualização da configuração."""   

    return dialogos.get(dialogoDesejado, '') 