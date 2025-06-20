from Backend.Classes.servico_execucao_teste import ServicoExecucaoTeste
from Backend.Classes.configurador_execucao import ConfiguradorExecucao
from Backend.Classes.servico_relatorio import ServicoRelatorio
from Backend.Classes.gerenciador_java import GerenciadorJava
from Backend.Classes.gestor_caminho import GestorCaminho
import threading
import logging
import time

logger = logging.getLogger(__name__)

class CoordenadorTestes:
    """Coordenador principal que orquestra a execução de testes"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, gestor_caminho: GestorCaminho):
        if CoordenadorTestes._instance is not None:
            raise RuntimeError("Use get_instance() para obter a instância")
            
        self.gestor_caminho = gestor_caminho
        self.executor_service = ServicoExecucaoTeste(gestor_caminho)
        self.configurador = ConfiguradorExecucao(gestor_caminho.controlador_configuracao)
        self.servico_relatorio = ServicoRelatorio()
        self.gerenciador_java = GerenciadorJava(self.gestor_caminho.return_path('arquivos'))
        
        CoordenadorTestes._instance = self


    @classmethod
    def get_instance(cls, gestor_caminho: GestorCaminho = None):
        """Obtém a instância singleton do coordenador"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if gestor_caminho is None:
                        raise ValueError("gestor_caminho é obrigatório na primeira inicialização")
                    cls._instance = cls(gestor_caminho)
        return cls._instance


    def executar_testes_completo(self, args: list):
        """
        Executa o fluxo completo de testes
        
        Args:
            args: Argumentos para lista de testes
            
        Yields:
            list: [resultado, porcentagem] se entrega_gradual=True
        Returns:
            dict: Resultado da execução com métricas se entrega_gradual=False
        """
        start_time = time.time()
        
        try:
            # 1. Preparação
            self._preparar_ambiente()
            lista_testes = self._obter_lista_testes(args)
            config_execucao = self._obter_configuracao_execucao()
            
            # 2. Execução
            # Modo gradual - yielda cada resultado
            resultados = []
            for resultado in self._executar_testes_gradual(lista_testes, config_execucao):
                resultados.append(resultado[0])
                yield resultado  # [resultado, porcentagem]
                
            # 3. Relatório após todos os yields
            tempo_total = time.time() - start_time
            self._gerar_relatorio(resultados, tempo_total)

        except Exception as e:
            logger.error(f"Erro durante execução de testes: {e}")
            raise e


    def _preparar_ambiente(self):
        """Prepara o ambiente para execução dos testes"""
        logger.info("Preparando ambiente...")
        self.gerenciador_java.java_instalado()
        self.gerenciador_java.extrair_java()
        self.executor_service.garantir_atualizacao_validator()


    def _obter_lista_testes(self, args: list) -> list:
        """Obtém e valida lista de testes"""
        logger.info("Obtendo lista de testes...")
        lista_arquivos_testes = self.executor_service.preparar_lista__arquivo_teste(args)
        lista_testes = self.executor_service.preparar_lista_Teste(lista_arquivos_testes)
        
        if not lista_testes:
            raise ValueError("Nenhum arquivo de teste encontrado. Verifique os argumentos.")
            
        logger.info(f"Encontrados {len(lista_testes)} testes")
        return lista_testes


    def _obter_configuracao_execucao(self) -> dict:
        """Obtém configurações otimizadas para execução"""
        return {
            'num_threads': self.configurador.calcular_threads_otimas(),
            'timeout': self.configurador.obter_timeout()
        }


    def _executar_testes_gradual(self, lista_testes: list, config: dict):
        """
        Executa testes e yielda resultados gradualmente
        
        Args:
            lista_testes: Lista de arquivos de teste
            config: Configuração de execução
            
        Yields:
            list: [resultado, porcentagem] para cada teste executado
        """
        logger.info(f"Iniciando execução gradual de {len(lista_testes)} testes...")
        resultados_processados = 0
        
        for resultado in self.executor_service.executar_testes_paralelos(
            lista_testes, config['num_threads'], config['timeout']
        ):
            resultados_processados += 1
            porcentagem = round(resultados_processados / len(lista_testes), 4)
            yield [resultado, porcentagem]


    def _gerar_relatorio(self, resultados: list, tempo_execucao: float):
        """Gera o relatório final"""
        logger.info("Testes listados completos")
        
        # Determinar o tipo de relatório a ser gerado
        versao_relatorio = self.configurador.obter_tipo_relatorio()
        
        try:
            self.servico_relatorio.criar_relatorio_completo(
                resultados, versao_relatorio, tempo_execucao, self.gestor_caminho.return_path('csv'), self.gestor_caminho.return_path('template_html')
            )
        except PermissionError as e:
            logger.error(f"Erro de permissão ao gerar relatório: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            raise e