class GerenciadorTestes:
    # Construtor
    def __init__(self):
        pass

    # Ideia: Cria um arquivo .yaml que segue o nosso template para caso de teste
    # P.s.: Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
    def criaTemplateYaml(self):
        # 
        templeteYaml = """test_id: ""  # (Obrigatório) Identificador único para cada teste (string).
description: ""  # (Recomendado) Descricao (string).
context:  # Definição do contexto de validação.
  igs: []  # (Recomendado) Lista dos Guias de Implementação (IGs).
  profiles: []  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados.
  resources: []  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
caminho_instancia: ""  # (Obrigatório) Caminho para o arquivo a ser testado.
resultados_esperados:  # (Obrigatório) Define os resultados esperados de validação.
  status: ""  # (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
  erros: []  # (Obrigatório) Lista de erros esperados (lista vazia indica sucesso).
  avisos: []  # (Obrigatório) Lista de avisos esperados.
  informacoes: []  # (Obrigatório) Lista de mensagens informativas esperadas.
  invariantes: []  # (Opcional) Claúsulas adicionais a serem verificadas."""
        with open("template.yaml", "w") as file:
            file.write(templeteYaml)

    # Ideia: recebe um arquivo de teste e apaga totemplate: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperadosdos arquivos relacionador (arquivo FHIR, ele em si, relatórios criados)
    def deleteCasoTeste(self, caminhoArquivoTeste):
        pass