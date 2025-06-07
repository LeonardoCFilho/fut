from pathlib import Path
import configparser
import logging

logger = logging.getLogger(__name__)

class ControladorConfiguracao:
    """
    Gerencia a leitura e alteração de configurações do sistema
    a partir do arquivo settings.ini.
    """

    def __init__(self, path_configuracoes: Path):
        """
        Inicializa o gerenciador de configurações.

        Args:
            path_configuracoes (Path): Caminho para o arquivo de configurações.
        """
        self.path_configuracoes = path_configuracoes
        self.dict_configuracoes = {
            "timeout": int,
            "max_threads": int,
            "caminho_validator": str,
            "requests_timeout": int,
            "armazenar_saida_validator": bool,
        }


    def return_valor_configuracao(self, configuracao_buscada: str) -> str | None:
        """
        Busca o valor de uma configuração na settings.ini

        Args:
            configuracao_buscada (str): Nome da configuração a ser buscada.
        
        Returns:
            Valor da configuração ou None (caso de erro).
        """
        settings = self._ler_arquivo_configuracao()
        configuracao_buscada_lower = configuracao_buscada.lower()

        for secao in settings.sections():
            if configuracao_buscada_lower in settings[secao]:
                valor_raw = settings[secao][configuracao_buscada_lower]
                
                # Se configuração não está no dicionário, retorna string
                if configuracao_buscada_lower not in self.dict_configuracoes:
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
            
        Returns:
            Valor da configuração ou valor padrão.
        """
        try:
            valor = self.return_valor_configuracao(nome_configuracao)
            return valor if valor is not None else valor_padrao
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
            ...
        """
        configuracao_ser_alterada = configuracao_ser_alterada.lower()

        # Validação específica para caminho do validator
        if configuracao_ser_alterada == "caminho_validator":
            self._validar_caminho_validator(novo_valor)
            return self._salvar_configuracao(configuracao_ser_alterada, novo_valor)

        # Validação para outras configurações
        if configuracao_ser_alterada in self.dict_configuracoes:
            try:
                novo_valor_convertido = self._converter_valor_para_tipo(configuracao_ser_alterada, novo_valor)
                if isinstance(novo_valor_convertido, (int, float)):
                    self._validar_limites_configuracao(configuracao_ser_alterada, novo_valor_convertido)
                return self._salvar_configuracao(configuracao_ser_alterada, str(novo_valor_convertido))
            except ValueError as e:
                tipo_configuracao = self.dict_configuracoes[configuracao_ser_alterada]
                logger.error(f"Erro ao alterar configuração '{configuracao_ser_alterada}'. Valor inválido: {novo_valor}. Tipo esperado: {tipo_configuracao.__name__}.")
                raise ValueError(f"Novo valor para configuração inválido! Essa configuração é do tipo {tipo_configuracao.__name__}.") from e

        return False


    def _validar_caminho_validator(self, novo_valor: str) -> None:
        """
        Valida o caminho do validator.

        Args:
            novo_valor (str): Novo caminho do validator.

        Raises:
            FileNotFoundError: Se o caminho não existir.
        """
        if novo_valor != "default":
            caminho_arquivo = Path(novo_valor)
            if not caminho_arquivo.is_absolute():
                caminho_arquivo = Path.cwd() / caminho_arquivo
            if not caminho_arquivo.exists():
                raise FileNotFoundError(f"Novo validator_cli não foi encontrado, endereço usado: {caminho_arquivo.resolve()}")
        # Quando o novo_valor for 'default' GestorCaminhos vai lidar com endereçamento em tempo real


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
        tipo_configuracao = self.dict_configuracoes[configuracao]

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
        tipo_configuracao = self.dict_configuracoes[configuracao]

        if tipo_configuracao is bool:
            if self.converter_string_para_bool(novo_valor):
                return "True"
            else:
                return "False"
        else:
            # Valida se pode ser convertido para o tipo (mas retorna como int/float para validação)
            return tipo_configuracao(novo_valor)


    def _validar_limites_configuracao(self, configuracao: str, novo_valor) -> None:
        """
        Valida se o novo valor está dentro dos limites aceitáveis.
        
        Args:
            configuracao (str): Nome da configuração.
            novo_valor: Valor a ser validado.
            
        Raises:
            ValueError: Se o valor estiver fora dos limites.
        """
        if configuracao in ('timeout', 'requests_timeout') and novo_valor < 15:
            raise ValueError("A configuração de timeout necessita de pelo menos 15 segundos para garantir execução.")
        if configuracao == "max_threads" and novo_valor < 1:
            raise ValueError("O número de máximo de threads tem que ser maior que 0!")


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