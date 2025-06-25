from Backend.Classes.gerenciador_arquivo_teste import GerenciadorArquivoTeste
from Backend.Classes.gerenciador_validator import GerenciadorValidator
from Backend.Classes.gerenciador_java import GerenciadorJava
from Backend.Classes.preparador_teste import PreparadorTeste
from Backend.Classes.gestor_caminho import GestorCaminho
from Backend.Classes.teste import Teste
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
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


    def preparar_lista__arquivo_teste(self, args=None) -> list[Path]:
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
        
        return GerenciadorArquivoTeste().gerar_lista_arquivos_teste(args)
    

    def _executar_teste(self, gerenciador_validator: GerenciadorValidator, teste: Teste, timeout:float, contador:int, path_java: Path):
        try:
            output_validacao = gerenciador_validator.validar_arquivo_fhir(
                Path(teste.conteudo['caminho_instancia']), 
                Path(self.gestor_caminho.return_path('pasta_validator')), 
                contador,
                timeout, 
                path_java,
                teste.argumentos_validator,
            )
            teste.path_resultado = output_validacao[0]
            teste.tempo_execucao = output_validacao[1]
            teste.estado_atual = "Finalizado"
            return teste
        except Exception as e:
            logger.info(f"Erro ao usar o validator: {e}")
            if teste.justificativa_teste_invalido:
                teste.justificativa_teste_invalido += "\n"
            teste.justificativa_teste_invalido += str(e)
            return teste


    def preparar_lista_Teste(self, lista_arquivos: list[Path]) -> list[Teste]:
        """
        Retorna uma lista bruta de criada pela leitura dos arquivos de teste (YAML)

        Args:
            lista_arquivos (list[Path]): A lista com os caminhos dos arquivos YAML

        Returns:
            list[dict]: Uma lista dos testes encontrados nos arquivos de entrada
        """
        gerenciador_arquivo_teste = GerenciadorArquivoTeste() # instancia que será usada para lidar com arquivos
        preparador_teste = PreparadorTeste() # instancia que será usada para preparar todos os testes
        try:
            # ler os arquivos
            list_conteudo_cru = []
            for path in lista_arquivos:
                temp_dict = {}
                temp_dict['conteudo'], temp_dict['razao_invalidez'] = gerenciador_arquivo_teste.carregar_yaml(path)
                temp_dict['path_arquivo_teste'] = path
                list_conteudo_cru.append(temp_dict)
            # Criar os Testes
            list_testes = []
            for teste_parcial in list_conteudo_cru:
                list_testes.extend(preparador_teste.processar_testes(teste_parcial['conteudo'],teste_parcial['path_arquivo_teste'] ,teste_parcial['razao_invalidez']))
        except FileNotFoundError as e:
            logger.warning(f"Arquivo de teste não existe: {e}")
            raise e
        
        return list_testes
        
        
    def executar_testes_paralelos(self, list_testes: list[Teste], num_threads: int, timeout: float):
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
        
        gerenciador_validator = GerenciadorValidator(self.gestor_caminho.return_path('validator')) # Instancia que será usada para os testes
        gerenciador_java = GerenciadorJava(self.gestor_caminho.return_path('arquivos')) # Instancia que será usada para encontrar o java baixado
        
        # Executar em paralelo
        total_testes = len(list_testes)
        logger.info(f"Total de testes para executar: {total_testes}")
    
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submeter todos os testes para execução
            future_to_teste = {
                executor.submit(self._executar_teste, gerenciador_validator,  teste, timeout, list_testes.index(teste), gerenciador_java.obter_java_executavel()): teste 
                for teste in list_testes
            }

            # Processar resultados conforme completam
            for future in as_completed(future_to_teste):
                teste_original = future_to_teste[future]

                try:
                    # Obter resultado do teste
                    teste_resultado = future.result()

                    # Criar dicionário com resultado para yield
                    yield {
                        'caminho_yaml': teste_resultado.path_arquivo_teste,
                        'yaml_valido': len(teste_resultado.justificativa_teste_invalido) == 0,
                        'caminho_output': teste_resultado.path_resultado,
                        'tempo_execucao': teste_resultado.tempo_execucao,
                        'justificativa_arquivo_invalido': teste_resultado.justificativa_teste_invalido,
                        'conteudo_dict': teste_resultado.conteudo,
                    }

                except Exception as e:
                    # Tratar erro na execução do teste
                    logger.warning(f"Erro ao executar teste {teste_original.conteudo.get('test_id', 'N/A')}: {e}")