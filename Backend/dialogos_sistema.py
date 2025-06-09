"""
Módulo responsável pelos diálogos e mensagens do sistema
"""
from colorama import Fore, Style


class DialogosSistema:
    """Classe responsável por gerenciar os diálogos do sistema"""
    
    @staticmethod
    def get_ansi_code(codigo_desejado: str) -> str:
        """
        Retorna o valor ANSI para um determinado código
        
        Args: 
            codigo_desejado (str): O nome do código desejado
            
        Returns:
            str com o valor solicitado ou uma string vazia (caso de erro)
        """
        dict_ansi = {
            "textoNegrito": Style.BRIGHT,
            "textoSublinhado": "\033[4m",
            "textoHyperlink": "\033[4;34m",
            'vermelho': Fore.RED,
            'azul': Fore.BLUE,
            'ciano': Fore.CYAN,
            'magenta': Fore.MAGENTA,
            "fimTextoColorido": Style.RESET_ALL,
        }
        return dict_ansi.get(codigo_desejado, '')


    @classmethod
    def obter_dialogo(cls, dialogo_desejado: str) -> str:
        """
        Retorna diálogos estilizados para uso no sistema

        Args:
            dialogo_desejado (str): Chave do diálogo a ser retornado

        Returns:
            str do diálogo ou string vazia se não encontrado
        """
        dialogos = {
            'help': cls._get_help_dialog(),
            'configuracoes': cls._get_config_dialog()
        }
        return dialogos.get(dialogo_desejado, '')


    @classmethod
    def _get_help_dialog(cls) -> str:
        """Retorna o diálogo de ajuda"""
        return f"""\n\n{cls.get_ansi_code("textoNegrito")}Ajuda:{cls.get_ansi_code("fimTextoColorido")}
Sistema de teste unitário para arquivos FHIR (versão 4.0.1)

{cls.get_ansi_code("textoSublinhado")}Leitura de casos de teste{cls.get_ansi_code("fimTextoColorido")}:
Sem argumentos, o comando fut executa todos os testes definidos por arquivos .yaml no diretório corrente.
Indicando arquivos específicos como fut teste/x.yml y.yml, ele executa o teste do arquivo em teste/x.yml e o teste do arquivo y.yml no diretório atual.
Usando curingas, por exemplo, fut patient-*.yml, ele executa todos os testes cujos nomes iniciam com patient- e terminam com .yml.

{cls.get_ansi_code("textoSublinhado")}Comandos{cls.get_ansi_code("fimTextoColorido")}:
{cls.get_ansi_code("ciano")}--help       {cls.get_ansi_code("fimTextoColorido")}\t\tAbri o menu atual e exibe mais informações sobre o programa
{cls.get_ansi_code("ciano")}gui          {cls.get_ansi_code("fimTextoColorido")}\t\tInicializa a interface gráfica (Ainda não foi implementada)
{cls.get_ansi_code("ciano")}template     {cls.get_ansi_code("fimTextoColorido")}\t\tGera um arquivo .yaml que segue o template de arquivos de teste
{cls.get_ansi_code("ciano")}configuracoes{cls.get_ansi_code("fimTextoColorido")}\t\tPermite a edição de configurações globais do sistema

Mais detalhes em: {cls.get_ansi_code("textoHyperlink")}https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md{cls.get_ansi_code("fimTextoColorido")}"""

    @classmethod
    def _get_config_dialog(cls) -> str:
        """Retorna o diálogo de configurações"""
        return f"""As configurações disponíveis para o Sistema de teste unitário para arquivos FHIR são as seguintes:

1. {cls.get_ansi_code("textoSublinhado")}[hardware]{cls.get_ansi_code("fimTextoColorido")}
 - {cls.get_ansi_code("ciano")}timeout (int):{cls.get_ansi_code("fimTextoColorido")} Define o tempo limite, em segundos, para a execução de cada teste. Exemplo de valor: `600` (10 minutos).
 - {cls.get_ansi_code("ciano")}max_threads (int):{cls.get_ansi_code("fimTextoColorido")} Especifica o número máximo de threads a serem usadas para executar os testes paralelamente. Exemplo de valor: `4`.
 - {cls.get_ansi_code("ciano")}requests_timeout (int):{cls.get_ansi_code("fimTextoColorido")} Define o tempo limite, em segundos, que o programa aguarda para downloads finalizar. Exemplo de valor: `600` (10 minutos).

2. {cls.get_ansi_code("textoSublinhado")}[enderecamento]{cls.get_ansi_code("fimTextoColorido")}
 - {cls.get_ansi_code("ciano")}caminho_validator (str):{cls.get_ansi_code("fimTextoColorido")} Caminho personalizado para o arquivo `validator_cli.jar`, caso seja necessário sobrescrever o caminho padrão. Exemplo de valor: `~/Downloads/validator_cli.jar`.
 - {cls.get_ansi_code("ciano")}armazenar_saida_validator (bool):{cls.get_ansi_code("fimTextoColorido")} Indica se a saída do validador deve ser armazenada. Valores aceitos: `True` (armazenar saída) ou `False` (não armazenar). Exemplo de valor: `False`.

Essas configurações podem ser editadas com o comando `fut configuracoes <nome da configuração> <novo valor>`, permitindo ajustar o comportamento global do sistema conforme suas necessidades. Certifique-se de que os valores correspondam aos tipos esperados para garantir a atualização da configuração."""