import subprocess
import json

caminho_do_arquivo_fhir_que_voce_quer_validar = "zzrandom_com_erros.json"

# O validador não está nativamente contido nessa pasta, baixe-o aqui: https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar 
caminho_do_jar_do_validador_fhir_que_voce_quer_usar = "validator_cli.jar" # se não for a 4.0.1 não vai funcionar

# função que vai validar
def validar_fhir(arquivo_fhir: str, jar_path: str = caminho_do_jar_do_validador_fhir_que_voce_quer_usar):
    """Executa a validação de um arquivo FHIR usando o validator_cli.jar da HL7 vers"""
    try:
        # comando que será executado no subprocess
        comando = ["java", "-jar", jar_path, arquivo_fhir, "-version", "4.0.1"]

        # resultado da execução so subprocess
        resultado = subprocess.run(comando, capture_output=True, text=True)

        return resultado
    except Exception as e:
        return None

# Teste com um arquivo JSON/XML
resultado = validar_fhir(caminho_do_arquivo_fhir_que_voce_quer_validar)

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
    print(json.dumps(dicio, ensure_ascii=False, indent=4))
else:
    print("Ocorreu algum erro")