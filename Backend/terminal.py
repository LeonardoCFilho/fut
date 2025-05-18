from pathlib import Path
from utils import *
from colorama import Style, Fore
import sys
import time
from main import acharCaminhoProjeto
import logging
logger = logging.getLogger(__name__)

# Para pintar o terminal
textoCiano = Fore.CYAN
fimTextoColorido = Style.RESET_ALL
flagAnimacaoSpinner = True

# Animação no terminal 
def spinner_animation():
    spinner = ['|', '/', '-', '\\']
    while flagAnimacaoSpinner:
        for symbol in spinner:
            # Animação
            sys.stdout.write(f'\r{symbol} Carregando...')
            sys.stdout.flush()
            time.sleep(0.2)

# Cria a thread e inicia a animação
def startSpinnerAnimation():
    import threading
    spinner_thread = threading.Thread(target=spinner_animation) # Thread so para a animação 
    spinner_thread.daemon = True  # Terminar com a main.py (Por segurança já que ela é encerrada antes)
    spinner_thread.start() 

# Executável
def mainMenu(args = None): # Quando não for executar pelo terminal mandar args
    # Não recebeu args => Ler do terminal
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
            print(obterDialogo('help'))

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
            try:
                gerarArquivoTeste(gerenciadorTestes)
            except PermissionError:
                print("O programa não tem permissão para criar o arquivo!")
            
        case "configuracoes":
            logger.info("Usuário solicitou o menu de configurações")
            print(obterDialogo('configuracoes'))

        case ["configuracoes", configuracaoSerLida]:
            logger.info("Usuário solicitou o valor de uma configuração")
            valorConfiguracao = obterValorConfiguracao(configuracaoSerLida)
            if valorConfiguracao:
                print(f"{textoCiano}Configurações:{fimTextoColorido} O valor atual de '{configuracaoSerLida}' é {valorConfiguracao}")
            else: 
                print("Configuração não reconhecida, verifique a escrita.")
            
        case ["configuracoes", configuracaoSerAlterada, novoValor]:
            logger.info("Usuário tentou alterar o valor de uma configuração")
            valorConfiguracao = obterValorConfiguracao(configuracaoSerAlterada)
            if valorConfiguracao:
                print("Alterando a configuração....")
                resultadoAlteracao = atualizarValorConfiguracao(configuracaoSerAlterada, novoValor)
                print(resultadoAlteracao)
                if "Erro" not in resultadoAlteracao:
                    print(f"Valor de '{configuracaoSerAlterada}' foi alterado de {valorConfiguracao} para {obterValorConfiguracao(configuracaoSerAlterada)}")
            else: 
                print("Configuração não reconhecida, verifique a escrita.")
            
        case _:
            logger.info("Iniciando testes")
            print("Iniciando testes!")

            # Caso ele estive apenas procurando ajuda
            if "help" in args or "ajuda" in args:
                print("Caso você estivesse procurando ajuda, digite 'fut --help'")

            # Iniciar testes em si
            try:
                entregaGradual = True
                startTestes = time.time()
                pctPronto = 0.1

                # Adicionando animação, para mais responsividade
                startSpinnerAnimation()

                # Responsivo
                if entregaGradual:
                    for resultado in iniciarExecucaoTestes(args,entregaGradual=entregaGradual):
                        # Mantendo o terminal responsivo
                        if (resultado[-1]) >= pctPronto:
                            resultadoLimpo = round(resultado[-1],1)
                            # Limpar o terminal
                            sys.stdout.write('\r')
                            sys.stdout.flush()
                            # Exibir progresso
                            print(f"{max(resultadoLimpo, (pctPronto))*100:.1f}% dos testes finalizados em {(time.time()-startTestes):.1f}s")
                            pctPronto = max(pctPronto+0.1, resultadoLimpo) # update
                    global flagAnimacaoSpinner
                    flagAnimacaoSpinner = False # Fim do processo => parar a animação
                    sys.stdout.write('\r')
                    sys.stdout.flush()

                # Entrega de uma vez
                else: 
                    list(iniciarExecucaoTestes(args,entregaGradual=entregaGradual))
                    
            except Exception as e:
                if 'nenhum arquivo de teste encontrado' in str(e).lower():
                    if len(args) == 0:
                        print("Nenhum arquivo YAML encontrado na pasta atual!")
                        print("Verifique a pasta atual ou a digitação do endereço dos testes")
                    else:
                        print("Caminhos fornecidos invalidos!")                    
                else:
                    print(f"Erro na execução dos testes: {e}")


if __name__ == "__main__":
    mainMenu()