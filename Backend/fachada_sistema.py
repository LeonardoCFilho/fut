from Backend.Classes.gerador_template_teste import GeradorTemplateTeste
from Backend.Classes.servico_execucao_teste import ServicoExecucaoTeste
from Backend.Classes.coordenador_teste import CoordenadorTestes
from Backend.Classes.gestor_caminho import GestorCaminho
from Backend.dialogos_sistema import DialogosSistema  
from pathlib import Path
import logging 
import sys

logger = logging.getLogger(__name__)


class FachadaSistema:
    """
    Fachada principal do sistema que coordena operações de teste e configuração.
    Fornece uma interface simplificada para terminal e interface gráfica.
    """
    
    def __init__(self):
        self._path_fut = None
        self._coordenador_testes = None


    @property
    def coordenador_testes(self) -> CoordenadorTestes:
        """Lazy initialization do coordenador de testes"""
        if self._coordenador_testes is None:
            self._coordenador_testes = CoordenadorTestes.get_instance(
                GestorCaminho(self.path_fut)
            )
        return self._coordenador_testes


    @property 
    def path_fut(self) -> Path:
        """Lazy initialization do caminho do projeto"""
        if self._path_fut is None:
            self._path_fut = self.acharCaminhoProjeto()
        return self._path_fut


    # === OPERAÇÕES DE ARQUIVOS ===

    def listar_arquivos_yaml(self, args = None) -> list[Path]:
        """
        Lista arquivos YAML para teste baseado nos argumentos fornecidos

        Args: 
            args: Argumentos para filtrar os testes a serem validados

        Returns:
            Lista com caminhos dos arquivos de teste (pode ser vazia)
            
        Raises:
            OSError: Erro ao acessar sistema de arquivos
        """
        try:
            return ServicoExecucaoTeste(self.path_fut).preparar_lista_testes(args)
        except Exception as e:
            logger.error(f"Erro ao listar arquivos YAML: {e}")
            raise OSError(f"Falha ao listar arquivos de teste: {e}") from e


    def gerar_arquivo_teste(self, dados_teste: dict = None, caminho_arquivo: Path|str = None) -> None:
        """
        Cria um arquivo .yaml seguindo o template para caso de teste

        Args:
            dados_teste: Dados a serem inseridos no template (opcional)
            caminho_arquivo: Caminho onde o arquivo será criado (opcional)

        Raises:
            PermissionError: Sem permissão para criar o arquivo
            OSError: Outros erros de I/O
        """
        GeradorTemplateTeste.gerar_arquivo_template(caminho_arquivo, dados_teste)

    # === OPERAÇÕES DE CONFIGURAÇÃO ===
    
    def obter_configuracao(self, nome_configuracao: str):
        """
        Obtém o valor de uma configuração específica

        Args:
            nome_configuracao: Nome da configuração buscada

        Returns:
            Valor da configuração ou None se não encontrada/erro

        Raises:
            ValueError: Se o nome da configuração for inválido
        """
        if not nome_configuracao or not nome_configuracao.strip():
            raise ValueError("Nome da configuração não pode ser vazio")
            
        try:
            return self.coordenador_testes.gestor_caminho.controlador_configuracao.obter_configuracao_segura(
                nome_configuracao
            )
        except Exception as e:
            logger.error(f"Erro ao obter configuração '{nome_configuracao}': {e}")
            return None
        
    
    def obter_caminho(self, nome_endereco: str) -> Path|None:
        """
        Obtém o valor de um caminho específico

        Args:
            nome_endereco: Nome da configuração buscada

        Returns:
            Valor do endereço solicitado ou None se o nome do caminho for inválido
        """
        try:
            return self.coordenador_testes.gestor_caminho.return_path(nome_endereco)
        except Exception as e:
            logger.warning(f'Erro ao buscar o caminho: {e}')
            return None


    def atualizar_configuracao(self, nome_configuracao: str, novo_valor) -> bool:
        """
        Atualiza o valor de uma configuração

        Args:
            nome_configuracao: Nome da configuração a ser alterada
            novo_valor: Novo valor para a configuração

        Returns:
            bool: True se alteração foi bem-sucedida, False caso contrário

        Raises:
            ValueError: Se argumentos forem inválidos ou valor incompatível
            FileNotFoundError: Se caminho especificado não existir
        """
        if not nome_configuracao or not nome_configuracao.strip():
            raise ValueError("Nome da configuração não pode ser vazio")
            
        return self.coordenador_testes.gestor_caminho.controlador_configuracao.alterar_valor_configuracao(
            nome_configuracao, str(novo_valor)
        )

    # === OPERAÇÕES DE TESTE ===
    
    def executar_testes_com_resultado_completo(self, args, tipo_relatorio: str = 'JSON') -> list[dict]:
        """
        Executa testes em múltiplas threads e retorna todos os resultados de uma vez

        Args:
            args: Argumentos determinando os testes a serem executados
            tipo_relatorio: Tipo do relatório ('JSON' ou 'HTML')

        Returns:
            Lista com todos os resultados dos testes

        Raises:
            ValueError: Lista de testes vazia ou argumentos inválidos
            FileNotFoundError: Schema do ExecutorTeste não encontrado
            PermissionError: Sem permissão para escrever relatório
        """
        self._validar_argumentos_teste(args, tipo_relatorio)
        
        try:
            logger.info("Iniciando execução de testes (resultado completo)")
            resultados = list(
                self.coordenador_testes.executar_testes_completo(
                    args, tipo_relatorio, entrega_gradual=False
                )
            )
            logger.info(f"Execução concluída: {len(resultados)} resultados")
            return resultados
        except Exception as e:
            logger.error(f"Erro durante execução dos testes: {e}")
            raise


    def executar_testes_com_entrega_gradual(self, args, tipo_relatorio: str = 'JSON'):
        """
        Executa testes em múltiplas threads com entrega gradual dos resultados

        Args:
            args: Argumentos determinando os testes a serem executados
            tipo_relatorio: Tipo do relatório ('JSON' ou 'HTML')

        Yields:
            Dict com informações do teste e porcentagem de progresso

        Raises:
            ValueError: Lista de testes vazia ou argumentos inválidos
            FileNotFoundError: Schema do ExecutorTeste não encontrado
            PermissionError: Sem permissão para escrever relatório
        """
        self._validar_argumentos_teste(args, tipo_relatorio)
        
        try:
            logger.info("Iniciando execução de testes (entrega gradual)")
            yield from self.coordenador_testes.executar_testes_completo(
                args, tipo_relatorio, entrega_gradual=True
            )
            logger.info("Execução com entrega gradual concluída")
        except Exception as e:
            logger.error(f"Erro durante execução dos testes: {e}")
            raise


    def _validar_argumentos_teste(self, args, tipo_relatorio: str) -> None:
        """Valida argumentos para execução de testes"""
        if tipo_relatorio not in ['JSON', 'HTML']:
            raise ValueError(f"Tipo de relatório inválido: {tipo_relatorio}. Use 'JSON' ou 'HTML'")
        
        # Validação adicional de args poderia ser implementada aqui

    # === UTILITÁRIOS DE INTERFACE ===
    
    def obter_dialogo(self, chave_dialogo: str) -> str:
        """
        Retorna diálogos estilizados para uso no terminal

        Args:
            chave_dialogo: Chave do diálogo desejado

        Returns:
            String do diálogo ou string vazia se não encontrado
        """
        if not chave_dialogo:
            return ""
        return DialogosSistema.obter_dialogo(chave_dialogo)

    # === MÉTODOS DE ENDEREÇAMENTO ===
    
    @classmethod
    def acharCaminhoProjeto(cls) -> Path:
        """
        Encontra o caminho do diretório do projeto usando múltiplas estratégias.

        Returns:
            Path: O caminho do diretório do projeto.

        Raises:
            SystemExit: Se o diretório do projeto não for encontrado.
        """
        max_iteracoes = 10
        num_iteracoes = 0
        path_fut = Path(__file__).resolve()
        
        while num_iteracoes < max_iteracoes:
            if "fut" in path_fut.name.lower():
                return path_fut
            path_fut = path_fut.parent
            num_iteracoes += 1

        sys.exit("Projeto FUT não encontrado. Garanta que está em um diretório do projeto.")


    @staticmethod
    def _is_fut_project(path: Path) -> bool:
        """
        Verifica se um diretório é um projeto FUT válido.
        
        Args:
            path: Caminho a ser verificado
            
        Returns:
            bool: True se for um projeto FUT
        """
        # Procura por arquivos/diretórios característicos do projeto FUT
        markers = [
            'Backend',
            'fut.py',  # se houver um arquivo principal
            'requirements.txt',
        ]
        
        return any((path / marker).exists() for marker in markers) or "fut" in path.name.lower()
