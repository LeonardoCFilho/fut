# Plano de construção
## Análise de requisitos
[Requisitos definido pelo professor](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md)  

Diagramas:
- [Diagrama de contexto](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContexto.png) ([Código gerador](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContexto.puml))
- [Diagrama de container](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContainer.png) ([Código gerador](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContainer.puml))  
<!-- Análise: Os requisitos são claros desde que você tenha alguma familiaridade com testes unitários. Porém, a falta de casos de testes e saídas esperadas dificulta o processo de compreensão e desenvolvimento do código e, como se trata de uma disciplina de construção, isso é problemático. -->
### Plano do framework
#### Padrões esperados  
- Entrada:  
  - Arquivo de teste (YAML) que é armazenado em pastas com o prefixo 'Grupo', cada pasta 'Grupo' agrupará casos de teste de acordo com o context.
    - Estrutura do arquivo de teste (YAML):
    ```yaml
    # Entrada
    test_id: Patient-001  # Identificador único para cada teste (string).
    description: Verifica a estrutura básica do arquivo de um Patient. # Descricao (string).
    context:  # Definição do contexto de validação.
      igs:  # Lista dos Guias de Implementação (IGs).
        - br-core-r4  # IDs dos IGs (lista de strings).
      profiles:  # Lista de perfis (StructureDefinitions) aplicados
        - br-patient  # IDs dos perfis ou URLs canônicas (lista de strings).
      resources:  # (Opcional) Recursos FHIR adicionais (ValueSet, CodeSystem, etc.).
        - valuesets/my-valueset.json  # Caminho do arquivo ou o recurso embutido.
    caminho_instancia: instances/patient_example.json  # Caminho para o arquivo a ser testado
    # Parâmetros para a comparação
    resultados_esperados:  # Define os resultados esperados de validação.
      status: success  # Nível geral esperado ('success', 'error', 'warning', 'information').
      erros: []  # Lista de erros esperados (lista vazia indica sucesso).
      avisos: []  # Lista de avisos esperados.
      informacoes: []  # Lista de mensagens informativas esperadas.
      invariantes: # Opcional.
        - expressao: "OperationOutcome.issues.count() = 0"
          esperado: True # Opcional, padrão: True.
    ```
- Saída
  - JSON contendo:
    - Resultados esperado (escrito pelo Oráculo)
    - Resultados inesperado:
      - Diferença imprevista
      - Diferença prevista com categoria (error, warning, etc) errada

#### Funcionamento do código  
1. Download do validator_cli  
    - Garantir que a versão mais recente
      - Crawler para a versão mais recente 
    - Permitir endereçamento pelo usuário  

2. Busca do arquivo de teste  
    - Receber um caminho absoluto ou nome
      - Se um caminho absoluto for recebido:
        - Procurar arquivo nesse endereço
        - Se não for encontrado, tentar um arquivo JSON de mesmo nome
      - Se não: Buscar na pasta 'Testes'
      - Se o arquivo ainda não for encontrado enviar mensagem de erro

3. Execução dos testes 
    - Se o usuário enviar uma pasta (prefixo Grupo) testar todos os arquivos, caso apenas um arquivo (YAML ou JSON) seja enviado apenas ele será testado
      - Ler o caso de teste (YAML, JSON)
      - Validar se o formato é válido (os campos obrigatórios estejam presentes e preenchidos corretamente)
      - Extração de context (IGs, perfis e recursos)
      - Localização da instância (caminho_instancia)
      - Executar validação 
      - Criar logs e comparar os resultados
    - Observacoes
      - Implementar timeout
      - Implementar paralelização, de modo que o usuário possa limitar a quantidade de processos simultâneos

4. Comparação de resultados
    - Separar resultados:
      - Resultados dentro do esperado
      - Resultados fora do esperado:
        - Oráculo não previu o resultado
        - Oráculo não previu o resultado na classificação correta (error, warning, etc)

5. Gerar relatório
    - HTML (para legibilidade) e JSON
    - [Recomendação do professor para o HTML:](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md#5-report-generation)
      - Sumário da execução
        - Estatísticas de acerto
        - Número dos resultados (total de 'error', 'warning', etc)
        - Tempo de duração
        - Tempo médio por teste
        - Lista por pasta (Grupo) com os resultados
          - Cada pasta:
            a. Nome
            b. Estatisticas
            c. Referência para o JSON do resultado 
      - Para cada teste
        - Identificação (id, context, etc)
        - Instância formatada
        - Resultados esperados
        - Resultados obtidos
        - Sumarização das diferenças
        - Referência para o JSON do resultado ou resultado por escrito (opcional)

6. Interface (GUI)
    - Dashboard.
      - Quantidade de testes executados em um dado período (meses, semanas, etc)
      - % de acertos por categoria
      - % de erros por categoria 
      - Media de duração de testes 
    - Gerenciador de blocos (arquivos).
      - Arquivos recentemente testados
      - Arquivos salvos/referenciados
    - Gerenciador de casos de teste (CRUD).
      - Lista de testes (YAML) permitindo: Leitura, Edição e Deleção
      - Opção de criar novo teste (com template)
    - Execução de testes (seleção, progresso, resultado em tempo real).
      - Tempo estimado de conclusão
      - Diferenças nos resultados esperados e os obtidos
      - Exibição dos detalhes de um teste já executado
    - Vizualização dos resultados (Navegação, filtros, comparação).
      - Permitir a expansão de detalhes de cada teste
      - Filtros
        - Resultado previsto
        - Resultado inesperado
        - Número de erros
    - Configurações.
      - Opção para escolher o validador a ser utilizado
      - Configurar tempo para timeout
      - Configuração de threads
      - Configuração de armazenamento  

## Arquitetura (grandes componentes da aplicação a ser desenvolvida)
### Frontend:
   - Interface Gráfica (GUI): Utilizar do Streamlit.
   - Relatórios: Geração de relatórios em formato HTML com a ajuda de templates como Jinja2, que podem ser visualizados na interface ou exportados.
### Backend:
- Gerenciador de caso de teste: Responsável por gerenciar os casos de teste, em uma estrutura de diretórios.
- Executor de testes:
  - Realiza a execução do FHIR Validator.
  - Gerencia a execução paralela dos testes e o controle de tempo limite.
- Compilador de resultados: 
  - Compara os resultados obtidos pela validação com os resultados esperados definidos nos casos de teste.
  - Geração de relatórios de resultados, utilizando Jinja2 para HTML e Plotly para gráficos interativos (se necessário).
  - Exportação em formatos como HTML e JSON.
- Data Storage: Caso haja a necessidade de persistir resultados de testes para consultas futuras ou integração com outras ferramentas, pode ser implementado um banco de dados simples ou arquivos como JSON/YAML.
<!-- ### 3. Componentes Modulares:
   - Validator Interface: Camada de abstração entre o código e o validador FHIR, para facilitar a troca do validador ou a implementação de novas versões.
   - Context Manager: Responsável por organizar e fornecer o contexto para os testes, como IGs (Implementation Guides), perfis (StructureDefinitions) e recursos adicionais (ValueSets, CodeSystems).
   - Error Handling e Logging: Implementar uma estratégia robusta para tratar erros e registrar eventos importantes para troubleshooting, usando bibliotecas como logging.
   - Parallelization: Suporte a execução paralela de testes para otimizar o tempo de execução, com controle cuidadoso do acesso a arquivos e gestão de concorrência. -->
<!-- ### Arquitetura em Camadas:
   - Camada de Apresentação (Frontend): Interface do usuário.
   - Camada de Lógica de Negócio: Responsável por coordenar a execução dos testes, comparar resultados e gerar relatórios.
   - Camada de Dados: Manipulação dos dados de entrada, resultados e persistência de dados (se necessário). -->
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
<!-- ### Suporte a Grandes Volumes de Dados:
  - A aplicação deve ser capaz de lidar com grandes volumes de dados FHIR (ex.: validação de lote de recursos).
  - Critério de Aceitação: A aplicação consegue validar um lote de 1000 recursos FHIR em menos de 10 segundos.  -->
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