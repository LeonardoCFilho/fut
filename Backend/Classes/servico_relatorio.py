from Backend.Classes.gerador_relatorio import GeradorRelatorios
import logging

logger = logging.getLogger(__name__)

class ServicoRelatorio:
    """
    Responsável por coordenar a criação de relatórios
    """
    # Construtor
    def __init__(self):
        pass
    

    def criar_relatorio_completo(self, resultados_validacao: list, versao_relatorio: str, tempo_execucao: float):
        """
        Cria relatório completo com base nos resultados da validação
        
        Args:
            resultados_validacao (list): Lista dos resultados dos testes
            versao_relatorio (str): Tipo do relatório (JSON ou HTML)
            tempo_execucao (float): Tempo total de execução
        """
        logger.info(f"Iniciando a criação do relatório, relatório selecionado é do tipo {versao_relatorio}")
        
        try:
            gerador_relatorio = GeradorRelatorios(resultados_validacao)
            
            # Sempre gerar o JSON
            gerador_relatorio.gerarRelatorioJson(tempo_execucao_total=tempo_execucao)
            
            # Gerar o relatório legível (HTML)
            #if versao_relatorio.lower() == "html":
            #    gerador_relatorio.gerarRelatorioHtml()
                
        except Exception as e:
            logger.error(f"Erro ao criar o relatório: {e}")
            raise e