from pathlib import Path
from utils import *
from colorama import Style, Fore
import sys
from main import acharCaminhoProjeto
import logging
logger = logging.getLogger(__name__)

textoCiano = Fore.CYAN
fimTextoColorido = Style.RESET_ALL

def mainMenu(args = None):
    # Ou le o terminal para receber args, ou recebe antes da execução
    if not args:
        args = sys.argv[1:] 
        if len(args) == 1:
            args = str(args[0])

    # Preparar para execução
    gerenciadorTestes = GerenciadorTestes.get_instance(acharCaminhoProjeto())
    #print(args) # debug
    # Opções a serem selecionadas
    match args:
        case "--help":
            logger.info("Usuário solicitou o menu de ajuda")
            print(returnDialogo('help'))
        case "gui":
            print("A interface gráfica será implementada em breve!")
            # logger.info("Iniciando a interface gráfica")
            # print("Abrindo interface....")
            # from Frontend.ClasseFrontend import frontend
            # frontend()
            # logger.info("Encerrando a interface gráfica")
            # print("Finalizando processo...")
        case "template":
            logger.info("Usuário criou um template")
            print("Criando template...")
            criaArquivoTeste(gerenciadorTestes)
        case "configuracoes":
            logger.info("Usuário solicitou o menu de configurações")
            print(returnDialogo('configuracoes'))
        case ["configuracoes", configuracaoSerLida]:
            logger.info("Usuário solicitou o valor de uma configuração")
            valorConfiguracao = lerValorConfiguracao(configuracaoSerLida)
            if valorConfiguracao:
                print(f"{textoCiano}Configurações:{fimTextoColorido} O valor atual de '{configuracaoSerLida}' é {valorConfiguracao}")
            else: 
                print("Configuração não reconhecida, verifique a escrita.")
        case ["configuracoes", configuracaoSerAlterada, novoValor]:
            logger.info("Usuário tentou alterar o valor de uma configuração")
            valorConfiguracao = lerValorConfiguracao(configuracaoSerAlterada)
            if valorConfiguracao:
                print("Alterando a configuração....")
                resultadoAlteracao = alterarValorConfiguracao(configuracaoSerAlterada, novoValor)
                print(resultadoAlteracao)
                if "Erro" not in resultadoAlteracao:
                    print(f"Valor de '{configuracaoSerAlterada}' foi alterado de {valorConfiguracao} para {lerValorConfiguracao(configuracaoSerAlterada)}")
            else: 
                print("Configuração não reconhecida, verifique a escrita.")
        case _:
            print("Iniciando testes!")

            # Caso ele estive apenas procurando ajuda
            if "help" in args or "ajuda" in args:
                print("Caso você estivesse procurando ajuda, digite 'fut --help'")
            realizarTestes(args)
            #try:
            #    realizarTestes(args)
            #except Exception as e:
            #    print(f"Erro na execução dos testes: {e}")


if __name__ == "__main__":
    mainMenu()