from pathlib import Path
import yaml
import json
import jsonschema
from Backend.Classes.inicializador_sistema import InicializadorSistema
import logging
logger = logging.getLogger(__name__)

class ExecutorTestes(InicializadorSistema):
    # Construtor
    def __init__(self, pathFut):
        super().__init__(pathFut)
    
    
    def limparConteudoEntrada(self, data:dict):
        """
        Padronizar as informações recebidas do arquivo de teste

        Args:
            data (dict): Entrada a ser tratada
        
        Returns:
            data (dict): Entrada tratada
        """
        if isinstance(data, dict):
            return {key: self.limparConteudoEntrada(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.limparConteudoEntrada(item) if item is not None else "" for item in data]
        return data

    
    def validarArquivoTeste(self, arquivoTeste: Path) -> dict:
        """
        Valida um arquivo YAML usando o schema JSON e, se válido, chama a validação FHIR.

        Args:
            arquivoTeste (Path): Caminho do arquivo de teste .yaml 
        
        Returns:
            Um dict com os dados do teste
        """
        # Schema para validar o arquivo de teste
        schemaPath = self.pathFut / "Backend" / "schema.json"
        with open(schemaPath, 'r', encoding="utf-8") as jsonSchemaFile:
            schema = json.load(jsonSchemaFile)
        # Arquivo de teste
        if arquivoTeste.suffix == ".yaml" or arquivoTeste.suffix == ".yml": # por segurança
            with open(arquivoTeste, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)  

        # Limpar a entrada
        data = self.limparConteudoEntrada(data)

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
                if dictContext[secaoInteresse] not in [None, "", [""]]:
                    strArgsFormatados = f" -{prefixo} " + f" -{prefixo} ".join(dictContext[secaoInteresse])
            return strArgsFormatados
        
        # Antes de tentar validar o arquivo verificar se existe:
        # Preparar arquivo
        data['caminho_instancia'] = Path(data['caminho_instancia'])
        if not data['caminho_instancia'].is_absolute(): # Para garantir consistencia
            data['caminho_instancia'] = arquivoTeste.parent / data['caminho_instancia']
        # Tentar mais duas maneiras de achar o arquivo
        if not data['caminho_instancia'].exists(): # Arquivo escrito no teste não existe
            if arquivoTeste.with_suffix('.json').exists(): # Ver se versão com mesmo nome (mas .json) existe
                data['caminho_instancia'] = arquivoTeste.with_suffix('.json')
            elif Path(arquivoTeste.parent / f"{data['test_id']}.json").exists(): # Ver se existe pelo id
                data['caminho_instancia'] = Path(arquivoTeste.parent / f"{data['test_id']}.json")
            else: # Simplesmente não existe
                flagYamlValido = False
                justificativaArquivoInvalido = "Não foi possível encontrar o arquivo a ser testado"

        if flagYamlValido:
            argsArquivoFhir = ''
            context = data.get('context', {})
            argsArquivoFhir += geraArgsValidator(context,'igs', 'ig')
            argsArquivoFhir += geraArgsValidator(context,'profiles', 'profile')
            argsArquivoFhir += geraArgsValidator(context,'resources', 'ig')
            from Backend.Classes.gerenciador_validator import GerenciadorValidator
            gerenciadorValidator = GerenciadorValidator(self.pathFut)
            try:
                # Iniciar testes
                outputValidacao = gerenciadorValidator.validarArquivoFhir(data['caminho_instancia'], args=argsArquivoFhir)
            except Exception as e:
                # print(e) # debug
                # raise(e)
                pass # Já está registrado no log 

        return {
            'caminho_yaml': arquivoTeste,
            'yaml_valido': flagYamlValido,
            'caminho_output': outputValidacao[0] if outputValidacao[0] is not None else None,
            'tempo_execucao': outputValidacao[1],
            'justificativa_arquivo_invalido': justificativaArquivoInvalido,
        }

    
    def gerarListaArquivosTeste(self, argsEntrada) -> list:
        """
        Recebe os comandos escritos pelo usuário, verificando os seguintes casos: 
        # 1. Todos os arquivos .yaml da pasta atual (entrada vazia)
        # 2. O arquivo em específico
        # 3. Os arquivos que tenham o mesmo prefixo (uso de '*') 

        Args: 
            argsEntrada: Entrada para determinar a lista de arquivos de teste
        
        Returns:
            list de paths para cada yaml encontrado OU list vazia
        """
        arquivosYaml = []
        # Ler todos da pasta atual
        if (isinstance(argsEntrada, list) or isinstance(argsEntrada, str)) and len(argsEntrada) == 0:
            arquivosYaml = list(Path.cwd().glob('*.yaml')) + list(Path.cwd().glob('*.yml'))
        # Arquivos especificados
        else:
            # Garantir que argsEntrada é uma list
            if isinstance(argsEntrada, str):
                argsEntrada = str(argsEntrada).split()
            elif isinstance(argsEntrada, (tuple, set)): # Conversão direta
                argsEntrada = list(argsEntrada) 
            elif not isinstance(argsEntrada, list): # Colocar em uma lista
                argsEntrada = [argsEntrada]  
            # Limpar a string
            argsEntrada = [str(file).replace('"','').replace("'","") for file in argsEntrada]

            # Iterar pela list
            for pathArquivo in argsEntrada:
                arquivoAtual = Path(pathArquivo)

                # Caminho relativo => caminho absoluto
                if not arquivoAtual.is_absolute():
                    arquivoAtual = Path.cwd() / arquivoAtual

                if '*' in arquivoAtual.name:
                    pesquisaPrefixo = str(arquivoAtual.name).split('*')[0]
                    argsEntrada.extend(list(arquivoAtual.parent.glob(f"{pesquisaPrefixo}*.yaml")))

                # Verificar se o arquivo tem a extensão .yaml ou .yml e existe
                if (arquivoAtual.suffix in [".yaml", ".yml"]) and arquivoAtual.exists():
                    arquivosYaml.append(arquivoAtual)
        
        # Garantir que não há duplicatas
        arquivosYaml = list(set(arquivosYaml))
        # Por segurança, remover qualquer arquivo inexistente
        arquivosYaml = [arquivo for arquivo in arquivosYaml if arquivo.exists()]

        return arquivosYaml