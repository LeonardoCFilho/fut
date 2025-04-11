# Plano de construção
## Análise de requisitos
[Requisitos definido pelo professor](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md)  

Diagramas:
- [Diagrama de contexto](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContexto.png) ([Código gerador](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContexto.puml))
- [Diagrama de container](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContainer.png) ([Código gerador](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContainer.puml))  

## Arquitetura (grandes componentes da aplicação a ser desenvolvida)
### Padrões esperados  
- Entrada:  
  - Arquivo de teste (YAML) que é armazenado em pastas com o prefixo 'Grupo', cada pasta 'Grupo' agrupará casos de teste de acordo com o context.
    - Estrutura do arquivo de teste (YAML):
    ```yaml
    # Entrada
    test_id: Patient-001  # (Obrigatório) Identificador único para cada teste (string).
    description: Verifica a estrutura básica do arquivo de um Patient. # (Recomendado) Descricao (string).
    context:  # Definição do contexto de validação.
      igs:  # (Recomendado) Lista dos Guias de Implementação (IGs).
        - br-core-r4  # IDs ou url dos IGs (Apenas 1 por linha).
      profiles:  # (Recomendado) Lista de perfis (StructureDefinitions) aplicados
        - br-patient  # IDs ou url dos perfis ou URLs canônicas (Apenas 1 por linha).
      resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
        - valuesets/my-valueset.json  # Caminho do arquivo ou o recurso embutido. (Apenas 1 por linha).
    caminho_instancia: instances/patient_example.json  #  (Obrigatório) Caminho para o arquivo a ser testado (string)
    # Parâmetros para a comparação
    resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
      status: success  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
      erros: []  #  (Obrigatório/Opcional em success) Lista de erros esperados (lista de string).
      avisos: []  #  (Obrigatório/Opcional em success) Lista de avisos esperados (lista de string).
      informacoes: []  #  (Obrigatório/Opcional em success) Lista de mensagens informativas esperadas (lista de string).
      invariantes: # (Opcional)
        - expressao: "OperationOutcome.issues.count() = 0" #(string)
          esperado: True # Resultado esperado (Booleano)
    ```
- Saída
  - JSON ou HTML contendo:
    - Resultados esperado (escrito pelo Oráculo)
    - Resultados inesperado:
      - Diferença imprevista
      - Diferença prevista com categoria (error, warning, etc) errada

### Funcionamento do código  
1. Download do validator_cli  
    - Garantir que a versão mais recente
      - Verificar no git versão mais recente
    - Permitir endereçamento pelo usuário (feito em configurações)

2. Busca do arquivo de teste  
    - Permite arquivos individuais, por prefixo ou todos da pasta atual (entrada vazia)  
      - Se um caminho for recebido:  
        - Procurar arquivo nesse endereço  
        - Se não for encontrado, tentar um arquivo JSON de mesmo nome  
        - Se o arquivo ainda não for encontrado enviar mensagem de erro  
      - Caso contrário buscar todos os arquivos .yaml na pasta atual que seguem os filtros recebidos  

3. Execução dos testes 
    - Se o usuário não inserir dados especifícos todos os arquivos serão testados, caso arquivos individuais (YAML ou JSON) sejam enviados apenas eles serão testados, o mesmo é válido para entrada a partir de prefixo
      - Ler o caso de teste (YAML, JSON)
        - Cada arquivo de teste obrigatoriamente contém uma instância a ser testada, não sendo permitido múltiplas instâncias no mesmo arquivo de teste
      - Validar se o formato é válido (os campos obrigatórios estejam presentes e preenchidos corretamente)
      - Extração de context (IGs, perfis e recursos)
      - Localização da instância (caminho_instancia)
      - Executar validação  
        - Output será salva em uma pasta separada, a qual pode ser temporária dependendo da escolha do usuário (feito em configurações)
        - Criar logs  
    - Observações
      - Implementar timeout
      - Implementar paralelização, de modo que o usuário possa limitar a quantidade de processos simultâneos

4. Comparação de resultados
    - Separar resultados:
      - Resultados dentro do esperado
      - Resultados fora do esperado:
        - Oráculo não previu o resultado
        - Oráculo não previu o resultado na classificação correta (error, warning, etc)

5. Gerar relatório
    - HTML (para legibilidade) ou JSON
    - [Recomendação do professor para o HTML:](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md#5-geração-de-relatórios)
      - Sumário da execução
        - Data e hora da execução
        - Estatísticas de acerto
        - Número dos resultados (total de 'error', 'warning', etc)
        - Tempo de duração
        - Tempo médio por teste
      - Para cada teste
        - Identificação (id, description e context)
        - Instância (formatada)
        - Resultados esperados
        - Resultados obtidos (tabela com diagnósticos, localização e severidade do OperationOutcome)
        - Sumarização das diferenças
        - Referência para o JSON do resultado ou resultado por escrito (opcional)

6. Interface (GUI)
    - Dashboard.
      - Quantidade de testes executados em um dado período (meses, semanas, etc)
      - % de acertos por categoria
      - % de erros por categoria 
      - Media de duração de testes 
    - Gerenciador de arquivos.
      - Lista de testes (YAML) permitindo: Leitura, Edição e Deleção
        - Arquivos recentemente testados e/ou referenciados
      - Opção de criar novo teste (com template)
    - Execução de testes e vizualização de resultados.
      - Tempo estimado de conclusão
      - Diferenças nos resultados esperados e os obtidos
      - Exibição dos detalhes de um teste já executado
      - Permitir a expansão de detalhes de cada teste
      - Filtros
        - Resultado previsto
        - Resultado inesperado
        - Número de erros
    - Configurações.
      - Opção para escolher o validador a ser utilizado
      - Opção para manter o .json resultado do validator_cli
      - Configurar tempo para timeout (em segundos)
      - Configuração de threads (número máximo permitido)
      - Configuração de armazenamento  

### Arquitetura do backend
1. Gerenciador de caso de teste: Responsável por gerenciar os casos de teste, em uma estrutura de diretórios.
2. Executor de testes:
    - Realiza a execução do FHIR Validator.
    - Gerencia a execução paralela dos testes e o controle de tempo limite.
3. Compilador de resultados: 
    - Compara os resultados obtidos pela validação com os resultados esperados definidos nos casos de teste.
    - Geração de relatórios de resultados, utilizando Jinja2 para HTML e Plotly para gráficos interativos (se necessário).
    - Exportação em formatos como HTML e JSON.
4. Data Storage: Caso haja a necessidade de persistir resultados de testes para consultas futuras ou integração com outras ferramentas, pode ser implementado um banco de dados simples ou arquivos como JSON/YAML.
## Tecnologias
- Linguagem: Python.
- Interface gráfica: Streamlit.
- Validador: validator_cli.
- Formato dos casos de teste: YAML.
- Relatório: HTML.
- Tecnologias necessárias: Java, PyYAML, fhir-validator-wrapper, testes, Interpretador python, ...
## Critérios de aceitação (testes, medidas aplicáveis, ...)
### Validação de Estrutura FHIR:
  - A aplicação deve validar se os arquivos FHIR estão no formato JSON ou XML e seguem a estrutura definida pelo padrão FHIR.
  - Critério de Aceitação: A aplicação identifica e reporta erros de estrutura (ex.: campos obrigatórios ausentes, tipos de dados incorretos).
### Suporte a Recursos FHIR:
  - A aplicação deve suportar a validação de todos os recursos FHIR (Patient, Observation, Encounter, etc.).
  - Critério de Aceitação: A aplicação consegue validar a maioria dos recursos FHIR.
### Geração de Dados de Teste:
  - A aplicação deve ser capaz de gerar dados de teste válidos para cada recurso FHIR.
  - Critério de Aceitação: Os dados gerados devem passar na validação de estrutura FHIR.
### Documentação Clara (Caso seja feito uso do YAML):
  - A aplicação deve fornecer documentação detalhada sobre como configurar e usar as funcionalidades.
  - Critério de Aceitação: Um novo usuário consegue configurar e executar um teste unitário em menos de 30 minutos seguindo a documentação.
### Exemplos Práticos:
  - A aplicação deve incluir exemplos de código e casos de uso comuns.
  - Critério de Aceitação: Pelo menos 5 exemplos de testes unitários para diferentes recursos FHIR devem estar disponíveis.
### Validação de Conformidade com FHIR:
  - A aplicação deve garantir que os arquivos FHIR estejam em conformidade com a versão especificada do padrão FHIR R4.
  - Critério de Aceitação: A aplicação deve identificar e reportar incompatibilidades com a versão FHIR especificada.
<!-- ### Proteção de Dados Sensíveis:
  - Se a aplicação lida com dados sensíveis (ex.: dados de pacientes), ela deve seguir as melhores práticas de segurança (ex.: anonimização de dados).
  - Critério de Aceitação: Dados sensíveis em arquivos FHIR são anonimizados durante a geração de dados de teste. -->
## Estratégia para comunicação entre membros da equipe (discord, ...)
Whatsapp
## Papel no projeto:
Amanda: Testes  
Deivison: Frontend  
Ester: Full stack  
Leonardo: Líder  
Mateus: Backend  