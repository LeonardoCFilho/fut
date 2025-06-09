from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GeradorTemplateTeste:
    """Responsável pela geração de templates de arquivos de teste YAML"""
    # Construtor
    def __init__(self):
        pass

    @staticmethod
    def gerar_arquivo_template(caminho_arquivo: str | Path = None, dados_teste: dict = None) -> None:
        """
        Cria um arquivo .yaml que segue o template para caso de teste

        Args:
            caminho_arquivo: Caminho onde o arquivo será criado (padrão: "template.yaml")
            dados_teste: Dados a serem inseridos no template (opcional)

        Raises:
            PermissionError: Quando não há permissão para criar/escrever o arquivo
            OSError: Outros erros de I/O
        """
        if caminho_arquivo is None:
            caminho_arquivo = "template.yaml"
        
        caminho_arquivo = Path(caminho_arquivo)
        
        if dados_teste is None:
            dados_teste = GeradorTemplateTeste._obter_dados_padrao()
            logger.info("Template vazio de arquivo de teste será criado")
        
        template_yaml = GeradorTemplateTeste._gerar_conteudo_yaml(dados_teste)
        
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as file:
                file.write(template_yaml)
            logger.info(f"Arquivo de teste criado em {caminho_arquivo}")
        except PermissionError:
            logger.error(f"Sem permissão para criar arquivo em {caminho_arquivo}")
            raise
        except OSError as e:
            logger.error(f"Erro ao criar arquivo {caminho_arquivo}: {e}")
            raise


    @staticmethod
    def _obter_dados_padrao() -> dict:
        """Retorna estrutura padrão para o template"""
        return {
            "test_id": '',
            "description": '',
            "igs": '',
            "profiles": '',
            "resources": '',
            "caminho_instancia": '',
            "status": '',
            "error": '',
            "warning": '',
            "fatal": '',
            "information": '',
            "invariantes": '',
        }
    

    @staticmethod
    def _gerar_conteudo_yaml(dados: dict) -> str:
        """Gera o conteúdo YAML do template"""
        return f"""test_id: {dados.get('test_id', '')} # (Obrigatório) Identificador único para cada teste (string).
description: {dados.get('description', '')} # (Recomendado) Descricao (string).
context: # Definição do contexto de validação.
    igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
        - {dados.get('igs', '')} # IDs ou url dos IGs (Apenas 1 por linha).
    profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
        - {dados.get('profiles', '')} # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
    resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
        - {dados.get('resources', '')} # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
caminho_instancia: {dados.get('caminho_instancia', '')} #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
    status: {dados.get('status', '')}  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
    error: [{dados.get('error', '')}]  #  (Obrigatório) Lista de erros esperados (lista de string).
    warning: [{dados.get('warning', '')}]  #  (Obrigatório) Lista de avisos esperados (lista de string).
    fatal: [{dados.get('fatal', '')}] #  #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
    information: [{dados.get('information', '')}]  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
    invariantes: {dados.get('invariantes', '')} # (Opcional)"""