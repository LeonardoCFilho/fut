from Backend.Classes.gerenciador_validator import GerenciadorValidator
from Backend.Classes.leitor_schema import LeitorSchema
from pathlib import Path
import yaml
import jsonschema
import logging

logger = logging.getLogger(__name__)


class ExecutorTeste:
    # Construtor
    def __init__(self, path_schema: Path, path_validator: Path):
        """
        Inicializa o executor de testes.
        
        Args:
            path_schema (Path): Caminho para o arquivo de schema JSON
            path_validator (Path): Caminho para o validador
        """
        self.path_validator = path_validator
        self.path_schema = path_schema
        if not self.path_schema.exists():
            raise FileNotFoundError("Arquivo schema.json não encontrado")


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


    def _gerar_argumentos_validator(self, dict_contexto: dict, secao_interesse: str, prefixo: str) -> str:
        """
        Formata os argumentos do contexto para comandos usados pelo validator_cli.
        
        Args:
            dict_contexto (dict): Dicionário com o contexto
            secao_interesse (str): Seção de interesse no contexto
            prefixo (str): Prefixo para os argumentos
            
        Returns:
            str: String com argumentos formatados
        """
        argumentos_formatados = ''
        if dict_contexto.get(secao_interesse):
            if dict_contexto[secao_interesse] not in [None, "", [""]]:
                argumentos_formatados = f" -{prefixo} " + f" -{prefixo} ".join(dict_contexto[secao_interesse])
        return argumentos_formatados


    def _encontrar_arquivo_instancia(self, dados: dict, arquivo_teste: Path) -> tuple[Path, bool, str]:
        """
        Encontra o arquivo de instância a ser testado.
        
        Args:
            dados (dict): Dados do teste
            arquivo_teste (Path): Caminho do arquivo de teste
            
        Returns:
            tuple: (caminho_instancia, arquivo_encontrado, justificativa_erro)
        """
        # Preparar arquivo
        caminho_instancia = Path(dados['caminho_instancia'])
        if not caminho_instancia.is_absolute():
            caminho_instancia = arquivo_teste.parent / caminho_instancia

        # Tentar encontrar o arquivo
        if caminho_instancia.exists():
            return caminho_instancia, True, None
        
        # Tentar versão com mesmo nome mas extensão .json
        caminho_json = arquivo_teste.with_suffix('.json')
        if caminho_json.exists():
            return caminho_json, True, None
        
        # Tentar encontrar pelo ID do teste
        caminho_por_id = Path(arquivo_teste.parent / f"{dados['test_id']}.json")
        if caminho_por_id.exists():
            return caminho_por_id, True, None
        
        return None, False, "Não foi possível encontrar o arquivo a ser testado"


    def validar_arquivo_teste(self, arquivo_teste: Path, path_pasta_validator: Path, tempo_timeout: int) -> dict:
        """
        Valida um arquivo YAML usando o schema JSON e, se válido, chama a validação FHIR.

        Args:
            arquivo_teste (Path): Caminho do arquivo de teste .yaml
            path_pasta_validator (Path): Caminho da pasta do validador
            tempo_timeout (int): Tempo limite para validação
        
        Returns:
            dict: Dados do resultado da validação
        """
        # Inicializar variáveis
        yaml_valido = True
        output_validacao = [None, None]
        justificativa_arquivo_invalido = None
        dados = None

        ## Carregando arquivos
        try:
            # Carregar schema para validar o arquivo de teste
            schema = LeitorSchema(self.path_schema).return_dados_schema()
            
            # Carregar arquivo de teste
            if arquivo_teste.suffix in [".yaml", ".yml"]:
                with open(arquivo_teste, "r", encoding="utf-8") as arquivo:
                    dados = yaml.safe_load(arquivo)
                    
        except yaml.YAMLError:
            logger.warning(f"O arquivo {arquivo_teste} é um arquivo YAML inválido")
            justificativa_arquivo_invalido = "O arquivo de teste YAML não é válido, verifique as aspas e indentação"
            yaml_valido = False
        except Exception as e:
            logger.error(f"Erro no executor de teste: {e}")
            yaml_valido = False
            justificativa_arquivo_invalido = f"Erro ao carregar arquivo: {str(e)}"

        ## Testando arquivo de entrada
        if yaml_valido and dados:
            # Limpar a entrada
            dados = self._limpar_conteudo_yaml(dados)

            try:
                # Validar contra schema
                jsonschema.validate(instance=dados, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                logger.warning(f"Arquivo de teste inválido: {e}")
                yaml_valido = False
                
                # Gerar mensagem de erro mais amigável
                if " is a required property" in e.message:
                    campo_faltando = e.message.split(' is a required property')[0]
                    justificativa_arquivo_invalido = f"O campo {campo_faltando} é obrigatório"
                elif " is not of type " in e.message:
                    partes = e.message.split(" is not of type ")
                    variavel = partes[0]
                    tipo_esperado = partes[1]
                    justificativa_arquivo_invalido = f"O valor da variável '{variavel}' deve ser do tipo {tipo_esperado}"
                elif " is not one of " in e.message:
                    partes = e.message.split(" is not one of ")
                    variavel = partes[0]
                    valores_validos = partes[1]
                    justificativa_arquivo_invalido = f"O valor da variável {variavel} deve ser um entre {valores_validos}"
                else:
                    justificativa_arquivo_invalido = f"Erro de validação: {e.message}"

            # Encontrar arquivo de instância
            if yaml_valido:
                caminho_instancia, arquivo_encontrado, erro_arquivo = self._encontrar_arquivo_instancia(dados, arquivo_teste)
                if not arquivo_encontrado:
                    yaml_valido = False
                    justificativa_arquivo_invalido = erro_arquivo
                else:
                    dados['caminho_instancia'] = caminho_instancia

        # Executar validação FHIR se tudo estiver válido
        if yaml_valido and dados:
            try:
                contexto = dados.get('context', {})
                argumentos_fhir = ''
                argumentos_fhir += self._gerar_argumentos_validator(contexto, 'igs', 'ig')
                argumentos_fhir += self._gerar_argumentos_validator(contexto, 'profiles', 'profile')
                argumentos_fhir += self._gerar_argumentos_validator(contexto, 'resources', 'ig')
                
                gerenciador_validator = GerenciadorValidator(self.path_validator)
                
                output_validacao = gerenciador_validator.validar_arquivo_fhir(
                    dados['caminho_instancia'], 
                    path_pasta_validator, 
                    tempo_timeout, 
                    argumentos_extras=argumentos_fhir
                )
            except Exception as e:
                logger.info(f"Erro ao usar o validator: {e}")

        return {
            'caminho_yaml': arquivo_teste,
            'yaml_valido': yaml_valido,
            'caminho_output': output_validacao[0],
            'tempo_execucao': output_validacao[1],
            'justificativa_arquivo_invalido': justificativa_arquivo_invalido,
        }


    def _padronizar_argumentos_entrada(self, argumentos) -> list:
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


    def gerar_lista_arquivos_teste(self, argumentos_entrada) -> list:
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