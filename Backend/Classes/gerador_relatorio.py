class GeradorRelatorios:
    # Construtor
    def __init__(self):
        pass

    # Ideia: Função recebe o que o oráculo esperava e o que o validator_cli detectou, comparando os e retornando uma lista com semelhanças e diferenças
    def compararResultados(saidaEsperada, saidaRecebida):
        pass

    # Ideia: Função gera partes do relatório que seriam usadas tanto no .json quanto no .html
    def gerarRelatorio(arquivoTeste, saidaValidador):
        pass

    # Ideia: Função recebe os dados de compararResultados() e cria um relatório .json do caso de teste
    def gerarRelatorioJson(arquivoTeste, saidaValidador):
        import json
        pass

    # Ideia: Função recebe os dados de compararResultados() e cria um relatório .html do caso de teste
    def gerarRelatorioJson(arquivoTeste, saidaValidador):
        import jinja2
        pass