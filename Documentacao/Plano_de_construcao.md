# Plano de Construção

## 1. Introdução

### 1.1 Visão Geral do Projeto
O projeto consiste na construção de uma aplicação para a validação de arquivos FHIR. O sistema receberá casos de teste organizados em arquivos YAML, executará a validação das instâncias FHIR (em JSON ou XML) e gerará relatórios detalhados (em HTML e/ou JSON). A aplicação ainda oferecerá uma interface gráfica, permitindo acompanhar a execução dos testes, visualizar estatísticas e gerenciar casos de teste.

### 1.2 Escopo do Projeto
O sistema abordará as seguintes funcionalidades:  
- **Validação dos Arquivos FHIR:** Verificação da estrutura e conformidade dos dados com o padrão FHIR R4.  
- **Execução de Testes:** Realização dos testes definidos em arquivos YAML, com comparação dos resultados obtidos em relação aos resultados esperados.  
- **Geração de Relatórios:** Produção de relatórios detalhados que sumarizam os testes executados, destacando divergências em valor ou na classificação.  
- **Execução Paralela e Controle de Timeout:** Execução eficiente dos testes utilizando paralelização e mecanismos de timeout para evitar travamentos.  


## 2. Requisitos

### 2.1 Requisitos Funcionais
- **Validação de Arquivos FHIR:**  
  O sistema deverá validar arquivos FHIR em formato JSON ou XML, assegurando a conformidade com o padrão FHIR R4.
  
- **Geração de Relatórios:**  
  Após a execução dos testes, o software gerará relatórios detalhados em um dos seguintes formatos:
  - **JSON:** Estrutura dos resultados, diferenciando resultados esperados e obtidos.
  - **HTML:** A qual permite uma navegação fácil e sucinta.

- **Execução Paralela e Controle de Timeout:**  
  Implementação de execução paralela dos testes, com configuração de número máximo de threads e controle de timeout para evitar travamentos.

- **Atualização do Validador:**  
  Download e verificação da versão mais recente do `validator_cli`, permitindo personalizações (como endereçamento e parâmetros de execução).

### 2.2 Requisitos Não Funcionais
- **Interface Gráfica:**  
  A aplicação deverá oferecer uma interface gráfica intuitiva, desenvolvida com Streamlit, que permita a execução dos testes, monitoramento dos resultados e gerenciamento dos casos de teste.

- **Desempenho:**  
  O sistema deverá executar os testes de maneira rápida e eficiente, otimizando recursos através da paralelização e de um adequado gerenciamento de timeouts.

### 2.3 Restrições e Limitações
- **Validador:**  
  Apenas o `validator_cli` será utilizado para a validação dos arquivos FHIR.

- **Formato dos Arquivos de Teste:**  
  Os arquivos de teste deverão estar no formato YAML, seguindo uma estrutura pré-definida.

- **Padrão FHIR:**  
  A aplicação focará na conformidade com a versão FHIR R4.

### 2.4 Casos de Uso e Cenários de Aplicação

#### 2.4.1 Ilustrações de Uso
- [Ilustração de usos e fluxos](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md#ilustração-de-usos) que exemplifica os principais cenários de aplicação.

#### 2.4.2 Cenários de Aplicação
- **Validação de Arquivo:**  
  O sistema recebe um arquivo YAML contendo os parâmetros de validação, interpreta o contexto (IGs, profiles, resources) e executa a validação da instância FHIR especificada.
  
- **Geração de Relatório:**  
  Ao final da execução dos testes, o sistema compara os resultados obtidos com os resultados esperados e gera um relatório (HTML e/ou JSON) que destaca as discrepâncias e as classifica apropriadamente.
  
- **Gerenciamento e Execução dos Testes:**  
  O sistema permite:
  - Selecionar arquivos individualmente, por prefixo ou executar todos os testes disponíveis.
  - Realizar a busca, validação de formato e armazenamento dos logs e outputs.

### 2.5 Estrutura do Arquivo de Teste
Cada arquivo de teste em YAML deve seguir a estrutura abaixo:

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
caminho_instancia: caminho/arquivo_fhir.json  #  (Obrigatório) Caminho para o arquivo a ser testado (string)
# Parâmetros para a comparação
resultados_esperados:  #  (Obrigatório) Define os resultados esperados de validação.
  status: success  #  (Obrigatório) Nível geral esperado ('success', 'error', 'warning', 'information').
  error: []  #  (Obrigatório) Lista de erros esperados (lista de string).
  warning: []  #  (Obrigatório) Lista de avisos esperados (lista de string).
  fatal: [] #  (Obrigatório) Lista de mensagens erros fatais esperados (lista de string).
  information: []  #  (Obrigatório) Lista de mensagens informativas esperadas (lista de string).
  invariantes: # (Opcional)
    - expressao: "OperationOutcome.issues.count() = 0" #(string)
      esperado: True # Resultado esperado (Booleano)
```


## 3. Arquitetura e Design

### 3.1 Arquitetura do Sistema
A aplicação será dividida em três grandes componentes, responsáveis pelo fluxo de execução:

1. **Gerenciador de Caso de Teste:**  
   - Organiza e manipula os arquivos de teste.  
   - Realiza a busca por arquivos individualmente ou por prefixo.  
   - Valida a estrutura dos arquivos de teste (YAML) e assegura a presença dos campos obrigatórios.

2. **Executor de Testes:**  
   - Executa o `validator_cli` com base nos parâmetros definidos no arquivo de teste.  
   - Extrai os contextos (IGs, perfis e resources) e localiza a instância a ser validada (através do `caminho_instancia`).  
   - Implementa a execução paralela dos testes, gerenciando o timeout e registrando logs, salvando os resultados em diretórios específicos (temporários ou configurados pelo usuário).

3. **Compilador de Resultados:**  
   - Compara os resultados obtidos pelo validador com os resultados esperados definidos nos arquivos de teste.  
   - Identifica discrepâncias, sejam divergências de valor ou erros na classificação (e.g., error, warning).  
   - Gera relatórios detalhados em HTML (usando Jinja2 e, quando necessário, Plotly para gráficos interativos) ou JSON, resumindo a análise dos diagnósticos e a severidade dos problemas encontrados.

### 3.1 Diagramas de Arquitetura
Diagramas C4:  
- [Diagrama de Contexto](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContexto.png)  
- [Diagrama de Container](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContainer.png)

### 3.2 Tecnologias Utilizadas
- **Linguagem de Programação:** Python  
- **Interface Gráfica:** Streamlit  
- **Validador FHIR:** validator_cli.jar
- **Formato dos Casos de Teste:** YAML  
- **Relatórios:** HTML (usando Jinja2) e JSON  
- **Dependências:** PyYAML, jsonschema, requests e Java para a execução do validador.  


## 4. Conclusão e Próximos Passos

### 4.1 Resultados Esperados
O software deverá:
- Executar os testes de validação dos arquivos FHIR de forma rápida e eficiente.  
- Gerar relatórios detalhados que comparem os resultados obtidos com os esperados, destacando divergências tanto em valores quanto na classificação das mensagens (e.g., error, warning).  
- Fornecer uma interface gráfica intuitiva para o monitoramento e gerenciamento dos testes realizados.

### 4.2 Gestão e Próximos Passos

#### 4.2.1 Membros da Equipe
- **Amanda:** Responsável pelos testes.  
- **Deivison:** Desenvolvimento do Frontend.  
- **Ester:** Desenvolvimento Full Stack.  
- **Leonardo:** Líder do Projeto.  
- **Mateus:** Desenvolvimento Backend.

#### 4.2.2 Comunicação entre a Equipe
A comunicação será realizada principalmente via WhatsApp, permitindo discussões rápidas e alinhamentos constantes.

#### 4.2.3 Possíveis Melhorias Futuras
- Suporte para outras versões do FHIR além da R4.  
- Inclusão de um sistema de autenticação para o acesso seguro à plataforma.  
- Aprimoramento da interface gráfica com recursos adicionais, como filtros avançados e novas opções de visualização.  
- Implementação de mecanismos para a persistência e análise histórica dos resultados dos testes.
