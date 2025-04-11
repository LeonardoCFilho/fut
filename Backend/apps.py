import sys
from pathlib import Path

# Caminhos utilizados no nosso projeto
pathFut = Path(__file__)  # Diretório do arquivo atual
while "fut" not in pathFut.name:  # Subir um nível se o diretório atual for 'fut'
    pathFut = pathFut.parent

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
    # Retrieve arguments passed from the command line
    args = sys.argv[1:]  # Exclude the script name (sys.argv[0])
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
{textoCiano}--help  {fimTextoColorido}\t\tAbri o menu atual e exibe mais informações sobre o programa
{textoCiano}gui     {fimTextoColorido}\t\tInicializa a interface gráfica (Ainda não foi implementada)
{textoCiano}template{fimTextoColorido}\t\tGera um arquivo .yaml que segue o template de arquivos de teste

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
            gerenciadorTestes = GerenciadorTestes()
            gerenciadorTestes.criaTemplateYaml()
        case _:
            # Adicionar caso que o comando termine com 'help' ou 'ajuda'
            print("Iniciando testes!")
            from Classes.executor_teste import ExecutorTestes
            executorDeTestes = ExecutorTestes(pathFut)  
            try:
                if not args: # Garantir que há uma list
                    args = []
                executorDeTestes.receberArquivosValidar(args)
            except Exception as e:
                print(f"Erro: {e}")
            
if __name__ == "__main__":
    mainMenu()