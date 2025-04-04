class ExecutorTestes:   
    # Construtor
    def __init__(self):
        # pathFut será o endereço para a pasta root
        from pathlib import Path
        self.pathFut = Path.cwd() # Caminho atual
        if "Backend" in self.pathFut.name: # Subir um nível se o diretório atual for 'Backend'
            self.pathFut = self.pathFut.parent  
        
        # Caminho do validator (se o usuário especificar um)
        # Outras variáveis

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
    def validarArquivoFhir(self, arquivoValidar, args=None, pathValidatorCli=None):
        import subprocess, time
        from pathlib import Path
        # Se é para usar o nosso validador padrão ou não
        self.atualizarValidatorCli()
        if not pathValidatorCli:  # Usuário não solicitou validator especial => usar o padrão
            pathValidatorCli = self.pathFut / "Backend"/ "validator_cli.jar"
        # Organizar o endereçamento do arquivo a ser validado
        if not isinstance(arquivoValidar, Path):
            arquivoValidar = Path(arquivoValidar).expanduser()# Encontrando o arquivo
        if not arquivoValidar.is_absolute(): # Não é caminho absoluto => criar o caminho de acordo com pathFut
            arquivoValidar = Path(self.pathFut).resolve() / arquivoValidar
        # Iniciar a validação
        try:
            if arquivoValidar.exists():
                # Comando que será executado no subprocess
                # args+=["-output", "teste.json"]
                comando = ["java", "-jar", str(pathValidatorCli.resolve()), str(arquivoValidar.resolve()), "-version", "4.0.1"]
                if args:  # Se context ter sido fornecido, args conterá os argumentos do contexto
                    comando += args  # Espera-se que args seja uma string formatada ou uma lista de strings
                start = time.time()
                resultado = subprocess.run(comando, capture_output=True, text=True)
                print(f"Arquivo validado em: {time.time() - start:.2f} segundos")  # Exibir quantos segundos cada iteração levou
                #print(resultado)
                return resultado
            else:
                raise FileNotFoundError("Arquivo de entrada não foi encontrado")
        except Exception as e:
            raise e  # Diagnóstico fácil em caso de erro
    
    # Ideia: Função recebe um arquivo de teste e valida ele, se for válido chama validarArquivoFhir()
    # P.s.: referencia: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
    def validarArquivoTeste(self, arquivoTeste):
        pass

    # Ideia: Função recebe o caminho de uma pasta e válida todos os arquivos através de validarArquivoTeste()
    def validarPasta(self, pathPasta):
        #concurrent.futures
        pass