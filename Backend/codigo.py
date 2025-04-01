# Link do colab do código: https://colab.research.google.com/drive/1R8RTxAQ72TZ1_HfuM1KpnZw3b0XzbCNd#scrollTo=h3tl_P7uwiQy

# temp
caminho_do_arquivo_fhir_que_voce_quer_validar = "../Arquivos/Testes/ArquivosFHIR/zzrandom_com_erros.json"

# Ideia: Função recebe uma url qualquer e tenta baixar um arquivo com nome/endereço enderecoArquivo
# P.s.: Nome do arquivo precisa do tipo do arquivo (.jar, .tgz, etc), mandar caminho absoluto ou apenas o nome do arquivo (nesse caso será salvo na pasta 'Backend')
def baixaArquivoUrl(url, enderecoArquivo):
    import requests
    try:
        # Request inicial
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Caso de erro
        # Iniciando download em si
        with open(enderecoArquivo, "wb") as arquivoBaixado:
            for chunk in response.iter_content(chunk_size=8192):
                arquivoBaixado.write(chunk)
    # Erros, adicionar logging e alterar isso para o front depois
    #except requests.exceptions.RequestException as e:
    #    print(f"Erro no download: {e}")
    except Exception as e:
        return e


# Ideia: Função instala ou atualiza o validator_cli.jar
# P.s.: Esse validator será instalado na pasta Backend e funcionará como o nosso validador padrão (usuário poderá escolher o dele pelas configurações)
def atualizarValidatorCli():
    linkDownloadValidator = "https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"
    import os , zipfile, requests
    if os.path.exists("validator_cli.jar"): # Verificar se já está instalado
        # Está instalado => verificar última versão
        # 1º verificar a versão do validator baixado
        versaoBaixada = None
        versaoGit = None
        try:
            with zipfile.ZipFile("validator_cli.jar", 'r') as jar:
                with jar.open('fhir-build.properties') as manifest: # Arquivo que eu achei com versão (Não achei manifest)
                    for linha in manifest:
                        linhaLegivel = linha.decode('utf-8').strip()
                        if "orgfhir.version" in linhaLegivel:
                            versaoBaixada = linhaLegivel.split("orgfhir.version=")[1]
        # Erros, adicionar logging e alterar isso para o front depois
        except Exception as e:
            return e
        # Não deu erros até aqui => verificar última versão no git
        try:
            api_url = "https://api.github.com/repos/hapifhir/org.hl7.fhir.core/releases/latest"
            # Criar request
            response = requests.get(api_url)
            if response.status_code == 200: # Sucesso
                dadosGit = response.json()
                versaoGit = dadosGit.get('tag_name')  # Versão é a tag dessa
            # Erros, adicionar logging e alterar isso para o front depois
            else: # Qualquer outra coisa
                return response.status_code
        # Erros, adicionar logging e alterar isso para o front depois
        except Exception as e:
            return e
        # Comparar as versões
        if versaoBaixada != versaoGit:
            # Instalar a nova
            try: 
                baixaArquivoUrl(linkDownloadValidator, "NOVOvalidator_cli.jar") # nome temporário (para não subscrever a versão antiga)
            # Erros, adicionar logging e alterar isso para o front depois
            except Exception as e:
                return e
            # Não deu erro => nova versão foi instalada
            if os.path.exists("NOVOvalidator_cli.jar"): # por segurança
                # removendo a antiga
                os.remove("validator_cli.jar") 
                # renomeando a nova
                os.rename("NOVOvalidator_cli.jar", "validator_cli.jar")
    else:
        # Não está instalado => fazer a instalação
        try: 
            baixaArquivoUrl(linkDownloadValidator, "validator_cli.jar")
        # Erros, adicionar logging e alterar isso para o front depois
        except Exception as e:
            return e

# Ideia: Função recebe o caminho do validator_cli e um arquivo a ser testado
# P.s.: Essa função apenas realiza o teste e retorna os resultados (Não faz limpeza na entrada nem da saída)
def validarArquivoFhir(arquivoValidar: str, args = None, pathValidatorCli: str = None): # Eventualmente pathValidatorCli vai ter um valor padrão (caminho será armazenado no manifest)
    import subprocess, os
    # Se é para usar o nosso validador padrão ou não
    if not pathValidatorCli: # Usuário não solicitou validator especial => usar o padrão (Estará na pasta backend)
        atualizarValidatorCli()
        pathValidatorCli = "validator_cli.jar"
    # Iniciar a validação
    try:
        # comando que será executado no subprocess
        comando = ["java", "-jar", os.path.abspath(pathValidatorCli), os.path.abspath(arquivoValidar), "-output", "teste.json", "-version", "4.0.1"] # Version se refere ao tipo de padrão FHIR, não a versão do validator
        if args: # Se context ter sido fornecido, args conterá os argumentos do contexto
            comando += args # Espera-se que args seja uma string formatada ou uma lista de strings
        # resultado da execução do subprocess
        resultado = subprocess.run(comando, capture_output=True, text=True)
        return resultado # Um json
    # Erros, adicionar logging e alterar isso para o front depois
    except Exception as e:
        return None # Caso de erro, diagnóstico fácil

# Teste com um arquivo JSON/XML
resultado = validarArquivoFhir(caminho_do_arquivo_fhir_que_voce_quer_validar)

# Abaixo, a saída da função validar_fhir é formatada para, dentro do dicionário dicio, capturar os campos: warning, error, note, fatal, dentre outros
dicio = None
if resultado:
    formatado = resultado.stdout.split("\n")
    dicio = {'erro': [], 'warning': [], 'note': [], 'fatal': [], 'else': []}
    for linha in formatado:
        if 'warning @' in linha.lower():
            dicio['warning'].append(linha)
        elif 'error @' in linha.lower():
            dicio['erro'].append(linha)
        elif 'note @' in linha.lower():
            dicio['note'].append(linha)
        elif 'fatal @' in linha.lower():
            dicio['fatal'].append(linha)
        elif '@' in linha:
            dicio['else'].append(linha)

if dicio:
    import json
    print(json.dumps(dicio, ensure_ascii=False, indent=4))
else:
    print("Ocorreu algum erro")