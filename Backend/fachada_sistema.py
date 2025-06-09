"""
Interface feita para armazenar funções usadas pelo terminal e pela interface gráfica
"""
from Backend.Classes.servico_execucao_teste import ServicoExecucaoTeste
from Backend.Classes.coordenador_teste import CoordenadorTestes
from Backend.Classes.gestor_caminho import GestorCaminho
from pathlib import Path
import logging 
import sys
logger = logging.getLogger(__name__)


class FachadaSistema:
    # Construtor
    def __init__(self):
        # Se não encontrar o caminho do projeto a função da sys.exit()
        self.coordenador_testes = CoordenadorTestes.get_instance(GestorCaminho(self.acharCaminhoProjeto())) 


    ## Endereçamento
    @staticmethod
    def acharCaminhoProjeto() -> Path:
        """
        Encontra o caminho do diretório do projeto onde o nome do diretório contém 'fut'.

        Returns:
            Path: O caminho do diretório do projeto.

        Raises:
            SystemExit: Se o diretório do projeto não for encontrado dentro do número máximo de iterações definidas.
        """
        maxIteracoes = 10
        numIteracoes = 0
        pathFut = Path(__file__)  # Diretório do arquivo atual
        while "fut" not in pathFut.name:  # Subir um nível se o diretório atual não for 'fut'
            pathFut = pathFut.parent
            numIteracoes +=1 
            if numIteracoes >= maxIteracoes:
                sys.exit("Problemas ao encontrar a pasta do projeto, renomeie-a para 'fut' ou 'fut-main'")
        return pathFut


    def listarArquivosYaml(self, args=None) -> list[Path]:
        """
        Lista arquivos yaml ou na pasta atual ou de acrodo com args

        Args: 
            args: Argumentos de entrada para a criação a lista de testes a serem validados

        Returns:
            Lista com endereços dos arquivos de testes a serem testados (pode ser vazia)
        """
        return ServicoExecucaoTeste(self.acharCaminhoProjeto()).preparar_lista_testes(args)


    ## Configurações
    def obterValorConfiguracao(self, settingsBuscada:str) -> str|None:
        """
        Solicita o valor da configuração procurada

        Args:
            settingsBuscada (str): O nome da configuração buscada

        Returns:
            O valor da configuração OU None(caso de erro)
        """
        return self.coordenador_testes.gestor_caminho.controlador_configuracao.obter_configuracao_segura(settingsBuscada)


    def atualizarValorConfiguracao(self, configuracaoSerAlterada:str, novoValor) -> str:
        """
        Solicita a alteração do valor de uma configuração

        Args:
            configuracaoSerAlterada (str): Nome da configuração a ser alterada
            novoValor: Novo valor desejado para a configuração

        Returns:
            Mensagem de sucesso OU mensagem de erro com justificativa"""
        try:
            self.coordenador_testes.gestor_caminho.controlador_configuracao.alterar_valor_configuracao(configuracaoSerAlterada, str(novoValor))
            return f"Configuração alterada com sucesso!"
        except Exception as e:
            return f"Erro ao alterar a configuração '{configuracaoSerAlterada}': {str(e)}"


    ## Testes
    def iniciarExecucaoTestes(self, args, tipoRelatorio:str='JSON', entregaGradual:bool=False):
        """
        Recebe os args e tenta fazer o teste com eles

        Args:
            args: Os argumentos determinando os testes a serem feitos
            tipoRelatorio (str): Tipo do relatório que será feito (JSON ou HTML)
            entregaGradual (bool): Determina se a entrega será gradual OU súbita

        Returns:
            Gradual: n list do tipo: [dict com informações do teste, porcentagem de testes finalizados]
            OU
            Súbita:  list com todos os valores (Súbito)

        Raises:
            ValueError: Quando a lista de testes criada com o 'args' é vazia
            FileNotFoundError: O ExecutorTeste não conseguiu encontrar o seu schema
            PermissionError: Quando não há permissão para escrever o relatório
            ...
        """
        try: 
            logger.info("Teste de arquivos inicializado")
            if entregaGradual: # Lidar com as entregas no frontend
                for resultado in self.coordenador_testes.executar_testes_completo(args, tipoRelatorio, entregaGradual):
                    yield resultado # é uma list, contém: dict com os dados do teste, % de testes finalizados
            else:
                list(self.coordenador_testes.executar_testes_completo(args, tipoRelatorio, entregaGradual))

        except Exception as e:
            raise(e)


    ## Arquivos de teste
    def gerarArquivoTeste(self, dictInformacoesTeste:dict = None, caminho_arquivo = None):
        """
        Cria um arquivo .yaml (preenchido ou não) que segue o nosso template para caso de teste
        Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados

        Args:
            dictInformacoesTeste (dict): dict com os dados a serem inseridos no arquivo (opcional)
            caminho_arquivo: Caminho onde o arquivo será criado/escrito (opcional)

        Raises:
            PermissionError: Programa não tem permissão para a criação/escrita do arquivo
            ...
        """
        if not caminho_arquivo:  # Se o nome não é especificado => template
            caminho_arquivo = "template.yaml"
        logger.info(f"Arquivo de teste criado em {caminho_arquivo}")
        if not dictInformacoesTeste:  # Sem informações especificadas => template
            logger.info("Template de um arquivo de teste criado") 
            dictInformacoesTeste = {
                "test_id": '',
                "description": '',
                "igs": '',
                "profiles": '',
                "resources": '',
                "caminho_instancia": '',
                "status": '',
                "error": '',
                "warning": '',
                "fatal": '',
                "information": '',
                "invariantes": '',
            }

            templateYaml = f"""test_id: {dictInformacoesTeste.get('test_id', '')} # (Obrigatório) Identificador único para cada teste (string).
    description: {dictInformacoesTeste.get('description', '')} # (Recomendado) Descricao (string).
    context: # Definição do contexto de validação.
        igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
            - {dictInformacoesTeste.get('igs', '')} # IDs ou url dos IGs (Apenas 1 por linha).
        profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
            - {dictInformacoesTeste.get('profiles', '')} # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
        resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
            - {dictInformacoesTeste.get('resources', '')} # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
    caminho_instancia: {dictInformacoesTeste.get('caminho_instancia', '')} #  (Obrigatório) Caminho para o arquivo a ser testado (string)
    # Parâmetros para a comparação
    resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
        status: {dictInformacoesTeste.get('status', '')}  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
        error: [{dictInformacoesTeste.get('error', '')}]  #  (Obrigatório) Lista de erros esperados (lista de string).
        warning: [{dictInformacoesTeste.get('warning', '')}]  #  (Obrigatório) Lista de avisos esperados (lista de string).
        fatal: [{dictInformacoesTeste.get('fatal', '')}] #  #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
        information: [{dictInformacoesTeste.get('information', '')}]  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
        invariantes: {dictInformacoesTeste.get('invariantes', '')} # (Opcional)"""
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as file:  # Se caminho_arquivo já existia ele é sobrescrito
                file.write(templateYaml)
        except PermissionError as e:
            logger.error("Programa não tem permissão para criar o arquivo de teste requisitado")
            raise e
        except Exception as e:
            raise e  # improvável


    def _returnCodigoANSI(self, codigoDesejado: str) -> str:
        """
        Retornar o valor ANSI para um determinado codigo
        
        Args: 
            codigoDesejado (str): O nome do codigo desejado
            
        Returns:
            str com o valor solicitado ou uma string vazia (caso de erro)
        """
        from colorama import Fore, Style
        dictANSI = {
            "textoNegrito": Style.BRIGHT,
            "textoSublinhado": "\033[4m",
            "textoHyperlink": "\033[4;34m",
            'vermelho': Fore.RED,
            'azul': Fore.BLUE,
            'ciano': Fore.CYAN,
            'magenta': Fore.MAGENTA,
            "fimTextoColorido": Style.RESET_ALL,
        }
        return dictANSI.get(codigoDesejado, '')


    # TODO implementar gettext ou similar (json?)
    ## Dialogos
    def obterDialogo(self, dialogoDesejado: str) -> str:
        """
        Armazena e retorna dialogos estilizados a serem usados

        Args:
            dialogoDesejado (str): Chave do dialogo a ser retornado

        Returns:
            str do dialogo ou None(caso de erro)
        """
        # Criando o dict com os dialogos
        dialogos = {}
        dialogos['help'] = f"""\n\n{self._returnCodigoANSI("textoNegrito")}Ajuda:{self._returnCodigoANSI("fimTextoColorido")}
    Sistema de teste unitário para arquivos FHIR (versão 4.0.1)

    {self._returnCodigoANSI("textoSublinhado")}Leitura de casos de teste{self._returnCodigoANSI("fimTextoColorido")}:
    Sem argumentos, o comando fut executa todos os testes definidos por arquivos .yaml no diretório corrente.
    Indicando arquivos específicos como fut teste/x.yml y.yml, ele executa o teste do arquivo em teste/x.yml e o teste do arquivo y.yml no diretório atual.
    Usando curingas, por exemplo, fut patient-*.yml, ele executa todos os testes cujos nomes iniciam com patient- e terminam com .yml.

    {self._returnCodigoANSI("textoSublinhado")}Comandos{self._returnCodigoANSI("fimTextoColorido")}:
    {self._returnCodigoANSI("ciano")}--help       {self._returnCodigoANSI("fimTextoColorido")}\t\tAbri o menu atual e exibe mais informações sobre o programa
    {self._returnCodigoANSI("ciano")}gui          {self._returnCodigoANSI("fimTextoColorido")}\t\tInicializa a interface gráfica (Ainda não foi implementada)
    {self._returnCodigoANSI("ciano")}template     {self._returnCodigoANSI("fimTextoColorido")}\t\tGera um arquivo .yaml que segue o template de arquivos de teste
    {self._returnCodigoANSI("ciano")}configuracoes{self._returnCodigoANSI("fimTextoColorido")}\t\tPermite a edição de configurações globais do sistema

    Mais detalhes em: {self._returnCodigoANSI("textoHyperlink")}https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md{self._returnCodigoANSI("fimTextoColorido")}"""

        dialogos['configuracoes'] = f"""As configurações disponíveis para o Sistema de teste unitário para arquivos FHIR são as seguintes:

    1. {self._returnCodigoANSI("textoSublinhado")}[hardware]{self._returnCodigoANSI("fimTextoColorido")}
     - {self._returnCodigoANSI("ciano")}timeout (int):{self._returnCodigoANSI("fimTextoColorido")} Define o tempo limite, em segundos, para a execução de cada teste. Exemplo de valor: `600` (10 minutos).
     - {self._returnCodigoANSI("ciano")}max_threads (int):{self._returnCodigoANSI("fimTextoColorido")} Especifica o número máximo de threads a serem usadas para executar os testes paralelamente. Exemplo de valor: `4`.
     - {self._returnCodigoANSI("ciano")}requests_timeout (int):{self._returnCodigoANSI("fimTextoColorido")} Define o tempo limite, em segundos, que o programa aguarda para downloads finalizar. Exemplo de valor: `600` (10 minutos).

    2. {self._returnCodigoANSI("textoSublinhado")}[enderecamento]{self._returnCodigoANSI("fimTextoColorido")}
     - {self._returnCodigoANSI("ciano")}caminho_validator (str):{self._returnCodigoANSI("fimTextoColorido")} Caminho personalizado para o arquivo `validator_cli.jar`, caso seja necessário sobrescrever o caminho padrão. Exemplo de valor: `~/Downloads/validator_cli.jar`.
     - {self._returnCodigoANSI("ciano")}armazenar_saida_validator (bool):{self._returnCodigoANSI("fimTextoColorido")} Indica se a saída do validador deve ser armazenada. Valores aceitos: `True` (armazenar saída) ou `False` (não armazenar). Exemplo de valor: `False`.

    Essas configurações podem ser editadas com o comando `fut configuracoes <nome da configuração> <novo valor>`, permitindo ajustar o comportamento global do sistema conforme suas necessidades. Certifique-se de que os valores correspondam aos tipos esperados para garantir a atualização da configuração."""   

        return dialogos.get(dialogoDesejado, '') 