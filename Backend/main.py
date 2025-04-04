# Link do colab do código: https://colab.research.google.com/drive/1R8RTxAQ72TZ1_HfuM1KpnZw3b0XzbCNd#scrollTo=h3tl_P7uwiQy

# temp
caminho_do_arquivo_fhir_que_voce_quer_validar = "Arquivos/Testes/ArquivosFHIR/zzrandom_com_erros.json"

if __name__ == '__main__':
    # Importar a classe para executar
    from Classes.executor_teste import ExecutorTestes
    executorDeTestes = ExecutorTestes()  

    # Tentar executar o teste
    resultado = None
    try:
        # Teste com um arquivo JSON/XML
        resultado = executorDeTestes.validarArquivoFhir(caminho_do_arquivo_fhir_que_voce_quer_validar)
    except Exception as e:
        print(f"Erro: {e}")
    
    # Abaixo, a saída da função validar_fhir é formatada para, dentro do dicionário dicio, capturar os campos: warning, error, note, fatal, dentre outros
    dicio = None
    if resultado:
        formatado = resultado.stdout.split("\n")
        dicio = {'erro': [], 'warning': [], 'note': [], 'fatal': [], 'else': []}
        for linha in formatado:
            if 'warning @' in linha.lower():
                dicio['warning'].append(linha)
            elif 'error @' in linha.lower():
                dicio['erro'].append(linha)
            elif 'note @' in linha.lower():
                dicio['note'].append(linha)
            elif 'fatal @' in linha.lower():
                dicio['fatal'].append(linha)
            elif '@' in linha:
                dicio['else'].append(linha)
    if dicio:
        import json
        print(json.dumps(dicio, ensure_ascii=False, indent=4))
    else:
        print("Ocorreu algum erro")