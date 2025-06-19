from Backend.dialogos_sistema import DialogosSistema
from Backend.fachada_sistema import FachadaSistema
import subprocess
import threading
import streamlit
import logging
import time
import sys

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
        """Inicia a execução do streamlit - versão para PyInstaller e execução direta via Python."""
        import os
        import sys
        import subprocess
        from pathlib import Path

        # Get the frontend script path
        script_frontend = self.fachada.obter_caminho('script_frontend')
        print(self.fachada.obter_caminho('raiz'))
        print(script_frontend, script_frontend.exists())

        # Check if running as PyInstaller executable
        is_frozen = getattr(sys, 'frozen', False)

        if is_frozen:
            # PyInstaller executable
            print("Starting Streamlit from PyInstaller executable...")
            print("Web interface will be available at: http://localhost:8501")
            
            # Set Streamlit configuration via environment variables
            os.environ['STREAMLIT_SERVER_PORT'] = '8501'
            os.environ['STREAMLIT_SERVER_ADDRESS'] = '127.0.0.1'
            os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
            os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
            os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
            
            try:
                # Method 1: Direct Streamlit bootstrap (most reliable for PyInstaller)
                try:
                    print("Attempting to start Streamlit server directly...")
                    
                    import streamlit.web.bootstrap as bootstrap
                    from streamlit import config
                    import click
                    
                    # Set configuration options before starting
                    config.set_option('server.port', 8501)
                    config.set_option('server.address', '127.0.0.1')
                    config.set_option('server.headless', True)
                    config.set_option('browser.gatherUsageStats', False)
                    config.set_option('logger.level', 'error')
                    config.set_option('server.enableCORS', False)
                    config.set_option('server.enableXsrfProtection', False)
                    
                    # Create a click context for streamlit
                    @click.command()
                    @click.argument('target', required=True)
                    @click.option('--server.port', default=8501)
                    @click.option('--server.address', default='127.0.0.1')
                    @click.option('--server.headless', default=True)
                    @click.option('--browser.gatherUsageStats', default=False)
                    def run_streamlit(target, **kwargs):
                        bootstrap.run(target, '', [], {})
                    
                    # Use click context
                    with click.Context(run_streamlit) as ctx:
                        ctx.params = {
                            'target': str(script_frontend),
                            'server.port': 8501,
                            'server.address': '127.0.0.1',
                            'server.headless': True,
                            'browser.gatherUsageStats': False
                        }
                        bootstrap.run(str(script_frontend), '', [], {})
                    
                except Exception as e:
                    print(f"Method 1 (bootstrap with context) failed: {e}")
                    
                    # Method 2: Try direct bootstrap without click context
                    try:
                        print("Attempting direct bootstrap...")
                        import streamlit.web.bootstrap as bootstrap
                        from streamlit import config
                        import os
                        
                        # Verify the script exists and is readable
                        if not script_frontend.exists():
                            raise FileNotFoundError(f"Frontend script not found: {script_frontend}")
                        
                        print(f"Frontend script path: {script_frontend}")
                        print(f"Frontend script exists: {script_frontend.exists()}")
                        
                        # Set configuration
                        config.set_option('server.port', 8501)
                        config.set_option('server.address', '127.0.0.1')
                        config.set_option('server.headless', True)
                        config.set_option('browser.gatherUsageStats', False)
                        config.set_option('server.enableCORS', False)
                        config.set_option('server.enableXsrfProtection', False)
                        config.set_option('server.runOnSave', False)
                        config.set_option('server.allowRunOnSave', False)
                        
                        # Also set browser config to prevent wrong URL display
                        config.set_option('browser.serverAddress', '127.0.0.1')
                        config.set_option('browser.serverPort', 8501)
                        
                        # Print the correct URL before starting
                        print("Streamlit server starting...")
                        print("You can now view your Streamlit app in your browser:")
                        print("  Local URL: http://127.0.0.1:8501")
                        print("  Network URL: http://127.0.0.1:8501")
                        print(f"Loading script: {script_frontend}")
                        
                        # Start bootstrap directly with proper arguments
                        # bootstrap.run(script_path, command_line_args, prog_name, prog_args)
                        bootstrap.run(
                            str(script_frontend), 
                            'run',  # command ('run' instead of empty string)
                            [],     # args (empty list)
                            {}      # flag_options (empty dict)
                        )
                        
                    except Exception as e:
                        print(f"Method 2 (direct bootstrap) failed: {e}")
                        import traceback
                        print("Traceback:")
                        traceback.print_exc()
                        
                        # Method 3: Try using streamlit main module
                        try:
                            print("Attempting streamlit main module...")
                            import streamlit.__main__ as st_main
                            
                            # Backup original argv
                            original_argv = sys.argv.copy()
                            
                            # Set argv for streamlit
                            sys.argv = ['streamlit', 'run', str(script_frontend), 
                                    '--server.port', '8501',
                                    '--server.address', '127.0.0.1',
                                    '--server.headless', 'true',
                                    '--browser.gatherUsageStats', 'false',
                                    '--server.enableCORS', 'false',
                                    '--server.enableXsrfProtection', 'false']
                            
                            # Call streamlit main
                            st_main.main()
                            
                            # Restore original argv
                            sys.argv = original_argv
                            
                        except Exception as e:
                            print(f"Method 3 (main module) failed: {e}")
                            
                            # Method 4: Last resort - try subprocess with current python
                            try:
                                print("Last resort: trying subprocess with current Python...")
                                comando = [sys.executable, "-c", 
                                        f"import streamlit.web.bootstrap; streamlit.web.bootstrap.run('{str(script_frontend)}', '', [], {{}})"]
                                
                                resultado = subprocess.run(comando)
                                
                            except Exception as e:
                                print(f"Method 4 (subprocess) failed: {e}")
                                raise Exception("All Streamlit execution methods failed")
                        
            except FileNotFoundError as e:
                print("Erro ao carregar a GUI!\nArquivo streamlit não foi encontrado")
                print(f"Detalhes do erro: {e}")
                logger.warning("Erro ao iniciar a GUI: Arquivo streamlit não foi encontrado")
            except KeyboardInterrupt:
                print("\nShutting down Streamlit server...")
                sys.exit(0)
            except Exception as e:
                print(f"Erro inesperado ao iniciar Streamlit: {e}")
                logger.error(f"Erro inesperado ao iniciar Streamlit: {e}")
        else:
            # Direct Python execution - check for virtual environment
            print("Starting Streamlit from Python environment...")
            print("Web interface will be available at: http://localhost:8501")
            
            caminho_venv = self.fachada.obter_caminho('venv')

            if sys.platform == 'win32':
                # Windows
                if caminho_venv and caminho_venv.exists():
                    # With virtual environment on Windows
                    venv_activate = str(caminho_venv)
                    comando = f'{venv_activate} && streamlit run "{script_frontend}"'
                    resultado = subprocess.run(comando, shell=True)
                else:
                    # Without virtual environment on Windows
                    comando = ["streamlit", "run", str(script_frontend)]
                    resultado = subprocess.run(comando)
            else:
                # Linux/Unix
                if caminho_venv and caminho_venv.exists():
                    # With virtual environment on Linux
                    venv_activate = f"source {str(caminho_venv)}"
                    comando = f'{venv_activate} && streamlit run "{script_frontend}"'
                    resultado = subprocess.run(["bash", "-c", comando])
                else:
                    # Without virtual environment on Linux
                    comando = ["streamlit", "run", str(script_frontend)]
                    resultado = subprocess.run(comando)


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
            entrega_gradual = True
            tipo_relatorio = "JSON"
            tempo_inicio = time.time()
            progresso_minimo = 0.1

            self.iniciar_spinner()

            if entrega_gradual:
                for resultado in self.fachada.executar_testes_com_entrega_gradual(argumentos, tipo_relatorio):
                    if resultado[-1] >= progresso_minimo:
                        progresso = round(resultado[-1], 1)
                        tempo_decorrido = time.time() - tempo_inicio
                        sys.stdout.write('\r' + ' ' * 20 + '\r')
                        print(f"{max(progresso, progresso_minimo) * 100:.1f}% dos testes finalizados em {tempo_decorrido:.1f}s")
                        progresso_minimo = max(progresso_minimo + 0.1, progresso)
            else:
                list(self.fachada.executar_testes_com_resultado_completo(argumentos, tipo_relatorio))
            
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
