# Arquivo feito para armazenar funções usadas pelo terminal e pelo Frontend
from pathlib import Path
from Classes.gerenciador_testes import GerenciadorTestes
from Classes.inicializador_sistema import InicializadorSistema
import logging 
logger = logging.getLogger(__name__)

# Retorna o valor da configuração buscada ou None(Configuração não foi encontrada no settings.ini)
def obterValorConfiguracao(settingsBuscada):
    objetoLerConfiguracoes = InicializadorSistema(GerenciadorTestes.get_instance().pathFut)
    return objetoLerConfiguracoes.returnValorSettings(settingsBuscada)

# Tenta alterar uma configuração
# Retorna ou a mensagem de sucesso ou uma Exception
def atualizarValorConfiguracao(configuracaoSerAlterada, novoValor):
    objetoAlterarConfiguracoes = InicializadorSistema(GerenciadorTestes.get_instance().pathFut)
    try:
        objetoAlterarConfiguracoes.alterarValorSetting(configuracaoSerAlterada, novoValor)
        return f"Configuração alterada com sucesso!"
    except Exception as e:
        return f"Erro ao alterar a configuração '{configuracaoSerAlterada}': {str(e)}"

# Recebe uma lista e faz a validação dos arquivos
# Retornar ValueError quando a lista de testes é vazia
def iniciarExecucaoTestes(args, tipoRelatorio='JSON', entregaGradual=False):
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

# Cria ou um template do arquivo de teste (nenhuma entrada enviada) ou um .yaml preenchido
# Se o caminho não foi especificado o arquivo é criado na pasta de execução
# Pode retornar PermissionError
def gerarArquivoTeste(dictInformacoesTeste:dict = None, caminhoArquivo = None):
    gerenciadorTestes = GerenciadorTestes.get_instance()
    try:
        gerenciadorTestes.criaArquivoYamlTeste(dictInformacoesTeste, caminhoArquivo)
    except Exception as e:
        raise(e)

# Retorna ou o conteudo desejado ou uma string vazia (Caso de erro)
def obterDialogo(dialogoDesejado: str):
    from colorama import Fore, Style, init
    # Variáveis para formatação de texto no terminal
    textoNegrito = Style.BRIGHT
    textoSublinhado = "\033[4m"
    textoVermelho = Fore.RED
    textoAzul = Fore.BLUE
    textoCiano = Fore.CYAN
    textoMagenta = Fore.MAGENTA
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
{textoCiano}--help       {fimTextoColorido}\t\tAbri o menu atual e exibe mais informações sobre o programa
{textoCiano}gui          {fimTextoColorido}\t\tInicializa a interface gráfica (Ainda não foi implementada)
{textoCiano}template     {fimTextoColorido}\t\tGera um arquivo .yaml que segue o template de arquivos de teste
{textoCiano}configuracoes{fimTextoColorido}\t\tPermite a edição de configurações globais do sistema

Mais detalhes em: \033[4;34mhttps://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md{fimTextoColorido} """
    
    dialogos['configuracoes'] = f"""As configurações disponíveis para o Sistema de teste unitário para arquivos FHIR são as seguintes:

1. {textoSublinhado}[hardware]{fimTextoColorido}
 - {textoCiano}timeout (int):{fimTextoColorido} Define o tempo limite, em segundos, para a execução de cada teste. Exemplo de valor: `600` (10 minutos).
 - {textoCiano}max_threads (int):{fimTextoColorido} Especifica o número máximo de threads a serem usadas para executar os testes paralelamente. Exemplo de valor: `4`.

2. {textoSublinhado}[enderecamento]{fimTextoColorido}
 - {textoCiano}caminho_validator (str):{fimTextoColorido} Caminho personalizado para o arquivo `validator_cli.jar`, caso seja necessário sobrescrever o caminho padrão. Exemplo de valor: `~/Downloads/validator_cli.jar`.
 - {textoCiano}armazenar_saida_validator (bool):{fimTextoColorido} Indica se a saída do validador deve ser armazenada. Valores aceitos: `True` (armazenar saída) ou `False` (não armazenar). Exemplo de valor: `False`.

Essas configurações podem ser editadas com o comando `fut configuracoes <nome da configuração> <novo valor>`, permitindo ajustar o comportamento global do sistema conforme suas necessidades. Certifique-se de que os valores correspondam aos tipos esperados para garantir a atualização da configuração."""   

    return dialogos.get(dialogoDesejado, '') 