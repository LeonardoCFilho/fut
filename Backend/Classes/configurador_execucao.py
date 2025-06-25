from Backend.Classes.controlador_configuracao import ControladorConfiguracao
import logging
import os

logger = logging.getLogger(__name__)

class ConfiguradorExecucao:
    """
    Responsável por configurar parâmetros de execução dos testes
    """
    
    # Construtor
    def __init__(self, controlador_configuracao: ControladorConfiguracao):
        self.controlador_configuracao = controlador_configuracao
    

    def calcular_threads_otimas(self) -> int:
        """
        Calcula o número ótimo de threads para execução
        
        Returns:
            int: O valor de threads a ser usado"""
        try:
            max_threads = int(self.controlador_configuracao.obter_configuracao_segura('max_threads'))
            cpu_cores = os.cpu_count() or 1
            return min(max_threads, max(1, (cpu_cores - 2)))
        except Exception as e:
            logger.warning(f"Erro ao calcular threads usando valor padrão: {e}")
            return 1  # por segurança
    

    def obter_timeout(self) -> int:
        """
        Obtém o timeout configurado para execução dos testes
        
        Returns:
            int: tempo de timeout do validator
        """
        return int(self.controlador_configuracao.obter_configuracao_segura('timeout'))

    
    def obter_tipo_relatorio(self) -> str:
        """
        Retorna o tipo de relatorio a ser criado

        Returns:
            str: HTML ou JSON
        """
        tipo_relatorio = "HTML"
        if not self.controlador_configuracao.obter_categoria_configuracao('relatorio_eh_html'):
            tipo_relatorio = "JSON"
        
        return tipo_relatorio