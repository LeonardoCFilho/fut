class GerenciadorTestes:
    # Construtor
    def __init__(self):
        pass

    # Ideia: Cria um arquivo .yaml que segue o nosso template para caso de teste
    # P.s.: Referência para o template: https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md#padrões-esperados
    def criaTemplateYaml(self):
        templeteYaml = """test_id:  # (Obrigatório) Identificador único para cada teste (string).
description:  # (Recomendado) Descricao (string).
context: # Definição do contexto de validação.
  igs: # (Recomendado) Lista dos Guias de Implementação (IGs).
    -  # IDs ou url dos IGs (Apenas 1 por linha).
  profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
    -  # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
  resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
    -  # Caminho do arquivo ou o recurso embutido (Apenas 1 por linha).
caminho_instancia:  #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
  status: success  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
  erros: []  #  (Obrigatório/Opcional em success) Lista de erros esperados (lista de string).
  avisos: []  #  (Obrigatório/Opcional em success) Lista de avisos esperados (lista de string).
  informacoes: []  #  (Obrigatório/Opcional em success) Lista de mensagens informativas esperadas (lista de string).
  invariantes:  # (Opcional)"""
        with open("template.yaml", "w") as file:
            file.write(templeteYaml)

    # Ideia: recebe um arquivo de teste e apaga todos arquivos relacionados (arquivo FHIR, ele em si, relatórios criados)
    def deleteCasoTeste(self, caminhoArquivoTeste):
        pass