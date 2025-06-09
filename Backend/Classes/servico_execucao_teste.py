from Backend.Classes.gerenciador_validator import GerenciadorValidator
from Backend.Classes.executor_teste import ExecutorTeste
from Backend.Classes.gestor_caminho import GestorCaminho
from functools import partial
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

class ServicoExecucaoTeste:
    """Responsável por executar os testes"""
    
    # Construtor
    def __init__(self, gestor_caminho: GestorCaminho):
        self.gestor_caminho = gestor_caminho
    

    def garantir_atualizacao_validator(self) -> bool:
        """
        Garante que o validator esteja atualizado

        Returns:
            bool: True: Se o validator está atualizado é valido e está atualizado
                  False: Se o validator é invalido ou não foi possível atualizá-lo
        """
        gerenciador_validator = GerenciadorValidator(self.gestor_caminho.return_path('validator'))
        tempo_request_timeout = int(self.gestor_caminho.controlador_configuracao.obter_configuracao_segura('requests_timeout'))
        return gerenciador_validator.atualizar_validator_cli_seguro(tempo_request_timeout)


    def preparar_lista_testes(self, args=None) -> list:
        """
        Prepara a lista de arquivos de teste a serem executados
        
        Args:
            args: Argumentos para criar a lista de testes
            
        Returns:
            Lista com endereços dos arquivos de teste
        """
        logger.info("Lista de testes a serem examinadas criada")
        if not args or not isinstance(args, list):
            logger.debug("Argumentos inválidos para a execução dos testes, lista vazia.")
            args = []
        
        executor_teste = ExecutorTeste(
            self.gestor_caminho.return_path('schema_yaml'), 
            self.gestor_caminho.return_path('validator')
        )
        return executor_teste.gerar_lista_arquivos_teste(args)
    

    def executar_testes_paralelos(self, lista_arquivos: list, num_threads: int, timeout: float):
        """
        Executa os testes em paralelo usando threads
        
        Args:
            lista_arquivos (list): Lista com endereços dos arquivos de teste
            num_threads (int): Número máximo de threads
            timeout (float): Timeout para cada teste
            
        Yields:
            dict: Resultado de cada teste executado
        """
        logger.info("Iniciando a execução dos testes requisitados")
        
        executor_teste = ExecutorTeste(
            self.gestor_caminho.return_path('schema_yaml'), 
            self.gestor_caminho.return_path('validator')
        )
        
        validar_completado = partial(
            executor_teste.validar_arquivo_teste, 
            path_pasta_validator=self.gestor_caminho.return_path('pasta_validator'), 
            tempo_timeout=timeout
        )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            for resultado in executor.map(validar_completado, lista_arquivos):
                try:
                    yield resultado
                except Exception as e:
                    logger.error(f"Erro ao executar thread de teste: {e}")
                    raise e
