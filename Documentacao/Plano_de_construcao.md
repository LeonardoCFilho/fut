# Plano de Construção Atualizado

## 1. Introdução

### 1.1 Visão Geral do Projeto
O projeto consiste na construção de uma aplicação para a validação de arquivos FHIR denominada **FHIRUT (FHIR Unit Test Suite)**. O sistema receberá casos de teste organizados em arquivos YAML, executará a validação das instâncias FHIR (em JSON ou XML) e gerará relatórios detalhados (em HTML e/ou JSON). A aplicação oferecerá tanto uma **interface de linha de comando (CLI)** quanto uma **interface gráfica**, permitindo acompanhar a execução dos testes, visualizar estatísticas e gerenciar casos de teste.

### 1.2 Escopo do Projeto
O sistema abordará as seguintes funcionalidades:  
- **Validação dos Arquivos FHIR:** Verificação da estrutura e conformidade dos dados com o padrão FHIR R4.  
- **Execução de Testes:** Realização dos testes definidos em arquivos YAML, com comparação dos resultados obtidos em relação aos resultados esperados.  
- **Interface Dupla:** Comando executável `fut` para linha de comando e interface gráfica Streamlit.
- **Geração de Relatórios:** Produção de relatórios detalhados que sumarizam os testes executados, destacando divergências em valor ou na classificação.  
- **Execução Paralela e Controle de Timeout:** Execução eficiente dos testes utilizando paralelização e mecanismos de timeout para evitar travamentos.  

## 2. Requisitos

### 2.1 Requisitos Funcionais

#### 2.1.1 Interface de Linha de Comando (CLI)
- **Comando `fut` executável:** O sistema deverá fornecer uma interface de linha de comando que permita execução via terminal
- **Execução sem argumentos:** `fut` - Executa todos os testes (.yaml/.yml) no diretório corrente
- **Execução de teste específico:** `fut teste/x.yml y.yml` - Executa testes específicos
- **Execução com wildcards:** `fut patient-*.yml` - Executa testes que correspondam ao padrão

#### 2.1.2 Validação de Arquivos FHIR
O sistema deverá validar arquivos FHIR em formato JSON ou XML, assegurando a conformidade com o padrão FHIR R4.

#### 2.1.3 Convenções de Nomenclatura de Arquivos
**Campo de instância:** `caminho_instancia` (substitui `instance_path`)

**Lógica de Resolução de Instâncias:**
Quando `caminho_instancia` não for fornecido, o sistema deverá buscar automaticamente:
1. **Primeira prioridade:** Arquivo com mesmo nome do YAML, mas extensão `.json`
2. **Segunda prioridade:** Arquivo com nome igual ao `test_id` e extensão `.json`
3. **Falha:** Se nenhuma convenção localizar arquivo, execução do teste falha com erro informativo

#### 2.1.4 Execução por Padrões de Arquivo (Wildcards)
- **Suporte a wildcards:** Sistema deverá interpretar padrões como `*`, `?`, `[...]`
- **Execução em lote:** Permite execução de múltiplos testes baseado em padrões de nomenclatura
- **Ordenação:** Arquivos encontrados via padrão devem ser executados em ordem alfabética

#### 2.1.5 Geração de Relatórios
Após a execução dos testes, o software gerará relatórios detalhados em um dos seguintes formatos:
- **JSON:** Estrutura dos resultados, diferenciando resultados esperados e obtidos.
- **HTML:** Interface que permite uma navegação fácil e sucinta.

#### 2.1.6 Execução Paralela e Controle de Timeout
Implementação de execução paralela dos testes, com configuração de número máximo de threads e controle de timeout para evitar travamentos.

#### 2.1.7 Atualização do Validador
Download e verificação da versão mais recente do `validator_cli`, permitindo personalizações (como endereçamento e parâmetros de execução).

### 2.2 Requisitos Não Funcionais

#### 2.2.1 Interface Gráfica
A aplicação deverá oferecer uma interface gráfica intuitiva, desenvolvida com Streamlit, que permita a execução dos testes, monitoramento dos resultados e gerenciamento dos casos de teste.

#### 2.2.2 Tratamento de Erros Robusto

**Categorias de Erro a Implementar:**

**Erros de Arquivo:**
- **Arquivos YAML ausentes:** Mensagem específica com caminho esperado
- **YAML malformado:** Parser com indicação de linha/coluna do erro
- **Instâncias FHIR ausentes:** Erro com caminhos tentados pela convenção
- **Permissões de arquivo:** Detecção e tratamento de problemas de acesso

**Erros do Validador:**
- **Validador não encontrado:** Verificação de existência do validator_cli.jar
- **Timeout de validação:** Interrupção controlada com mensagem informativa
- **Falha na execução:** Captura de stderr e stdout para diagnóstico
- **Versão incompatível:** Verificação de compatibilidade de versão

**Erros de Configuração:**
- **Parâmetros inválidos:** Validação de entrada com mensagens específicas
- **Contexto inválido:** Verificação de IGs, perfis e recursos especificados
- **Recursos faltantes:** Detecção de dependências não satisfeitas

**Estratégias de Recuperação:**
- **Continuação parcial:** Prosseguir com outros testes em caso de falha individual
- **Retry automático:** Tentativas adicionais para falhas temporárias
- **Fallback:** Alternativas quando recursos primários falham
- **Logging detalhado:** Registro completo para troubleshooting

#### 2.2.3 Desempenho
O sistema deverá executar os testes de maneira rápida e eficiente, otimizando recursos através da paralelização e de um adequado gerenciamento de timeouts.

#### 2.2.4 Configurações Avançadas

**Sistema de Configuração Global:**

**Níveis de Configuração (por prioridade):**
1. **Argumentos de linha de comando** (maior prioridade)
2. **Variáveis de ambiente**
3. **Arquivo de configuração global** (~/.fut/config.yaml)
4. **Configurações padrão** (menor prioridade)

**Configurações Suportadas:**
```yaml
# ~/.fut/Arquivos/settings.ini
desempenho:
  timeout: 300
  max_threads: 8
  requests_timeout: 120

enderecamento:
  caminho_validator: default
  armazenar_saida_validator: False
```

**Interface de Configuração:**
- **Comando de configuração:** `fut config --list`, `fut config --set key=value`
- **Validação de configuração:** Verificação de valores válidos na inicialização
<!-- - **Configuração interativa:** Wizard para primeira configuração -->
<!-- - **Localização global:** Configurações armazenadas no diretório home do usuário -->

### 2.3 Restrições e Limitações
- **Validador:**  
  Apenas o `validator_cli` será utilizado para a validação dos arquivos FHIR.

- **Formato dos Arquivos de Teste:**  
  Os arquivos de teste deverão estar no formato YAML, seguindo uma estrutura pré-definida.

- **Padrão FHIR:**  
  A aplicação focará na conformidade com a versão FHIR R4.

### 2.4 Casos de Uso e Cenários de Aplicação

#### 2.4.1 Ilustrações de Uso
**Execução via CLI:**
- `fut` - Executa todos os testes no diretório corrente
- `fut teste/x.yml y.yml` - Executa testes específicos
- `fut patient-*.yml` - Executa testes que correspondam ao padrão

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

Enquanto uma suite de testes seguiria a seguinte estrutura:  
```yaml  
suite_name: "FHIR Validation Suite"  
tests:
  - {YAML seguindo a estrutura acima}  
  ...  
  - {YAML seguindo a estrutura acima}  
```

**Regras para caminho_instancia:**
- Se `caminho_instancia` é fornecida, indica a instância a ser verificada.
- **Convenção:** Se o arquivo em `caminho_instancia` não for encontrado, a ferramenta irá procurar por:
  - Arquivo com o mesmo nome do arquivo YAML, mas com a extensão .json.
  - Se não encontrado, um arquivo com o nome `test_id` e a extensão .json será empregado.
- Se o arquivo ainda não é encontrado, então a execução do teste falha.

## 3. Arquitetura e Design

### 3.1 Arquitetura do Sistema
A aplicação será dividida em quatro grandes componentes, responsáveis pelo fluxo de execução:

1. **Interface de Linha de Comando (CLI):**
<!--    - Interpreta argumentos e padrões de arquivo -->
   - Gerencia configurações globais
   - Fornece acesso para a execução da GUI
   - Coordena execução de testes via linha de comando
<!--    - Implementa resolução de wildcards e padrões de arquivo -->

2. **Gerenciador de Caso de Teste:**  
   - Organiza e manipula os arquivos de teste.  
   - Realiza a busca por arquivos individualmente ou por prefixo.  
   - Valida a estrutura dos arquivos de teste (YAML) e assegura a presença dos campos obrigatórios.
   - Implementa convenções de nomenclatura para resolução automática de instâncias.

3. **Executor de Testes:**  
   - Executa o `validator_cli` com base nos parâmetros definidos no arquivo de teste.  
   - Extrai os contextos (IGs, perfis e resources) e localiza a instância a ser validada (através do `caminho_instancia`).  
   - Implementa a execução paralela dos testes, gerenciando o timeout e registrando logs, salvando os resultados em diretórios específicos (temporários ou configurados pelo usuário).

4. **Compilador de Resultados:**  
   - Compara os resultados obtidos pelo validador com os resultados esperados definidos nos arquivos de teste.  
   - Identifica discrepâncias, sejam divergências de valor ou erros na classificação (e.g., error, warning).  
   - Gera relatórios detalhados em HTML (usando Jinja2 e, quando necessário, Plotly para gráficos interativos) ou JSON, resumindo a análise dos diagnósticos e a severidade dos problemas encontrados.

### 3.2 Diagramas de Arquitetura
Diagramas de alto nível
  - Diagramas C4:  
    - [Diagrama de Contexto](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContexto.png)  
    - [Diagrama de Container](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaContainer.png)  
    - [Diagrama de Componente](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaComponente.png)  

Diagramas de baixo nível
  - Diagrama de classe UML  
    - [Diagrama de classe](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Diagramas/DiagramaClasse.png)  

### 3.3 Tecnologias Utilizadas
- **Linguagem de Programação:** Python  
- **Interface de Linha de Comando:** argparse, glob
- **Interface Gráfica:** Streamlit  
- **Validador FHIR:** validator_cli.jar
- **Formato dos Casos de Teste:** YAML  
- **Relatórios:** HTML (usando Jinja2) e JSON  
- **Dependências:** PyYAML, jsonschema, requests e Java para a execução do validador.  

## 4. Implementação Técnica

### 4.1 Componentes CLI
- Desenvolver script executável Python com argparse
<!-- - Criar sistema de instalação para comando global -->
- Manter compatibilidade com interface gráfica Streamlit existente
- Implementar parser de argumentos para diferentes modos de execução

### 4.2 Resolução de Instâncias
- Modificar parser YAML para suportar novo campo `caminho_instancia`
- Implementar algoritmo de resolução automática de instâncias
<!-- - Atualizar validação de arquivos de teste -->
<!-- - Criar mensagens de erro específicas para instâncias não encontradas -->

### 4.3 Execução com Wildcards
- Utilizar biblioteca `glob` para resolução de padrões
- Implementar validação de arquivos encontrados
- Criar feedback sobre quantos arquivos foram localizados
<!-- - Manter logs de quais arquivos foram processados -->

### 4.4 Sistema de Configuração
<!-- - Implementar hierarquia de configurações (CLI > ENV > Global > Padrão) -->
- Criar parser para arquivo de configuração YAML global
- Desenvolver comandos de gerenciamento de configuração
- Implementar validação de configurações na inicialização

## 5. Conclusão e Próximos Passos

### 5.1 Resultados Esperados
O software deverá:
- Executar os testes de validação dos arquivos FHIR de forma rápida e eficiente via CLI ou GUI.  
- Implementar resolução automática de instâncias seguindo convenções de nomenclatura.
- Suportar execução em lote através de padrões de arquivo (wildcards).
- Gerar relatórios detalhados que comparem os resultados obtidos com os esperados, destacando divergências tanto em valores quanto na classificação das mensagens (e.g., error, warning).  
- Fornecer tratamento robusto de erros com estratégias de recuperação.
- Fornecer uma interface gráfica intuitiva para o monitoramento e gerenciamento dos testes realizados.

### 5.2 Gestão e Próximos Passos

#### 5.2.1 Membros da Equipe
- **Deivison:** Desenvolvimento do Frontend.  
- **Ester:** Desenvolvimento Full Stack.  
- **Leonardo:** Líder do Projeto.  
- **Mateus:** Desenvolvimento Backend.

#### 5.2.2 Comunicação entre a Equipe
A comunicação será realizada principalmente via WhatsApp, permitindo discussões rápidas e alinhamentos constantes.

#### 5.2.3 Possíveis Melhorias Futuras
- Suporte para outras versões do FHIR além da R4.  
- Inclusão de um sistema de autenticação para o acesso seguro à plataforma.  
- Aprimoramento da interface gráfica com recursos adicionais, como filtros avançados e novas opções de visualização.  
- Implementação de mecanismos para a persistência e análise histórica dos resultados dos testes.
- Suporte a outros validadores FHIR além do validator_cli.