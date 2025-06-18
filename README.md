# FUT  
Repositório para o trabalho de Construção de Software, utilizando o padrão FHIR  
[Plano de construção](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md)  
## Execução:  
[Funcionamento segue a orientação dos requisitos](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md#ilustração-de-usos)  
Os comandos descritos estão sendo **executados na pasta principal do projeto** (fut ou fut-main):  
Caso esteja em outro diretório, utilize **endereçamento relativo ou absoluto** para executar o arquivo main.py.

## Primeira execução:
### 1. Baixe o codigo
- Ou instale o .zip do codigo e o extrai. ([Encontrado aqui](https://github.com/LeonardoCFilho/fut/archive/refs/heads/main.zip))
- Ou faça um clone do diretorio, via:
  ```bash
  git clone LeonardoCFilho/fut
  ```

### 2. Abra o projeto no terminal
  ```bash
  cd fut-main
  ```

### 3. Realize a instalação do docker
- Windows
  ```bash
  install.bat
  ```
- Linux/MacOS  
  ```bash
  chmod +x install.sh && ./install.sh
  ```

E com isso a instalação será concluída

### Execução do programa
- Linux  
  ```bash  
  fut  
  ```
- Windows  
  ```bash  
  fut  
  ```
Adicione '--help' após main.py para mais detalhes quanto o sistema
Exemplo:  
  ```bash  
  fut --help
  ```

### **Importante**
No momento apenas o relatório JSON é criado, esse relatório será criado na pasta que o projeto é executado, sendo nomeado: relatorio_final_fut.json
