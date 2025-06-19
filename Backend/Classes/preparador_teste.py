from Backend.Classes.teste import Teste
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PreparadorTeste:
    # Construtor
    def __init__(self):
        pass


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
                argumentos_formatados = f"-{prefixo} " + f" -{prefixo} ".join(dict_contexto[secao_interesse])
        return argumentos_formatados


    def _encontrar_arquivo_instancia(self, teste: Teste, caminho_teste: Path) -> Teste:
        """
        Localiza o arquivo de instância necessário para o teste.

        Args:
            teste (Teste): Objeto contendo os dados do teste.
            caminho_teste (Path): Caminho do arquivo de teste principal.

        Returns:
            Teste: Objeto `teste`, com o estado atualizado caso o arquivo não seja encontrado.
        """
        caminho_instancia = Path(teste.conteudo['caminho_instancia'])

        # Resolver caminho relativo
        if not caminho_instancia.is_absolute():
            caminho_instancia = caminho_teste.parent / caminho_instancia

        # Verificar se o arquivo existe no caminho original
        if caminho_instancia.exists():
            teste.conteudo['caminho_instancia'] = caminho_instancia
            return teste

        # Verificar se existe um arquivo JSON com o mesmo nome do teste
        caminho_json = caminho_teste.with_suffix('.json')
        if caminho_json.exists():
            teste.conteudo['caminho_instancia'] = caminho_json
            return teste

        # Verificar por nome baseado no test_id
        test_id = teste.conteudo.get('test_id')
        caminho_por_id = caminho_teste.parent / f"{test_id}.json"
        if caminho_por_id.exists():
                teste.conteudo['caminho_instancia'] = caminho_por_id
                return teste

        # Se nenhum dos arquivos foi encontrado, marcar como inválido
        teste.estado_atual = "Invalido"
        teste.justificativa_teste_invalido = "Não foi possível encontrar o arquivo de instância necessário para o teste."
        return teste


    def _criar_teste(self, dados: dict, path_arquivo_teste: Path) -> Teste:
        teste_cru = Teste(path_arquivo_teste, dados)
        teste = self._encontrar_arquivo_instancia(teste_cru, path_arquivo_teste)
        if len(teste.justificativa_teste_invalido) == 0:
            teste.argumentos_validator += self._gerar_argumentos_validator(teste.conteudo['context'], 'igs', 'ig')
            teste.argumentos_validator += self._gerar_argumentos_validator(teste.conteudo['context'], 'profiles', 'profile')
            teste.argumentos_validator += self._gerar_argumentos_validator(teste.conteudo['context'], 'resources', 'ig')
        
        return teste


    def processar_testes(self, dados: dict, arquivo_origem: Path, path_schema: Path,  justificativa_teste_invalido: str = None) -> list[Teste]:
        """
        Processa um dicionário que pode ser uma suite ou um teste único,
        retornando uma lista de objetos Teste.

        Args:
            dados (dict): Dicionário com dados da suite ou teste único
            arquivo_origem (Path): Caminho do arquivo de origem

        Returns:
            list[Teste]: Lista com um ou mais objetos Teste
        """

        # Criar teste já errado
        if justificativa_teste_invalido:
            temp_teste = Teste(arquivo_origem, dados, "Invalido", justificativa_teste_invalido)
            return [temp_teste]

        # Não é => Fazer validação com o schema
        teste_cru = Teste(arquivo_origem, dados)
        teste_cru.validar_schema(path_schema)
        
        # Verificar se é uma suite
        if teste_cru.estado_atual == "Suite":
            testes = []
            # É uma suite - processar cada teste
            for teste_data in dados['tests']:
                temp_teste = self._criar_teste(teste_data, arquivo_origem)
                # Tornar enderecos unicos
                temp_teste.path_arquivo_teste = Path(str(temp_teste.path_arquivo_teste) + str(len(testes)+1))
                testes.append(temp_teste)
            return testes
        else:
            # É um teste único
            return [self._criar_teste(dados, arquivo_origem)]