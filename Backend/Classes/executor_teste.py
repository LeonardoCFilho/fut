from pathlib import Path
import yaml
import json
import jsonschema
from Classes.inicializador_sistema import InicializadorSistema
import subprocess
import logging
logger = logging.getLogger(__name__)

class ExecutorTestes(InicializadorSistema):
    def __init__(self, pathFut):
        super().__init__(pathFut)
    
    # Ideia: Padronizar as informações recebidas do arquivo de teste
    def limparEntrada(self, data):
        if isinstance(data, dict):
            return {key: self.limparEntrada(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.limparEntrada(item) if item is not None else "" for item in data]
        return data

    # Ideia: Valida um arquivo YAML usando o schema JSON e, se válido, chama a validação FHIR.
    def validarArquivoTeste(self, arquivoTeste: Path):
        # Schema para validar o arquivo de teste
        schemaPath = self.pathFut / "Backend" / "schema.json"
        with open(schemaPath, 'r', encoding="utf-8") as jsonSchemaFile:
            schema = json.load(jsonSchemaFile)
        # Arquivo de teste
        if arquivoTeste.suffix == ".json":
            with open(arquivoTeste, "r", encoding="utf-8") as file:
                data = json.load(file)  
        elif arquivoTeste.suffix == ".yaml" or arquivoTeste.suffix == ".yml":
            with open(arquivoTeste, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)  
        data = self.limparEntrada(data)

        # Inicializar variaveis
        flagYamlValido = True
        outputValidacao = [None, None]
        justificativaArquivoInvalido = None
        try:
            # Validar
            jsonschema.validate(instance=data, schema=schema)
            #print("Sucesso")
        except jsonschema.exceptions.ValidationError as e:
            logger.warning(f"Arquivo de teste invalido: {e}")
            print(f"Arquivo {arquivoTeste} invalido")
            #print(e) # temp
            # justificativaArquivoInvalido = ...
            flagYamlValido = False
        
        # Ideia: Formata os argumentos do contexto para comandos usados pelo validator_cli
        def geraArgsValidator(dictContext, secaoInteresse, prefixo):
            strArgsFormatados = ''
            if dictContext.get(secaoInteresse):
                if dictContext[secaoInteresse] != [""] and dictContext[secaoInteresse] != "":
                    strArgsFormatados = f" -{prefixo} " + f" -{prefixo} ".join(dictContext[secaoInteresse])
            return strArgsFormatados

        if flagYamlValido:
            argsArquivoFhir = ''
            context = data.get('context', {})
            argsArquivoFhir += geraArgsValidator(context,'igs', 'ig')
            argsArquivoFhir += geraArgsValidator(context,'profiles', 'profile')
            argsArquivoFhir += geraArgsValidator(context,'resources', 'ig')
            from Classes.gerenciador_validator import GerenciadorValidator
            gerenciadorValidator = GerenciadorValidator(self.pathFut)
            try:
                # Caminho do arquivo a ser validado
                data['caminho_instancia'] = Path(data['caminho_instancia'])
                if not data['caminho_instancia'].is_absolute(): # Para garantir consistencia
                    data['caminho_instancia'] = arquivoTeste.parent / data['caminho_instancia']
                # Iniciar testes em si
                outputValidacao = gerenciadorValidator.validarArquivoFhir(data['caminho_instancia'], args=argsArquivoFhir)
            except subprocess.TimeoutExpired as e:
                pass # Já está registrado no log e não é um erro crítico
            except Exception as e:
                #print(e) # debug
                pass # Já está registrado no log (testar)

        return {
            'caminho_yaml': arquivoTeste,
            'yaml_valido': flagYamlValido,
            'caminho_output': outputValidacao[0] if outputValidacao[0] is not None else None,
            'tempo_execucao': outputValidacao[1],
            'justificativa_arquivo_invalido': justificativaArquivoInvalido,
        }

    # Ideia: Recebe os comandos escritos pelo usuário, verificando os seguintes casos: 
    # 1. Todos os arquivos .yaml da pasta atual (entrada vazia)
    # 2. O arquivo em específico
    # 3. Os arquivos que tenham o mesmo prefixo (uso de '*') 
    def listarArquivosValidar(self, argsEntrada):
        if len(argsEntrada) == 0:
            arquivosYaml = list(Path.cwd().glob('*.yaml'))
            arquivosYaml += list(Path.cwd().glob('*.yml'))
        else:
            arquivosYaml = []
            # Garantir que argsEntrada é uma list
            if isinstance(argsEntrada, str):
                argsEntrada = str(argsEntrada).split()
            # Limpar a string
            argsEntrada = [str(file).replace('"','').replace("'","") for file in argsEntrada]

            # Iterar pela list
            for pathArquivo in argsEntrada:
                arquivoAtual = Path(pathArquivo)

                # Caminho relativo => caminho absoluto
                if not arquivoAtual.is_absolute():
                    arquivoAtual = Path.cwd() / arquivoAtual

                if '*' in arquivoAtual.name:
                    argsEntrada.extend(list(arquivoAtual.parent.glob(f"{str(arquivoAtual.name).split('*')[0]}*.yaml")))

                # Buscar primeiro arquivo YAML
                if (arquivoAtual.suffix == ".yaml" or arquivoAtual.suffix == ".yml") and arquivoAtual.exists():
                    arquivosYaml.append(arquivoAtual)
        
        # Garantir que não há duplicatas
        arquivosYaml = list(set(arquivosYaml))

        return arquivosYaml