from pathlib import Path
import configparser
class ExecutorTestes:   
    # Construtor
    def __init__(self, pathFut:Path):
        # pathFut será o endereço para a pasta root
        self.pathFut = pathFut
        # Validator
        verificandoValidator = self._verificaValidator(pathFut)
        self.pathValidator = Path(verificandoValidator)
        # Variavel para armazenar timeout
        config = configparser.ConfigParser()
        config.read(Path(pathFut / "Backend" / "settings.ini").resolve(), encoding='utf-8')
        self.timeout = int(config.get('hardware', 'timeout').split('#')[0].strip())
        # Outras variáveis

    # Ideia: Verifica no settings.ini a localização do validator_cli e se ele existe
    # P.s.: Essa função é usada diretamente no construtor do objeto, editar com cautela
    def _verificaValidator(self, pathFut:Path):
        pathSettings = pathFut / "Backend" / "settings.ini"
        if pathSettings.exists():
            # Ler o settings.ini
            config = configparser.ConfigParser()
            config.read(pathSettings.resolve(), encoding='utf-8')
            caminhoValidatorSettings = Path(config.get('enderecamento', 'pathValidator_cli').split('#')[0].strip())
            # Caminho não é absoluto => validator_cli é o padrão
            if not caminhoValidatorSettings.is_absolute():
                caminhoValidatorSettings = pathFut / caminhoValidatorSettings
            if caminhoValidatorSettings.exists():
                return caminhoValidatorSettings
            else:
                raise FileNotFoundError("validator_cli.jar não foi encontrado! Tente retornar seu valor ao padrão")
        else:
            raise FileNotFoundError("Arquivo settings.ini não foi encontrado")

    # Ideia: Função recebe uma url qualquer e tenta baixar um arquivo com nome/endereço enderecoArquivo
    # P.s.: Nome do arquivo precisa do tipo do arquivo (.jar, .tgz, etc), mandar caminho absoluto ou apenas o nome do arquivo (nesse caso será salvo na pasta 'Backend')
    def baixaArquivoUrl(self, url, enderecoArquivo):
        # implementar requests timeout & retry
        import requests, os
        try:
            # Request inicial
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Caso de erro

            # Iniciando download em si
            with open(os.path.abspath(enderecoArquivo), "wb") as arquivoBaixado:
                for chunk in response.iter_content(chunk_size=8192):
                    arquivoBaixado.write(chunk)

        # Erros, adicionar logging e alterar isso para o front depois
        except Exception as e:
            raise e

    # Ideia: Função instala ou atualiza o validator_cli.jar
    # P.s.: Esse validator será instalado na pasta Backend e funcionará como o nosso validador padrão (usuário poderá escolher o dele pelas configurações)
    def atualizarValidatorCli(self):
        linkDownloadValidator = "https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"
        import zipfile, requests

        # Garantindo que o validator será instalado no local correto (pasta Backend)
        caminhoValidator = self.pathFut / "Backend" / "validator_cli.jar"

        # Iniciando as verificações
        if caminhoValidator.exists(): # Verificar se já está instalado
            # Está instalado => verificar última versão
            versaoBaixada = None
            versaoGit = None

            # 1º verificar a versão do validator baixado
            try:
                with zipfile.ZipFile(caminhoValidator, 'r') as jar:
                    with jar.open('fhir-build.properties') as manifest: # Arquivo que eu achei com versão (Não achei manifest)
                        for linha in manifest:
                            linhaLegivel = linha.decode(errors="ignore").strip()
                            if "orgfhir.version" in linhaLegivel:
                                versaoBaixada = linhaLegivel.split("orgfhir.version=")[1]
            # Erros, adicionar logging e alterar isso para o front depois
            except Exception as e:
                raise e

            # 2º verificar última versão no git
            try:
                api_url = "https://api.github.com/repos/hapifhir/org.hl7.fhir.core/releases/latest"
                # Criar request
                # adicionar tentativas extras?
                response = requests.get(api_url)
                if response.status_code == 200: # Sucesso
                    dadosGit = response.json()
                    versaoGit = dadosGit.get('tag_name')  # Versão é a tag dessa
                # Erros, adicionar logging e alterar isso para o front depois
                else: # Qualquer outra coisa
                    return response.status_code
            # Erros, adicionar logging e alterar isso para o front depois
            except Exception as e:
                raise e

            # 3º Verificar se foram encontradas, se sim compará-las
            if (versaoBaixada and versaoGit) and versaoBaixada != versaoGit: # Há uma versão mais recente
                # Instalar a nova
                try: 
                    caminhoValidatorTemp = caminhoValidator.with_name("NOVOvalidator_cli.jar")
                    self.baixaArquivoUrl(linkDownloadValidator, caminhoValidatorTemp) # nome temporário (para não subscrever a versão antiga)
                # Erros, adicionar logging e alterar isso para o front depois
                except Exception as e:
                    raise e

                # Não deu erro => nova versão foi instalada
                if caminhoValidatorTemp.exists(): # por segurança
                    # removendo a antiga
                    caminhoValidator.unlink()  
                    # renomeando a nova
                    caminhoValidatorTemp.rename(caminhoValidator)  
        else:
            # Não está instalado => fazer a instalação
            try:
                self.baixaArquivoUrl(linkDownloadValidator, caminhoValidator)
            # Erros, adicionar logging e alterar isso para o front depois
            except Exception as e:
                raise e
    
    # Ideia: Função recebe o caminho do validator_cli e um arquivo a ser testado
    # P.s.: Essa função apenas realiza o teste e retorna os resultados (Não faz limpeza na entrada nem da saída)
    def validarArquivoFhir(self, arquivoValidar, args=None):
        import subprocess, time

        # Se é o validator padrão => tentar atualizar
        if self.pathValidator.is_relative_to(self.pathFut):
            self.atualizarValidatorCli()

        # Organizar o endereçamento do arquivo a ser validado
        arquivoValidar = Path(arquivoValidar).expanduser() # Encontrando o arquivo
        if not arquivoValidar.is_absolute(): # Não é caminho absoluto => criar o caminho de acordo com endereço atual
            arquivoValidar = Path.cwd() / arquivoValidar
        
        # Pasta para os resultados do validator
        config = configparser.ConfigParser()
        config.read(Path(self.pathFut / 'Backend' / 'settings.ini').resolve(), encoding='utf-8')
        flagSalvarOutput = config.getboolean('enderecamento', 'flagArmazenarSaidaValidator')
        if flagSalvarOutput == True:
            pastaRelatorio = Path.cwd() / "resultados-validator_cli"
            pastaRelatorio.mkdir(exist_ok=True)
        else:
            pastaRelatorio = Path.cwd() / ".temp-fut"
            pastaRelatorio.mkdir(exist_ok=True)
            
        # Iniciar a validação
        try:
            if arquivoValidar.exists():
                # Comando que será executado no subprocess
                nomeRelatorio = str(arquivoValidar.with_suffix(".json").name)
                caminhoRelatorio = pastaRelatorio / nomeRelatorio
                comando = ["java", "-jar", str(self.pathValidator.resolve()), # validator 
                           str(arquivoValidar.resolve()), # Arquivo de entrada
                           "-output", str(caminhoRelatorio.resolve()), # Relatório do validator_cli
                           "-version", "4.0.1"] # Versão pre-definida de arquivos FHIR
                # Argumentos adicionais (context)
                if args:  
                    comando += args if isinstance(args, list) else [args] # Espera-se que args seja uma string formatada ou uma lista de strings
                
                # Executando o comando
                start = time.time()
                resultado = subprocess.run(comando, capture_output=True, text=True, timeout=self.timeout)
                end = time.time()
                #print("temp ----------------------------------------------------------------------------------------------------------------------------------------------------------------")
                #print(resultado)
                #print("temp ----------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")
                return [caminhoRelatorio, (end-start)]
            else:
                raise FileNotFoundError(f"Arquivo de entrada não foi encontrado {arquivoValidar}")
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(f"Timeout na validação de: {arquivoValidar}") from e
        except Exception as e:
            raise e  # Diagnóstico fácil em caso de erro
    
    # Ideia: Função recebe um arquivo de teste e valida ele, se for válido chama validarArquivoFhir()
    # P.s.: referencia schema.json na pasta Backend
    def validarArquivoTeste(self, arquivoTeste):
        import yaml, json, jsonschema
        # Ideia: Recebe um dicionário e retorna ele como um dicionário válido para essa função
        def limparEntrada(data:dict):
            if isinstance(data, dict):
                for key, value in data.items():
                    data[key] = limparEntrada(value)
            elif isinstance(data, list):
                data = [item if item is not None else "" for item in data]
            return data
        
        # Iniciar o sistema
        try:
            # Ler o arquivo para validar .yaml
            with open(Path(self.pathFut / 'Backend' / 'schema.json').resolve(), 'r') as jsonSchema:
                schema = json.load(jsonSchema)
            # Tentar ler o arquivo .yaml
            with open(arquivoTeste, "r") as file:
                data = yaml.safe_load(file)
                data = limparEntrada(data)

            # Validar o arquivo .yaml
            try:
                jsonschema.validate(instance=data, schema=schema)
                flagYamlValido = True # Arquivo é válido
            except jsonschema.exceptions.ValidationError as e:
                # Aumentar feedback para o usuário dps
                print(e)
                flagYamlValido = False # Deu erro => arquivo é inválido
                outputValidacao = [None, -1]
            
            # Se válido => testar o arquivo FHIR
            if flagYamlValido:
                argsArquivoFHIR = ''
                if len(data['context']['igs']) > 0:
                    argsArquivoFHIR = argsArquivoFHIR + " -ig ".join(data['context']['igs'])
                if len(data['context']['profiles']) > 0:
                    argsArquivoFHIR = argsArquivoFHIR = " -profile ".join(data['context']['profiles'])
                if len(data['context']['resources']) > 0: # Aparentemente ig aceita (testar mais a fundo)
                    argsArquivoFHIR = argsArquivoFHIR + " -ig ".join(data['context']['resources'])
                outputValidacao = self.validarArquivoFhir(data['caminho_instancia'], args= argsArquivoFHIR)

            # Retornar os dados 
            dictDadosTeste = {
                'caminho_yaml': arquivoTeste,
                'yaml_valido': flagYamlValido,
                'caminho_output': outputValidacao[0],
                'tempo_execucao': outputValidacao[1],
            }
            return dictDadosTeste
        
        except yaml.YAMLError as e:
            raise e("Arquivo de teste não é um .yaml válido!")
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo .yaml não foi encontrado!")
        except Exception as e:
            raise e

    # Ideia: Função recebe o caminho de uma pasta e válida todos os arquivos através de validarArquivoTeste()
    def receberArquivosValidar(self, argsEntrada):
        # Validar instancia java
        #import shutil
        #if shutil.which("java") is None:
        #    raise RuntimeError("Java is not installed or not found in PATH.")

        # Threads
        #concurrent.futures
        #import configparser
        # Ler a entrada
        if len(argsEntrada) == 0: # Ler a pasta inteira
            arquivosYaml = Path.cwd().glob('*.yaml')
        else: # Ler os arquivos em esepecífico
            arquivosYaml = [] # Lista para inserir todos os caminhos
            # Garantir que a entrada é uma lista
            if isinstance(argsEntrada, str):
                argsEntrada = [argsEntrada]
            # Ler argsEntrada inteira
            for pathArquivoValidar in argsEntrada:
                # Endereçar o arquivo
                pathArquivoAtual = Path(pathArquivoValidar)
                if not pathArquivoAtual.is_absolute():
                    pathArquivoAtual = Path.cwd() / pathArquivoAtual
                # Adicionar a lista
                if pathArquivoAtual.suffix == ".yaml" and pathArquivoAtual.exists():
                    arquivosYaml.append(pathArquivoAtual)
                elif pathArquivoAtual.with_suffix(".json").exists():
                    arquivosYaml.append(pathArquivoAtual.with_suffix(".json"))

        # Iniciar a validação
        listaArquivosTeste = []
        for arquivoValidar in arquivosYaml:
            try:
                # Tentar validar o arquivo e insire a output na lista
                listaArquivosTeste.append(self.validarArquivoTeste(arquivoValidar))
            # Erros, adicionar logging e alterar isso para o front depois
            except Exception as e:
                print(f"Erro ao validar arquivo: {e}")

        # Trigger para a criação do relatório final aqui
        # temp
        print(arquivosYaml)
        print(listaArquivosTeste)