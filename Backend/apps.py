from pathlib import Path

# Caminhos utilizados no nosso projeto
maxIteracoes = 10
numIteracoes = 0
pathFut = Path(__file__)  # Diretório do arquivo atual
while "fut" not in pathFut.name:  # Subir um nível se o diretório atual não for 'fut'
    pathFut = pathFut.parent
    numIteracoes +=1 

    if numIteracoes >= maxIteracoes:
        raise FileNotFoundError("Problemas ao encontrar a pasta do projeto, renomeie-a para 'fut' ou 'fut-main'")

# Implementar colorama dps

# Variáveis para formatação de texto no terminal
textoNegrito = "\033[1m"
textoSublinhado = "\033[4m"
textoVermelho = "\033[31m"
textoAzul = "\033[34m"
textoCiano = "\033[36m"
textoMagenta = "\033[35m"
fimTextoColorido = "\033[0m"

listaConfiguracoes = [
    "timeout",
    "threads",
    "pathValidator_cli",
    "flagArmazenarSaidaValidator",
]

def mainMenu(args = None):
    import sys
    # Ou le o terminal para receber args, ou recebe antes da execução
    if not args:
        args = sys.argv[1:] 
        if len(args) == 1:
            args = str(args[0])
    # Preparar para execução
    from Classes.gerenciador_testes import GerenciadorTestes
    gerenciadorTestes = GerenciadorTestes.get_instance(pathFut)
    from Classes.inicializador_sistema import InicializadorSistema
    objetoAlterarConfiguracoes = InicializadorSistema(pathFut)
    # Opções a serem selecionadas
    match args:
        case ["--help"]:
            stringHelp=f"""\n\n{textoNegrito}Ajuda:{fimTextoColorido}
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
            print(stringHelp)
        case "gui":
            print("A interface gráfica será implementada em breve!")
            # print("Abrindo interface....")
            # from Frontend.ClasseFrontend import frontend
            # frontend()
            # print("Finalizando processo...")
        case "template":
            print("Criando template...")
            gerenciadorTestes.criaTemplateYaml()
        case "configuracoes":
            stringConfiguracoes = f"""As configurações disponíveis para o Sistema de teste unitário para arquivos FHIR são as seguintes:

1. {textoSublinhado}[hardware]{fimTextoColorido}
 - {textoCiano}timeout (int):{fimTextoColorido} Define o tempo limite, em segundos, para a execução de cada teste. Exemplo de valor: `600` (10 minutos).
 - {textoCiano}threads (int):{fimTextoColorido} Especifica o número máximo de threads a serem usadas para executar os testes paralelamente. Exemplo de valor: `4`.

2. {textoSublinhado}[enderecamento]{fimTextoColorido}
 - {textoCiano}pathValidator_cli (str):{fimTextoColorido} Caminho personalizado para o arquivo `validator_cli.jar`, caso seja necessário sobrescrever o caminho padrão. Exemplo de valor: `~/Downloads/validator_cli.jar`.
 - {textoCiano}flagArmazenarSaidaValidator (bool):{fimTextoColorido} Indica se a saída do validador deve ser armazenada. Valores aceitos: `True` (armazenar saída) ou `False` (não armazenar). Exemplo de valor: `False`.

Essas configurações podem ser editadas com o comando `fut configuracoes <nome da configuração> <novo valor>`, permitindo ajustar o comportamento global do sistema conforme suas necessidades. Certifique-se de que os valores correspondam aos tipos esperados para garantir a atualização da configuração."""         
            print(stringConfiguracoes)
        case ["configuracoes", lerValorConfiguracao]:
            if str(lerValorConfiguracao) in listaConfiguracoes:
                valorConfiguracao = objetoAlterarConfiguracoes.returnValorSettings(lerValorConfiguracao)
                print(f"{textoCiano}Configurações:{fimTextoColorido} O valor atual de '{lerValorConfiguracao}' é {valorConfiguracao}")
            else: 
                print("Configuração não reconhecida, verifique a escrita.")
        case ["configuracoes", configuracaoSerAlterada, novoValor]:
            if str(configuracaoSerAlterada) in listaConfiguracoes:
                from Classes.inicializador_sistema import InicializadorSistema
                objetoAlterarConfiguracoes = InicializadorSistema(pathFut)
                try:
                    valorAntigo = objetoAlterarConfiguracoes.returnValorSettings(configuracaoSerAlterada)
                    objetoAlterarConfiguracoes.alterarValorSetting(configuracaoSerAlterada, novoValor)
                    print(f"Configuração alterada com sucesso!\nValor de {configuracaoSerAlterada} foi alterado de {valorAntigo} para {novoValor}")
                except Exception as e: # em caso de erro nada acontece em settings.ini
                    print(f"Erro: {e}")
            else: 
                print("Configuração não reconhecida, verifique a escrita.")
        case _:
            # Adicionar caso que o comando termine com 'help' ou 'ajuda'
            print("Iniciando testes!")
            if "help" in args or "ajuda" in args:
                print("Caso você estivesse procurando ajuda, digite 'fut --help'")

            sys.path.append("Backend/Classes")

            

            gerenciadorTestes.iniciarSistema(args)


            
if __name__ == "__main__":
    mainMenu()