from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

class GerenciadorArquivoTeste:
    def __init__(self):
        pass


    def _padronizar_argumentos_entrada(self, argumentos) -> list[str]:
        """
        Garante que os argumentos seguem um padrão pré-definido.
        
        Args: 
            argumentos: Os argumentos de entrada
        
        Returns:
            list: Lista de formato padronizado com os valores armazenados em argumentos
        """
        if isinstance(argumentos, str):
            argumentos = str(argumentos).split()
        elif isinstance(argumentos, (tuple, set)):
            argumentos = list(argumentos)
        elif not isinstance(argumentos, list):
            argumentos = [argumentos]
        
        # Limpar as strings
        argumentos = [str(arquivo).replace('"', '').replace("'", "") for arquivo in argumentos]
        
        return argumentos
    

    def gerar_lista_arquivos_teste(self, argumentos_entrada) -> list[Path]:
        """
        Recebe os comandos escritos pelo usuário, verificando os seguintes casos:
        1. Todos os arquivos .yaml da pasta atual (entrada vazia)
        2. O arquivo específico
        3. Os arquivos que tenham o mesmo prefixo (uso de '*')

        Args: 
            argumentos_entrada: Entrada para determinar a lista de arquivos de teste
        
        Returns:
            list: Lista de paths para cada yaml encontrado
        """
        arquivos_yaml = []
        
        # Garantir que argumentos_entrada é uma lista
        argumentos_entrada = self._padronizar_argumentos_entrada(argumentos_entrada)
        
        # Ler todos da pasta atual se não há argumentos
        if len(argumentos_entrada) == 0:
            arquivos_yaml = list(Path.cwd().glob('*.yaml')) + list(Path.cwd().glob('*.yml'))
        else:
            # Processar arquivos especificados
            for caminho_arquivo in argumentos_entrada:
                arquivo_atual = Path(caminho_arquivo)

                # Converter caminho relativo para absoluto
                if not arquivo_atual.is_absolute():
                    arquivo_atual = Path.cwd() / arquivo_atual

                # Processar wildcards
                if '*' in arquivo_atual.name:
                    prefixo_pesquisa = str(arquivo_atual.name).split('*')[0]
                    arquivos_encontrados = list(arquivo_atual.parent.glob(f"{prefixo_pesquisa}*.yaml"))
                    arquivos_encontrados.extend(list(arquivo_atual.parent.glob(f"{prefixo_pesquisa}*.yml")))
                    arquivos_yaml.extend(arquivos_encontrados)
                else:
                    # Verificar se o arquivo tem extensão válida e existe
                    if (arquivo_atual.suffix in [".yaml", ".yml"]) and arquivo_atual.exists():
                        arquivos_yaml.append(arquivo_atual)

        # Remover duplicatas e arquivos inexistentes
        arquivos_yaml = list(set(arquivos_yaml))
        arquivos_yaml = [arquivo for arquivo in arquivos_yaml if arquivo.exists()]

        return arquivos_yaml


    def _limpar_conteudo_yaml(self, dados: dict) -> dict:
        """
        Padroniza as informações recebidas do arquivo de teste.

        Args:
            dados (dict): Entrada a ser tratada
        
        Returns:
            dict: Entrada tratada
        """
        if isinstance(dados, dict):
            return {chave: self._limpar_conteudo_yaml(valor) for chave, valor in dados.items()}
        elif isinstance(dados, list):
            return [self._limpar_conteudo_yaml(item) if item is not None else "" for item in dados]
        return dados


    def carregar_yaml(self, arquivo: Path) -> tuple[dict, str]:
        """Load YAML file and validate it's valid YAML syntax"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as arquivo:
                dados = yaml.safe_load(arquivo)
            return self._limpar_conteudo_yaml(dados), None
        except yaml.YAMLError as e:
            return None, f"YAML inválido: {e}"
        except Exception as e:
            return None, f"Erro ao carregar arquivo: {e}"