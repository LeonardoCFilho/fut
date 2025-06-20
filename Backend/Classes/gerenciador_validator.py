from pathlib import Path
from json import dump
from Backend.Classes.exceptions import ExcecaoTemplate
from Backend.Classes.arquivo_downloader import ArquivoDownloader
import time
import subprocess
import requests
import zipfile
import logging
import sys
import re

logger = logging.getLogger(__name__)


class GerenciadorValidator:
    # Constantes da classe
    URL_DOWNLOAD_VALIDADOR = "https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"
    URL_API_GITHUB = "https://api.github.com/repos/hapifhir/org.hl7.fhir.core/releases/latest"
    MAXIMO_TENTATIVAS_PADRAO = 3
    TEMPO_ESPERA_TENTATIVA = 300  # segundos

    # Construtor
    def __init__(self, caminho_validador: Path):
        """
        Inicializa o gerenciador do validator_cli
        
        Args:
            caminho_validador (Path): Caminho onde o validator_cli será armazenado
            
        Raises:
            TypeError: Se caminho_validador não for Path
            ValueError: Se diretório pai não existir
        """
        self._validar_path(caminho_validador)
        self.caminho_validador = caminho_validador


    def _validar_path(self, caminho: Path):
        """
        Valida o path fornecido para o validador
        
        Args:
            caminho (Path): Path a ser validado
            
        Raises:
            TypeError: Se não for instância de Path
            ValueError: Se diretório pai não existir
        """
        if not isinstance(caminho, Path):
            raise TypeError("caminho_validador deve ser uma instância Path")
        
        if not caminho.parent.exists():
            raise ValueError("Diretório pai deve existir")


    @staticmethod
    def _comparar_versoes(versao1: str, versao2: str) -> int:
        """
        Compara duas versões semanticamente
        
        Args:
            versao1 (str): Primeira versão a comparar
            versao2 (str): Segunda versão a comparar
            
        Returns:
            int: -1 se versao1 < versao2, 0 se iguais, 1 se versao1 > versao2
        """
        def _extrair_numeros(versao: str) -> list[int]:
            """Extrai números da versão, ignorando prefixos como 'v'"""
            versao_limpa = re.sub(r'^v', '', versao.strip())
            partes = re.findall(r'\d+', versao_limpa)
            return [int(parte) for parte in partes]
        
        numeros1 = _extrair_numeros(versao1)
        numeros2 = _extrair_numeros(versao2)
        
        # Equalizar tamanhos das listas
        tamanho_maximo = max(len(numeros1), len(numeros2))
        numeros1.extend([0] * (tamanho_maximo - len(numeros1)))
        numeros2.extend([0] * (tamanho_maximo - len(numeros2)))
        
        for n1, n2 in zip(numeros1, numeros2):
            if n1 < n2:
                return -1
            elif n1 > n2:
                return 1
        return 0


    @staticmethod
    def verificar_versao_validator(caminho_validador: Path) -> str|None:
        """
        Verifica a versão do validator_cli instalado
        
        Args:
            caminho_validador (Path): Caminho do arquivo validator_cli.jar
            
        Returns:
            str: Versão do validator ou None se erro
        """
        try:
            with zipfile.ZipFile(caminho_validador, 'r') as jar:
                with jar.open('fhir-build.properties') as manifest:
                    for linha in manifest:
                        linha_legivel = linha.decode(errors="ignore").strip()
                        if "orgfhir.version" in linha_legivel:
                            versao_encontrada = linha_legivel.split("orgfhir.version=")[1]
                            return versao_encontrada
            return None
        except (zipfile.BadZipFile, KeyError, FileNotFoundError, UnicodeDecodeError) as e:
            logger.warning(f"Não foi possível ler versão do validator: {e}")
            return None


    def _precisa_atualizar(self, versao_atual: str, versao_mais_recente: str) -> bool:
        """
        Determina se o validator precisa ser atualizado
        
        Args:
            versao_atual (str): Versão atualmente instalada
            versao_mais_recente (str): Versão mais recente disponível
            
        Returns:
            bool: True se atualização necessária
        """
        if not versao_atual or not versao_mais_recente:
            return True
        
        return self._comparar_versoes(versao_atual, versao_mais_recente) < 0


    def _obter_versao_mais_recente_github(self, tempo_timeout: int) -> str:
        """
        Obtém a versão mais recente do validator no GitHub
        
        Args:
            tempo_timeout (int): Timeout para requisições HTTP
            
        Returns:
            str: Versão mais recente ou None se erro
        """
        numero_tentativas = 0
        while numero_tentativas < self.MAXIMO_TENTATIVAS_PADRAO:
            try:
                logger.info("Buscando ultima versao no git")
                resposta = requests.get(self.URL_API_GITHUB, timeout=tempo_timeout)
                
                if resposta.status_code == 200:
                    dados_git = resposta.json()
                    return dados_git.get('tag_name')
                else:
                    logger.debug(f"Requisição falhou com código {resposta.status_code}")
                    return None
                    
            except (requests.exceptions.RequestException, ValueError) as e:
                numero_tentativas += 1
                if numero_tentativas < self.MAXIMO_TENTATIVAS_PADRAO:
                    logger.warning(f"Erro na tentativa {numero_tentativas} de conexão com git")
                    print(f"Erro na tentativa {numero_tentativas} de conexão, reiniciando...")
                    time.sleep(self.TEMPO_ESPERA_TENTATIVA)
                else:
                    logger.warning(f"Erro ao conectar com github do validator_cli: {e}")
                    versao_local = self.verificar_versao_validator(self.caminho_validador)
                    if versao_local:
                        print(f"Não foi possível atualizar o validator_cli, executando com versão '{versao_local}'")
                    raise e
        return None


    def instalar_validator_cli(self, downloader_callback: ArquivoDownloader, path_customizado: Path = None) -> None:
        """
        Faz a instalação inicial do validator_cli
        
        Args:
            downloader_callback (ArquivoDownloader): Instancia para fazer o download
            path_customizado (Path, optional): Caminho customizado para instalação
        
        Raises:
            requests.exceptions.ConnectionError: Erro de conexão
            Exception: Outros erros durante instalação
        """        
        caminho_instalacao = path_customizado or self.caminho_validador
        if not caminho_instalacao.exists():  # Evitar sobrescrita
            try:
                logger.info("Fazendo download do validator_cli")
                # Timeout de 20 minutos
                downloader_callback.baixar_arquivo(
                    self.URL_DOWNLOAD_VALIDADOR, 
                    caminho_instalacao, 
                )
            except Exception as e:
                logger.fatal(f"Erro ao instalar o validator_cli: {e}")
                raise e


    def atualizar_validator_cli(self, tempo_timeout_requests: int, downloader_callback: ArquivoDownloader):
        """
        Atualiza o validator_cli para a versão mais recente
        
        Args:
            tempo_timeout_requests (int): Timeout para requisições HTTP
            downloader_callback (ArquivoDownloader): Instancia de ArquivoDownloader que fará os download
            
        Raises:
            requests.exceptions.Timeout: Timeout nas requisições
            requests.exceptions.ConnectionError: Erro de conexão
            ExcecaoTemplate: Arquivo validator inválido
        """
        logger.info("Buscando atualizações do validator_cli")

        # Verificar se o validator já existe
        if self.caminho_validador.exists():
            # Verificar versão atual
            try:
                versao_atual = self.verificar_versao_validator(self.caminho_validador)
            except Exception as e:
                raise ExcecaoTemplate("Arquivo validator_cli inválido", e)

            # Obter versão mais recente
            versao_mais_recente = self._obter_versao_mais_recente_github(tempo_timeout_requests)
            
            if versao_mais_recente and self._precisa_atualizar(versao_atual, versao_mais_recente):
                self._executar_atualizacao(downloader_callback)
            else:
                logger.info("Verificação de atualização finalizada")
        else:
            logger.info("Nenhuma instância de validator_cli encontrada, iniciando download")
            print("O validator padrão não foi encontrado ou não existe!\nIniciando sua instalação.")
            self.instalar_validator_cli(downloader_callback)


    def atualizar_validator_cli_seguro(self, tempo_timeout_requests: int, downloader_callback: ArquivoDownloader=None) -> bool:
        """
        Versão segura que lida com erros sem interromper o programa principal
        
        Args:
            tempo_timeout_requests (int): Timeout para requisições HTTP
            downloader_callback (ArquivoDownloader): Instancia de ArquivoDownloader que fará os download
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
        """
        try:
            if not downloader_callback:
                downloader_callback = ArquivoDownloader(self.TEMPO_ESPERA_TENTATIVA)
            self.atualizar_validator_cli(tempo_timeout_requests, downloader_callback)
            return True
        except ExcecaoTemplate as e:
            logger.fatal(f"O arquivo do validator_cli é inválido: {e}")
            sys.exit("Arquivo validator_cli é inválido, verifique seu download ou considere utilizar o validator padrão")
        except requests.exceptions.ConnectionError:
            logger.warning("Erro de conexão ao tentar atualizar validator - continuando com versão atual")
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar o validator: {e}")
            return False


    def _executar_atualizacao(self, downloader_callback: ArquivoDownloader):
        """
        Executa o processo de atualização do validator
        
        Args:
            downloader_callback (ArquivoDownloader): Instancia de ArquivoDownloader que fará o download
        
        Raises:
            Exception: Erros durante processo de atualização
        """
        try:
            caminho_temporario = self.caminho_validador.with_name("temp_validator_cli.jar")
            
            # Fazer download da nova versão usando o downloader_callback
            logger.info("Fazendo download da nova versão do validator_cli")
            self.instalar_validator_cli(downloader_callback, caminho_temporario)
            logger.info("Download da versão mais recente concluído")
            
            # Substituir arquivo antigo
            if caminho_temporario.exists():
                logger.info("Atualizando o validator_cli")
                self.caminho_validador.unlink()  # Remove arquivo antigo
                caminho_temporario.rename(self.caminho_validador)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar validator: {e}")
            raise e
        

    def validar_arquivo_fhir(self, arquivo_validar: Path, pasta_relatorio: Path, num_teste: int, tempo_timeout: int, java_path: Path = None, argumentos_extras: str = None) -> list:
        """
        Executa validação do arquivo FHIR usando validator_cli.jar
        
        Args:
            arquivo_validar (Path): Arquivo FHIR a ser validado
            pasta_relatorio (Path): Pasta onde relatório será salvo
            num_teste (int): Número do teste
            tempo_timeout (int): Timeout para execução
            java_path (Path): Caminho para o executável Java (opcional)
            argumentos_extras (str): Argumentos adicionais para validação
            
        Returns:
            List: [Caminho do relatório JSON, Tempo de execução em segundos]
            
        Raises:
            FileNotFoundError: Arquivo não encontrado
            Exception: Outros erros durante validação
        """
        
        arquivo_validar = arquivo_validar.expanduser()
        if not arquivo_validar.is_absolute():
            arquivo_validar = Path.cwd() / arquivo_validar

        try:
            if not arquivo_validar.exists():
                logger.warning(f"Arquivo não encontrado: {arquivo_validar}")
                raise FileNotFoundError(f"Arquivo de entrada não encontrado: {arquivo_validar}")

            nome_relatorio = f"{arquivo_validar.stem}_{str(num_teste)}.json"
            caminho_relatorio = pasta_relatorio / nome_relatorio
            
            # Usa o java_path fornecido ou fallback para "java" do sistema
            java_executable = str(java_path.resolve()) if java_path else "java"
            
            comando = [
                java_executable, '-Dfile.encoding=UTF-8', "-jar", str(self.caminho_validador.resolve()),
                str(arquivo_validar.resolve()),
                "-output", str(caminho_relatorio.resolve()),
                "-version", "4.0.1"
            ]
            
            if argumentos_extras:
                comando += argumentos_extras if isinstance(argumentos_extras, list) else [argumentos_extras]

            inicio = time.time()
            resultado = subprocess.run(
                comando, 
                capture_output=True, 
                text=True, 
                timeout=tempo_timeout
            )
            fim = time.time()
            #print(resultado.returncode)

            # Criar relatório manual se não foi gerado
            if not caminho_relatorio.exists():
                self._criar_relatorio_erro(
                    caminho_relatorio,
                    "non-existent ig or resource or profile"
                )

            return [caminho_relatorio, (fim - inicio)]

        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout na validação de {arquivo_validar}")
            self._criar_relatorio_timeout(caminho_relatorio, tempo_timeout)
            return [caminho_relatorio, tempo_timeout]
        
        # Exceções aqui provavelmente são problemas do código, não do validator
        except Exception as e:
            logger.error(f"Erro durante validação do arquivo FHIR: {e}")
            raise e


    def _criar_relatorio_erro(self, caminho_relatorio: Path, mensagem_erro: str) -> None:
        """
        Cria relatório JSON para casos de erro
        
        Args:
            caminho_relatorio (Path): Onde salvar o relatório
            mensagem_erro (str): Mensagem de erro a incluir
        """
        dicionario_erro = {
            'issue': [{
                'severity': 'fatal',
                'code': 'non-existent',
                'details': {'text': mensagem_erro},
                'expression': []
            }]
        }
        
        with open(caminho_relatorio, mode="w", encoding="utf8") as arquivo:
            dump(dicionario_erro, arquivo, indent=4, ensure_ascii=False)


    def _criar_relatorio_timeout(self, caminho_relatorio: Path, tempo_timeout: int) -> None:
        """
        Cria relatório JSON para casos de timeout
        
        Args:
            caminho_relatorio (Path): Onde salvar o relatório
            tempo_timeout (int): Tempo de timeout que ocorreu
        """
        mensagem_timeout = f"tentativa de validar arquivo excedeu {tempo_timeout} segundos"
        self._criar_relatorio_erro(caminho_relatorio, mensagem_timeout)