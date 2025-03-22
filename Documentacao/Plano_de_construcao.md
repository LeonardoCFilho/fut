# Plano de construção
## Análise de requisitos
[Requisitos definido pelo professor](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md)

<!-- Análise: Os requisitos são claros desde que você tenha alguma familiaridade com testes unitários. Porém, a falta de casos de testes e saídas esperadas dificulta o processo de compreensão e desenvolvimento do código e, como se trata de uma discoiplina de cnstrução, isso é problemático. -->
## Arquitetura (grandes componentes da aplicação a ser desenvolvida)
### Frontend:
   - Interface Gráfica (GUI): Utilizar do Streamlit.
   - Relatórios: Geração de relatórios em formato HTML com a ajuda de templates como Jinja2, que podem ser visualizados na interface ou exportados.
### Backend:
- Gerenciador de caso de teste:  Responsável por gerenciar os casos de teste, em uma estrutura de diretórios.
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
