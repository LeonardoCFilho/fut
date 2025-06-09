import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LeitorSchema:
    """Classe unificada para ler e validar schemas de teste e configuração"""
    
    # Construtor
    def __init__(self, arquivo_schema: Path):
        """Inicializa com o caminho do arquivo de schema.
        
        Args:
            arquivo_schema: Caminho para o arquivo JSON do schema
        """
        self.arquivo_schema = arquivo_schema
        self.dados_schema = self._carregar_schema()
        self.tipo_schema = self._detectar_tipo_schema()
    

    def _carregar_schema(self) -> dict:
        """Carrega e analisa o arquivo JSON do schema.
        
        Returns:
            Dict contendo os dados do schema carregado
            
        Raises:
            FileNotFoundError: Se o arquivo de schema não for encontrado
            ValueError: Se o JSON for inválido
        """
        try:
            with open(self.arquivo_schema, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {self.arquivo_schema}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido no arquivo de schema: {e}")
    

    def _detectar_tipo_schema(self) -> str:
        """Detecta se é um schema de teste ou configuração.
        
        Returns:
            String indicando o tipo de schema: 'configuracao', 'teste' ou 'desconhecido'
        """
        if "configuracoes" in self.dados_schema:
            return "configuracao"
        elif "properties" in self.dados_schema and "test_id" in self.dados_schema.get("properties", {}):
            return "teste"
        else:
            return "desconhecido"
    

    def return_tipo_schema(self) -> str:
        """Retorna o tipo de schema detectado.
        
        Returns:
            String com o tipo de schema
        """
        return self.tipo_schema
    

    def return_dados_schema(self) -> dict:
        """Retorna os dados completos do schema.
        
        Returns:
            Dict contendo todos os dados do schema
        """
        return self.dados_schema
    
    