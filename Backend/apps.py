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

def mainMenu():
    import sys
    args = sys.argv[1:] 
    if len(args) == 1:
        args = str(args[0])
    match args:
        case "--help":
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
            from Classes.gerenciador_testes import GerenciadorTestes
            gerenciadorTestes = GerenciadorTestes.get_instance()
            gerenciadorTestes.criaTemplateYaml()
        case "configuracoes":
            listaConfiguracoes = [
                "timeout",
                "threads",
                "pathValidator_cli",
                "flagArmazenarSaidaValidator",
            ]
            print("Exibindo configurações:")
            pass
        case _:
            # Adicionar caso que o comando termine com 'help' ou 'ajuda'
            print("Iniciando testes!")
            if "help" in args or "ajuda" in args:
                print("Caso você estivesse procurando ajuda, digite 'fut --help'")

            sys.path.append("Backend/Classes")

            from Classes.gerenciador_testes import GerenciadorTestes
            gerenciadorTestes = GerenciadorTestes.get_instance(pathFut)

            gerenciadorTestes.iniciarSistema(args)


            
if __name__ == "__main__":
    mainMenu()