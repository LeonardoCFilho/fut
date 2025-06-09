from Backend.Classes.leitor_schema import LeitorSchema
from pathlib import Path
import configparser
import logging
import json

logger = logging.getLogger(__name__)

class ControladorConfiguracao:
    """
    Gerencia a leitura e alteração de configurações do sistema
    a partir do arquivo settings.ini usando um schema JSON.
    """
    # Construtor
    def __init__(self, path_configuracoes: Path, path_schema: Path):
        """
        Inicializa o gerenciador de configurações.

        Args:
            path_configuracoes (Path): Caminho para o arquivo de configurações.
            path_schema (Path): Caminho para o arquivo de schema JSON.
        """
        self.path_configuracoes = path_configuracoes
        self.path_schema = path_schema
        self.schema = LeitorSchema(self.path_schema).return_dados_schema()


    def _obter_tipo_configuracao(self, nome_configuracao: str) -> type:
        """
        Obtém o tipo Python correspondente ao tipo do schema.
        
        Args:
            nome_configuracao (str): Nome da configuração.
            
        Returns:
            type: Tipo Python correspondente.
        """
        config_info = self.schema['configuracoes'].get(nome_configuracao.lower())
        if not config_info:
            return str  # Tipo padrão para configurações não definidas no schema
            
        tipo_schema = config_info.get('type', 'string')
        
        # Mapeamento de tipos do schema para tipos Python
        mapeamento_tipos = {
            'integer': int,
            'string': str,
            'boolean': bool,  # Corrigindo o typo "oolean" do seu schema
            'path': str
        }
        
        return mapeamento_tipos.get(tipo_schema, str)


    def _obter_limites_configuracao(self, nome_configuracao: str) -> dict:
        """
        Obtém os limites definidos no schema para uma configuração.
        
        Args:
            nome_configuracao (str): Nome da configuração.
            
        Returns:
            Dict: Dicionário com os limites (minimum, maximum, etc.).
        """
        config_info = self.schema['configuracoes'].get(nome_configuracao.lower(), {})
        return {
            'minimum': config_info.get('minimum'),
            'maximum': config_info.get('maximum'),
            'validation': config_info.get('validation', {})
        }

    def obter_valor_padrao(self, nome_configuracao: str):
        """
        Obtém o valor padrão de uma configuração definido no schema.
        
        Args:
            nome_configuracao (str): Nome da configuração.
            
        Returns:
            Valor padrão da configuração ou None se não definido.
        """
        config_info = self.schema['configuracoes'].get(nome_configuracao.lower())
        return config_info.get('default') if config_info else None


    def return_valor_configuracao(self, configuracao_buscada: str) -> str|int|bool|None:
        """
        Busca o valor de uma configuração na settings.ini

        Args:
            configuracao_buscada (str): Nome da configuração a ser buscada.
        
        Returns:
            Valor da configuração convertido para o tipo correto ou None (caso de erro).
        """
        settings = self._ler_arquivo_configuracao()
        configuracao_buscada_lower = configuracao_buscada.lower()

        for secao in settings.sections():
            if configuracao_buscada_lower in settings[secao]:
                valor_raw = settings[secao][configuracao_buscada_lower]
                
                # Se configuração não está no schema, retorna string
                if configuracao_buscada_lower not in self.schema['configuracoes']:
                    return valor_raw
                
                # Converte para o tipo correto
                try:
                    return self._converter_valor_para_tipo_leitura(configuracao_buscada_lower, valor_raw)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao converter configuração '{configuracao_buscada}': {e}. Retornando valor original.")
                    return valor_raw
                    
        return None


    def obter_configuracao_segura(self, nome_configuracao: str, valor_padrao=None):
        """
        Método auxiliar para obter configurações de forma segura.
        
        Args:
            nome_configuracao (str): Nome da configuração.
            valor_padrao: Valor padrão caso a configuração não seja encontrada.
                         Se None, usa o valor padrão do schema.
            
        Returns:
            Valor da configuração ou valor padrão.
        """
        try:
            valor = self.return_valor_configuracao(nome_configuracao)
            if valor is not None:
                return valor
            
            # Se valor_padrao não foi fornecido, tenta usar o do schema
            if valor_padrao is None:
                valor_padrao = self.obter_valor_padrao(nome_configuracao)
                
            return valor_padrao
        except Exception as e:
            logger.error(f"Erro ao obter configuração '{nome_configuracao}': {e}")
            return valor_padrao


    def converter_string_para_bool(self, valor_str: str) -> bool:
        """
        Converte uma string para valor booleano.
        
        Args:
            valor_str (str): String a ser convertida.
            
        Returns:
            bool: Valor booleano correspondente.
        """
        if not isinstance(valor_str, str):
            return bool(valor_str)
        valor_str = valor_str.strip().lower()
        return valor_str in ["true", "verdade", "1", "yes", "sim"]


    def alterar_valor_configuracao(self, configuracao_ser_alterada: str, novo_valor: str) -> bool:
        """
        Altera o valor de uma configuração na settings.ini.

        Args:
            configuracao_ser_alterada (str): Nome da configuração a ser alterada.
            novo_valor (str): Novo valor para a configuração.
        
        Returns:
            bool: Indica se a configuração foi alterada com sucesso.
        
        Raises:
            ValueError: Se o novo_valor for incompatível com o tipo esperado da configuração.
            FileNotFoundError: Se um caminho especificado para arquivos não existir.
        """
        configuracao_ser_alterada = configuracao_ser_alterada.lower()

        # Validação específica para caminho do validator
        if configuracao_ser_alterada == "caminho_validator":
            self._validar_caminho_validator(novo_valor)
            return self._salvar_configuracao(configuracao_ser_alterada, novo_valor)

        # Validação para outras configurações usando o schema
        if configuracao_ser_alterada in self.schema['configuracoes']:
            try:
                novo_valor_convertido = self._converter_valor_para_tipo(configuracao_ser_alterada, novo_valor)
            except ValueError as e:
                tipo_configuracao = self._obter_tipo_configuracao(configuracao_ser_alterada)
                logger.error(f"Erro ao alterar configuração '{configuracao_ser_alterada}'. Valor inválido: {novo_valor}. Tipo esperado: {tipo_configuracao.__name__}.")
                raise ValueError(f"Novo valor para configuração inválido! Essa configuração é do tipo {tipo_configuracao.__name__}.") from e
            try:
                if isinstance(novo_valor_convertido, (int, float)):
                    self._validar_limites_configuracao(configuracao_ser_alterada, novo_valor_convertido)
                return self._salvar_configuracao(configuracao_ser_alterada, str(novo_valor_convertido))
            except ValueError as e:
                logger.error(f"Erro ao alterar configuração '{configuracao_ser_alterada}'. Novo valor está fora do escopo permitido!")
                raise ValueError(f"Erro ao alterar configuração '{configuracao_ser_alterada}'. Novo valor está fora do escopo permitido!") from e
            
        return False


    def _validar_caminho_validator(self, novo_valor: str):
        """
        Valida o caminho do validator usando as regras do schema.

        Args:
            novo_valor (str): Novo caminho do validator.

        Raises:
            FileNotFoundError: Se o caminho não existir.
            ValueError: Se a extensão do arquivo não for válida.
        """
        if novo_valor != "default":
            caminho_arquivo = Path(novo_valor)
            if not caminho_arquivo.is_absolute():
                caminho_arquivo = Path.cwd() / caminho_arquivo
                
            # Validação de existência
            limites = self._obter_limites_configuracao("caminho_validator")
            validation_rules = limites.get('validation', {})
            
            if validation_rules.get('must_exist', True) and not caminho_arquivo.exists():
                raise FileNotFoundError(f"Novo validator_cli não foi encontrado, endereço usado: {caminho_arquivo.resolve()}")
            
            # Validação de extensão
            extensoes_validas = validation_rules.get('file_extensions', [])
            if extensoes_validas and caminho_arquivo.suffix not in extensoes_validas:
                raise ValueError(f"Extensão de arquivo inválida. Extensões aceitas: {extensoes_validas}")


    def _converter_valor_para_tipo_leitura(self, configuracao: str, valor_str: str):
        """
        Converte o valor lido do arquivo para o tipo correto da configuração.

        Args:
            configuracao (str): Nome da configuração.
            valor_str (str): Valor a ser convertido.

        Returns:
            Valor convertido para o tipo correto.

        Raises:
            ValueError: Se o valor não puder ser convertido.
            TypeError: Se o tipo não for suportado.
        """
        tipo_configuracao = self._obter_tipo_configuracao(configuracao)

        if tipo_configuracao is bool:
            return self.converter_string_para_bool(valor_str)
        elif tipo_configuracao in (int, float):
            return tipo_configuracao(valor_str)
        elif tipo_configuracao is str:
            return valor_str
        else:
            raise TypeError(f"Tipo não suportado para conversão: {tipo_configuracao}")


    def _converter_valor_para_tipo(self, configuracao: str, novo_valor: str):
        """
        Converte o novo valor para o tipo correto da configuração (para salvamento).

        Args:
            configuracao (str): Nome da configuração.
            novo_valor (str): Valor a ser convertido.

        Returns:
            Valor convertido para string apropriada para salvamento.

        Raises:
            ValueError: Se o valor não puder ser convertido.
        """
        tipo_configuracao = self._obter_tipo_configuracao(configuracao)

        if tipo_configuracao is bool:
            if self.converter_string_para_bool(novo_valor):
                return "True"
            else:
                return "False"
        else:
            # Valida se pode ser convertido para o tipo (mas retorna como int/float para validação)
            return tipo_configuracao(novo_valor)


    def _validar_limites_configuracao(self, configuracao: str, novo_valor):
        """
        Valida se o novo valor está dentro dos limites definidos no schema.
        
        Args:
            configuracao (str): Nome da configuração.
            novo_valor: Valor a ser validado.
            
        Raises:
            ValueError: Se o valor estiver fora dos limites.
        """
        limites = self._obter_limites_configuracao(configuracao)
        
        # FIXED: Using correct keys 'minimum' and 'maximum' instead of 'minimo' and 'maximo'
        minimo = limites.get('minimum')
        maximo = limites.get('maximum')
        
        if minimo is not None and novo_valor < minimo:
            config_info = self.schema['configuracoes'].get(configuracao, {})
            descricao = config_info.get('description', f'configuração {configuracao}')
            raise ValueError(f"Valor muito baixo para {descricao}. Mínimo: {minimo}")
            
        if maximo is not None and novo_valor > maximo:
            config_info = self.schema['configuracoes'].get(configuracao, {})
            descricao = config_info.get('description', f'configuração {configuracao}')
            raise ValueError(f"Valor muito alto para {descricao}. Máximo: {maximo}")


    def _salvar_configuracao(self, configuracao: str, novo_valor: str) -> bool:
        """
        Salva a configuração no arquivo settings.ini.
        
        Args:
            configuracao (str): Nome da configuração.
            novo_valor: Novo valor da configuração.
            
        Returns:
            bool: True se a configuração foi salva com sucesso.
        """
        try:
            settings = self._ler_arquivo_configuracao()
            
            for secao in settings.sections():
                if configuracao in settings[secao]:
                    settings[secao][configuracao] = novo_valor
                    logger.info(f"Valor da configuração '{configuracao}' foi alterado para {novo_valor}")
                    break
                    
            self._escrever_arquivo_configuracao(settings)
            return True
        except FileNotFoundError as e:
            logger.error(f'Arquivo de configurações não encontrado: {e}')
            return False
        except PermissionError as e:
            logger.error(f'Permissão negada ao acessar o arquivo de configurações: {e}')
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar as '{configuracao}': {e}")
            return False


    def _ler_arquivo_configuracao(self) -> configparser.ConfigParser:
        """
        Lê o arquivo de configurações e retorna um objeto ConfigParser.
        
        Returns:
            configparser.ConfigParser: Objeto com as configurações carregadas.
        """
        settings = configparser.ConfigParser()
        settings.read(self.path_configuracoes, encoding='utf-8')
        return settings


    def _escrever_arquivo_configuracao(self, settings: configparser.ConfigParser) -> None:
        """
        Escreve as configurações no arquivo settings.ini.
        
        Args:
            settings (configparser.ConfigParser): Objeto com as configurações a serem salvas.
        """
        with open(self.path_configuracoes, 'w', encoding="utf-8") as configfile:
            settings.write(configfile)


    def listar_configuracoes(self) -> dict:
        """
        Lista todas as configurações disponíveis no schema.
        
        Returns:
            Dict: Dicionário com informações sobre as configurações.
        """
        return self.schema['configuracoes']


    def obter_categoria_configuracao(self, nome_configuracao: str) -> str:
        """
        Obtém a categoria de uma configuração.
        
        Args:
            nome_configuracao (str): Nome da configuração.
            
        Returns:
            str: Categoria da configuração ou "geral" se não definida.
        """
        config_info = self.schema['configuracoes'].get(nome_configuracao.lower(), {})
        return config_info.get('category', 'geral')