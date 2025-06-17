from Backend.Classes.leitor_schema import LeitorSchema
from pathlib import Path
import jsonschema
import logging

logger = logging.getLogger(__name__)

class Teste:
    def __init__(self, path_arquivo_teste: Path, conteudo: dict, estado_atual:str = "Pendente", justificativa_teste_invalido:str = ''):
        self.path_arquivo_teste = path_arquivo_teste
        self.conteudo = conteudo
        self.estado_atual = estado_atual
        self.justificativa_teste_invalido = justificativa_teste_invalido
        self.argumentos_validator = ""
        self.path_resultado = None
        self.tempo_execucao = -1 # Deixar claro que nao foi testado
    

    def validar_schema(self, path_schema: Path) -> bool:
        """Valida o conteúdo contra o schema JSON"""
        try:
            # Checar antes se é uma suite
            if isinstance(self.conteudo, dict) and 'suite_name' in self.conteudo:
                self.estado_atual = "Suite"
                return True
            
            # Não é => tratar como arquivo de teste normal
            schema = LeitorSchema(path_schema).return_dados_schema() 
            jsonschema.validate(instance=self.conteudo, schema=schema)
            self.estado_atual = "Válido"
            return True
            
        except jsonschema.ValidationError as e:
            self.estado_atual = "Inválido"
            self._gerar_mensagem_erro_amigavel(e)
            return False
            
        except Exception as e:
            self.estado_atual = "Erro"
            self.justificativa_teste_invalido = f"Erro ao carregar schema: {str(e)}"
            return False
    

    def _gerar_mensagem_erro_amigavel(self, e) -> str:
        """Gera mensagem de erro mais amigável"""
        if " is a required property" in e.message:
            campo_faltando = e.message.split(' is a required property')[0]
            self.justificativa_teste_invalido = f"O campo {campo_faltando} é obrigatório"
        elif " is not of type " in e.message:
            partes = e.message.split(" is not of type ")
            variavel = partes[0]
            tipo_esperado = partes[1]
            self.justificativa_teste_invalido = f"O valor da variável '{variavel}' deve ser do tipo {tipo_esperado}"
        elif " is not one of " in e.message:
            partes = e.message.split(" is not one of ")
            variavel = partes[0]
            valores_validos = partes[1]
            self.justificativa_teste_invalido = f"O valor da variável {variavel} deve ser um entre {valores_validos}"
        else:
            self.justificativa_teste_invalido = f"Erro de validação: {e.message}"
    

    def esta_pronto(self) -> bool:
        """Verifica se o teste está pronto para validação"""
        return self.estado_atual in ["Valido"]