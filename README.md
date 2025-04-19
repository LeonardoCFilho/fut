# FUT  
Repositório para o trabalho de Construção de Software, utilizando o padrão FHIR  
[Plano de construção](https://github.com/LeonardoCFilho/fut/blob/main/Documentacao/Plano_de_construcao.md)  
## Execução:  
[Funcionamento segue a orientação dos requisitos](https://github.com/kyriosdata/construcao-2025-01/blob/main/docs/fut.md#ilustração-de-usos)  
Os comandos descritos estão sendo **executados na pasta principal do projeto** (fut ou fut-main):  
Caso esteja em outro diretório, utilize **endereçamento relativo ou absoluto** para executar o arquivo main.py.
- Linux  
  ```bash  
  python3 Backend/main.py  
  ```
- Windows  
  ```bash  
  python Backend/main.py  
  ```
Adicione '--help' após main.py para mais detalhes quanto os comandos
Exemplo:  
  ```bash  
  python Backend/main.py  --help
  ```

### **Importante**
No momento apenas o relatório JSON é criado, esse relatório será criado na pasta que o projeto é executado, sendo nomeado: relatorio_final_fut.json