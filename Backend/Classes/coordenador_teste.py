from Backend.Classes.servico_execucao_teste import ServicoExecucaoTeste
from Backend.Classes.configurador_execucao import ConfiguradorExecucao
from Backend.Classes.servico_relatorio import ServicoRelatorio
from Backend.Classes.gestor_caminho import GestorCaminho
import threading
import logging
import time

logger = logging.getLogger(__name__)

class CoordenadorTestes:
    """
    Coordenador principal que orquestra os diferentes serviços para execução de testes
    """
    _instance = None
    _lock = threading.Lock()
    # Construtor
    def __init__(self, gestor_caminho: GestorCaminho):
        if not CoordenadorTestes._instance:
            CoordenadorTestes._instance = self
            self.gestor_caminho = gestor_caminho
            
            # Injeção de dependências - serviços especializados
            self.executor_service = ServicoExecucaoTeste(gestor_caminho)
            self.configurador = ConfiguradorExecucao(gestor_caminho.controlador_configuracao)
            self.servico_relatorio = ServicoRelatorio()


    @staticmethod
    def get_instance(gestor_caminho: GestorCaminho = None):
        with CoordenadorTestes._lock:
            if CoordenadorTestes._instance is None:
                if gestor_caminho is None:
                    raise ValueError("Caminho da pasta do projeto deve ser providenciada na primeira execução")
                CoordenadorTestes._instance = CoordenadorTestes(gestor_caminho)
        return CoordenadorTestes._instance


    def executar_testes_completo(self, args: list, versao_relatorio: str, entrega_gradual: bool = True):
        """
        Coordena todo o fluxo de execução dos testes
        
        Args:
            args (list): Argumentos para criar lista de testes
            versao_relatorio (str): Tipo do relatório (JSON ou HTML)
            entrega_gradual (bool): Se deve entregar resultados gradualmente
            
        Yields:
            list: [resultado, porcentagem] se entrega_gradual=True
        """
        # 1. Atualizar validator/Garantir instalação
        self.executor_service.garantir_atualizacao_validator()
        
        # 2. Preparar lista de testes
        lista_arquivos = self._obter_lista_testes(args)
        
        # 3. Configurar execução
        config = {}
        config['num_threads'] = self.configurador.calcular_threads_otimas()
        config['timeout'] = self.configurador.obter_timeout()
        
        # 4. Executar testes
        resultados_validacao = []
        start_time = time.time()
        for resultado_info in self._executar_testes(lista_arquivos, config, entrega_gradual):
            resultados_validacao.append(resultado_info[0])  # armazenar o resultado
            yield resultado_info  # Yield [resultado, porcentagem]
        tempo_execucao = time.time() - start_time

        # 5. Gerar relatório
        logger.info("Testes listados completos")
        print("Testes finalizados!")
        
        try:
            self.servico_relatorio.criar_relatorio_completo(
                resultados_validacao, 
                versao_relatorio, 
                tempo_execucao
            )
        except PermissionError as e:
            raise e


    def _obter_lista_testes(self, args: list) -> list:
        """
        Obtém e valida a lista de testes a partir dos argumentos fornecidos.
    
        Args:
            args (list): Argumentos utilizados para construir a lista de testes.
    
        Returns:
            list: Lista de testes válidos para execução.
        """
        lista_arquivos = self.executor_service.preparar_lista_testes(args)
        
        if len(lista_arquivos) == 0:
            logger.info("Nenhum caso de teste válido encontrado")
            raise ValueError("Nenhum arquivo de teste encontrado. Verifique os argumentos e endereços.")
        
        return lista_arquivos
    

    def _executar_testes(self, lista_arquivos: list, config: dict, entrega_gradual: bool):
        """
        Executa os testes e yielda resultados conforme progride
        
        """
        try:
            resultados_validacao = []
            
            for resultado in self.executor_service.executar_testes_paralelos(
                lista_arquivos, config['num_threads'], config['timeout']
            ):
                resultados_validacao.append(resultado)
                
                if entrega_gradual:
                    porcentagem = round((len(resultados_validacao) / len(lista_arquivos)), 4)
                    yield [resultado, porcentagem]
            
        except Exception as e:
            logger.error(f"Erro ao rodar os testes em threads: {e}")
            #raise e