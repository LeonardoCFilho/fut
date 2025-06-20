from Backend.dialogos_sistema import DialogosSistema
from Backend.fachada_sistema import FachadaSistema
import streamlit.web.cli as stcli
import subprocess
import threading
import logging
import time
import sys
import os

logger = logging.getLogger(__name__)


class TerminalUI:
    """Interface de linha de comando para interação com o sistema."""
    
    # Construtor
    def __init__(self):
        """Inicializa a interface do terminal e os componentes necessários."""
        self.fachada = FachadaSistema()
        self._spinner_ativo = False
        self._thread_spinner = None


    def _mostrar_spinner(self):
        """Exibe uma animação de carregamento no terminal."""
        simbolos_spinner = ['|', '/', '-', '\\']
        while self._spinner_ativo:
            for simbolo in simbolos_spinner:
                if not self._spinner_ativo:
                    break
                sys.stdout.write(f'\r{simbolo} Carregando...')
                sys.stdout.flush()
                time.sleep(0.2)
        sys.stdout.write('\r' + ' ' * 20 + '\r')
        sys.stdout.flush()


    def iniciar_spinner(self):
        """Inicia a animação de carregamento."""
        if self._thread_spinner and self._thread_spinner.is_alive():
            return
        
        self._spinner_ativo = True
        self._thread_spinner = threading.Thread(target=self._mostrar_spinner, daemon=True)
        self._thread_spinner.start()


    def parar_spinner(self, tempo_espera: float = 0.1):
        """Para a animação de carregamento.

        Args:
            tempo_espera (float): Tempo máximo de espera para finalizar o spinner.
        """
        if not self._spinner_ativo:
            return
            
        self._spinner_ativo = False
        if self._thread_spinner:
            self._thread_spinner.join(timeout=tempo_espera)


    def _mostrar_ajuda(self):
        """Exibe informações de ajuda."""
        logger.info("Usuário solicitou o menu de ajuda")
        print(DialogosSistema.obter_dialogo('help'))


    def _mostrar_interface_grafica(self):
        """Inicia a execução do streamlit - versão que realmente funciona."""
        logger.info("Iniciando a GUI")

        # Get the frontend script path
        script_frontend = self.fachada.obter_caminho('script_frontend')

        if not script_frontend.exists():
            print(f"ERROR: Frontend script not found: {script_frontend}")
            return

        # Check if running as PyInstaller executable
        is_frozen = getattr(sys, 'frozen', False)

        if is_frozen:
            try:
                # Change to the script directory
                script_dir = script_frontend.parent
                os.chdir(str(script_dir))
                
                print(f"Changed to directory: {os.getcwd()}")
                print(f"Script to run: {script_frontend.name}")
                print("Web interface will be available at: http://127.0.0.1:8501")
                                
                
                # Set up sys.argv as if streamlit run was called
                original_argv = sys.argv.copy()
                sys.argv = [
                    "streamlit",
                    "run",
                    str(script_frontend),
                    "--global.developmentMode=false"
                ]
                
                try:
                    # Run streamlit directly
                    stcli.main()
                finally:
                    # Restore original sys.argv
                    sys.argv = original_argv
                    
            except KeyboardInterrupt:
                print("Encerrando a GUI...")
                sys.exit(0)
            except Exception as e:
                print(f"Error starting Streamlit: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            # Direct Python execution using subprocess (non-frozen)
            try:
                cmd = ["streamlit", "run", str(script_frontend)]
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print("Encerrando a GUI...")
                sys.exit(0)


    def _criar_template(self):
        """Cria um template de teste."""
        logger.info("Usuário criou um template")
        print("Criando template...")
        try:
            self.fachada.gerar_arquivo_teste()
            print("Template criado com sucesso!")
        except PermissionError:
            print("Erro: O programa não tem permissão para criar o arquivo!")
        except Exception as e:
            print(f"Erro ao criar template: {e}")


    def _mostrar_menu_configuracoes(self):
        """Exibe o menu de configurações."""
        logger.info("Usuário solicitou o menu de configurações")
        print(DialogosSistema.obter_dialogo('configuracoes'))


    def _ler_configuracao(self, nome_config: str):
        """Lê e exibe o valor de uma configuração.

        Args:
            nome_config (str): Nome da configuração a ser consultada.
        """
        logger.info(f"Usuário solicitou o valor da configuração: {nome_config}")
        valor = self.fachada.obter_configuracao(nome_config)
        
        if valor is not None:
            ciano = DialogosSistema.get_ansi_code("ciano")
            resetar = DialogosSistema.get_ansi_code("fimTextoColorido")
            print(f"{ciano}Configurações:{resetar} O valor atual de '{nome_config}' é {valor}")
        else:
            print(f"Erro: Configuração '{nome_config}' não encontrada. Verifique a escrita.")


    def _atualizar_configuracao(self, nome_config: str, novo_valor: str):
        """Atualiza o valor de uma configuração.

        Args:
            nome_config (str): Nome da configuração a ser alterada.
            novo_valor (str): Novo valor da configuração.
        """
        logger.info(f"Usuário tentou alterar a configuração: {nome_config}")
        valor_antigo = self.fachada.obter_configuracao(nome_config)
        
        if valor_antigo is None:
            print(f"Erro: Configuração '{nome_config}' não encontrada. Verifique a escrita.")
            return

        try:
            print("Alterando a configuração...")
            if self.fachada.atualizar_configuracao(nome_config, novo_valor):
                valor_confirmado = self.fachada.obter_configuracao(nome_config)
                ciano = DialogosSistema.get_ansi_code("ciano")
                resetar = DialogosSistema.get_ansi_code("fimTextoColorido")
                print(f"{ciano}Configurações:{resetar} Valor de '{nome_config}' alterado de {valor_antigo} para {valor_confirmado}")
            else:
                print("Falha ao alterar a configuração.")
        except Exception as e:
            print(f"Erro: {e}")


    def _executar_testes(self, argumentos: list[str]):
        """Executa os testes e exibe o progresso.

        Args:
            argumentos (List[str]): Lista de argumentos para execução dos testes.
        """
        try:
            tempo_inicio = time.time()
            progresso_minimo = 0.1

            self.iniciar_spinner()
            
            for resultado in self.fachada.executar_testes_com_entrega_gradual(argumentos):
                if resultado[-1] >= progresso_minimo:
                    progresso = round(resultado[-1], 1)
                    tempo_decorrido = time.time() - tempo_inicio
                    sys.stdout.write('\r' + ' ' * 20 + '\r')
                    print(f"{max(progresso, progresso_minimo) * 100:.1f}% dos testes finalizados em {tempo_decorrido:.1f}s")
                    progresso_minimo = max(progresso_minimo + 0.1, progresso)
            
            self.parar_spinner()
            print("Testes finalizados com sucesso!")

        except Exception as e:
            self.parar_spinner()
            print(f"Erro na execução dos testes: {e}")


    def menu_principal(self, argumentos: list[str] = None):
        """Exibe o menu principal e processa comandos.

        Args:
            argumentos (Optional[List[str]]): Lista de argumentos ou entrada do terminal.
        """
        if not argumentos:
            argumentos = sys.argv[1:]

        comando = argumentos[0] if argumentos else ''
        comando = comando.lower()
        #print(comando)
        match comando:
            case "--help":
                self._mostrar_ajuda()
            case "gui":
                self._mostrar_interface_grafica()
            case "template":
                self._criar_template()
            case "configuracoes":
                if len(argumentos) == 1:
                    self._mostrar_menu_configuracoes()
                elif len(argumentos) == 2:
                    self._ler_configuracao(argumentos[1])
                elif len(argumentos) == 3:
                    self._atualizar_configuracao(argumentos[1], argumentos[2])
                else:
                    print("Uso: fut configuracoes [nome] [valor]")
            case _:
                print("Iniciando testes!")
                if any(x in ["help", "ajuda"] for x in argumentos):
                    print("Caso você estivesse procurando ajuda, digite 'fut --help'")
                self._executar_testes(argumentos)
