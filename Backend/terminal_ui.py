from Backend.fachada_sistema import FachadaSistema
import sys
import time
import threading
import logging
logger = logging.getLogger(__name__)

class TerminalUI:
    def __init__(self):
        # Instancia da fachada que centraliza as operações do sistema
        self.fachada = FachadaSistema()
        # Variaveis para a aparencia e responsividade do terminal
        self.flagAnimacaoSpinner = True
        self.threadAnimacaoSpinner = None


    # Animação no terminal 
    def controleAnimacao(self, status:str='start', timeout: float = 1.0):
        """
        Controla a animação do spinner no terminal.
        
        """
        def spinner_animation():
            spinner = ['|', '/', '-', '\\']
            while self.flagAnimacaoSpinner:
                for symbol in spinner:
                    sys.stdout.write(f'\r{symbol} Carregando...')
                    sys.stdout.flush()
                    time.sleep(0.2)
            # Terminou a animação => limpar o terminal
            sys.stdout.write('\r')
            sys.stdout.flush()
        
        match status:
            case 'start':
                self.flagAnimacaoSpinner = True 
                self.threadAnimacaoSpinner = threading.Thread(target=spinner_animation)
                self.threadAnimacaoSpinner.daemon = True  # Garante que a thread seja finalizada com a main thread
                self.threadAnimacaoSpinner.start()
            case 'end':
                self.flagAnimacaoSpinner = False
                if self.threadAnimacaoSpinner is not None:
                    self.threadAnimacaoSpinner.join(timeout=timeout) # Garantir sincronia
                sys.stdout.write('\r')
                sys.stdout.flush()


    # Executável
    #TODO implementar a GUI
    def mainMenu(self, args:list|str|None = None):
        """
        Exibe o menu principal e encaminha as ações conforme os argumentos fornecidos.
        
        Args:
            args: Lista de argumentos ou string, caso a execução seja pelo terminal.
        """
        # Se nenhum argumento é passado, utiliza os argumentos da linha de comando
        if not args:
            args = sys.argv[1:]
        # Garantir que é uma list
        if isinstance(args, str):
            args = [args]
        
        match args:
            case ["--help"]:
                logger.info("Usuário solicitou o menu de ajuda")
                print(self.fachada.obterDialogo('help'))

            case ["gui"]:
                print("A interface gráfica será implementada em breve!")

            case ["template"]:
                logger.info("Usuário criou um template")
                print("Criando template...")
                try:
                    self.fachada.gerarArquivoTeste()
                except PermissionError:
                    print("O programa não tem permissão para criar o arquivo!")

            case ["configuracoes"]:
                logger.info("Usuário solicitou o menu de configurações")
                print(self.fachada.obterDialogo('configuracoes'))

            case ["configuracoes", configuracaoSerLida]:
                self._terminalConfiguracoes(configuracaoSerLida)

            case ["configuracoes", configuracaoSerAlterada, novoValor]:
                self._terminalConfiguracoes(configuracaoSerAlterada, novoValor)

            case _:
                logger.info("Iniciando testes")
                print("Iniciando testes!")
                if any(x in ["help", "ajuda"] for x in args):
                    print("Caso você estivesse procurando ajuda, digite 'fut --help'")
                self._testesTerminal(args)


    def _testesTerminal(self, args: str | list):
        """
        Executa os testes no terminal em modo interativo, exibindo o progresso.
        
        Args:
            args (str | list): Caminho(s) dos arquivos de teste.
        """
        try:
            entregaGradual = True
            startTestes = time.time()
            pctPronto = 0.1

            # Inicia a animação para melhorar a sensação de responsividade
            self.controleAnimacao('start')

            if entregaGradual:
                for resultado in self.fachada.iniciarExecucaoTestes(args, entregaGradual=entregaGradual):
                    # Atualiza o progresso e exibe ao usuário
                    if resultado[-1] >= pctPronto:
                        resultadoLimpo = round(resultado[-1], 1)
                        sys.stdout.write('\r')
                        sys.stdout.flush()
                        print(f"{max(resultadoLimpo, pctPronto) * 100:.1f}% dos testes finalizados em {(time.time() - startTestes):.1f}s")
                        pctPronto = max(pctPronto + 0.1, resultadoLimpo)
                self.controleAnimacao('end')
            else: 
                list(self.fachada.iniciarExecucaoTestes(args, entregaGradual=entregaGradual))
        except Exception as e:
            self.controleAnimacao('end')
            # Tratamento simplificado de erros para exibição no terminal:
            if 'nenhum arquivo de teste encontrado' in str(e).lower():
                if not args:
                    print("Nenhum arquivo YAML encontrado na pasta atual!")
                    print("Verifique se o diretório contém arquivos com extensão '.yaml'.")
                else:
                    print("Caminhos fornecidos inválidos!")
                    print("Confirme se os caminhos digitados existem e estão corretos.")
                print("Para mais detalhes, digite 'fut --help'")
            else:
                print(f"Erro na execução dos testes: {e}")


    def _terminalConfiguracoes(self, nomeConfiguracao: str, novoValor: str = None):
        """
        Exibe ou altera o valor de uma configuração através do terminal.

        Args:
            nomeConfiguracao (str): Nome da configuração.
            novoValor (str): Novo valor para a configuração (se informado).
        """
        if not novoValor:  # Leitura da configuração
            logger.info("Usuário solicitou o valor de uma configuração")
            valorConfiguracao = self.fachada.obterValorConfiguracao(nomeConfiguracao)
            if valorConfiguracao:
                print(f"{self.fachada._returnCodigoANSI("ciano")}Configurações:{self.fachada._returnCodigoANSI("fimTextoColorido")} O valor atual de '{nomeConfiguracao}' é {valorConfiguracao}")
            else:
                print("Configuração não reconhecida, verifique a escrita.")
        else:  # Atualização da configuração
            logger.info("Usuário tentou alterar o valor de uma configuração")
            valorConfiguracao = self.fachada.obterValorConfiguracao(nomeConfiguracao)
            if valorConfiguracao:
                print("Alterando a configuração....")
                resultadoAlteracao = self.fachada.atualizarValorConfiguracao(nomeConfiguracao, novoValor)
                print(resultadoAlteracao)
                if "Erro" not in resultadoAlteracao:
                    valorConfiguracaoAtualizado = self.fachada.obterValorConfiguracao(nomeConfiguracao)
                    print(f"Valor de '{nomeConfiguracao}' foi alterado de {valorConfiguracao} para {valorConfiguracaoAtualizado}")
            else:
                print("Configuração não reconhecida, verifique a escrita.")