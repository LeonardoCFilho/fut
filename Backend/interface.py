"""
Interface feita para armazenar funções usadas pelo terminal e pela interface gráfica
"""
from Classes.gerenciador_testes import GerenciadorTestes
import logging 
logger = logging.getLogger(__name__)


## Configurações
def obterValorConfiguracao(settingsBuscada:str):
    """
    Solicita o valor da configuração procurada
    
    Args:
        settingsBuscada (str): O nome da configuração buscada
    
    Returns:
        O valor da configuração OU None(caso de erro)
    """
    return GerenciadorTestes.get_instance().iniciarSistema().returnValorSettings(settingsBuscada)


def atualizarValorConfiguracao(configuracaoSerAlterada:str, novoValor):
    """
    Solicita a alteração do valor de uma configuração
    
    Args:
        configuracaoSerAlterada (str): Nome da configuração a ser alterada
        novoValor: Novo valor desejado para a configuração
    
    Returns:
        Mensagem de sucesso OU mensagem de erro com justificativa"""
    try:
        GerenciadorTestes.get_instance().iniciarSistema().alterarValorSetting(configuracaoSerAlterada, novoValor)
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
    Cria um arquivo .yaml seguindo os padrões estabelecidos para o projeto
    
    Args:
        dictInformacoesTeste (dict): As informações a serem inseridas no arquivo (opcional)
        caminhoArquivo: Caminho onde será salvo o arquivo
    
    Raises:
        PermissionError: Quando o programa não tem permissão para criar/escrever o arquivo
        ...
        """
    gerenciadorTestes = GerenciadorTestes.get_instance()
    try:
        gerenciadorTestes.criaArquivoYamlTeste(dictInformacoesTeste, caminhoArquivo)
    except Exception as e:
        raise(e)


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