import subprocess
import sys
import venv
from pathlib import Path

# Ideia: Buscar um requirements.txt (na pasta arquivos) e tenta instalar todas bibliotecas
# P.s.: Após a instação o arquivo é renomeado para evitar redundância
def instalarRequirements(pathFut):
    print("Buscando arquivo requirements...")
    try:
        pathRequirements = pathFut / "Arquivos" / "requirements.txt"
        if pathRequirements.exists():
            print("Arquivo encontrado!\nInstalando bibliotecas...")
            result = subprocess.check_output([sys.executable, "-m", "pip", "install", "-r", str(pathRequirements)], stderr=subprocess.STDOUT, text=True)
            pathRequirements.rename(pathFut / "Arquivos" / "OLDrequirements.txt")
            return result  # Retorna a saída capturada
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro: {e}")
        return e.output  # Retorna a saída de erro

# Ideia: Verifica as bibliotecas do ambiente virtual e tenta atualizar todas
# P.s.: Lenta devido a verificação individual de bibliotecas e possível download (internet do usuário pode aumentar o tempo de execução drasticamente)
def check_for_updates():
    print("Verificando bibliotecas desatualizadas...")
    try:
        # Procurando desatualizadas
        outdated = subprocess.check_output([sys.executable, "-m", "pip", "list", "--outdated"], stderr=subprocess.STDOUT, text=True)
        if outdated.strip():  # Tem alguma(s) desatualizada(s)
            print("Os seguintes pacotes estão desatualizados:")
            print(outdated)
            # Extrai os nomes dos pacotes e os atualiza
            print("\nAtualizando pacotes desatualizados...")
            for line in outdated.splitlines()[2:]:  # Ignora cabeçalhos
                package_name = line.split()[0]  # Extrai o nome do pacote
                print(f"Atualizando {package_name}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])  # Atualiza o pacote
            print("\nTodos os pacotes desatualizados foram atualizados!")
        else:
            print("Todas as bibliotecas estão atualizadas!")
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro ao verificar ou atualizar as bibliotecas: {e}")
        return e.output  

# Ideia: Maneja tudo que envolve o ambiente virtual
def setupAmbienteVirtual(pathFut:Path, pathVenv:Path):
    # Criar o ambiente (se necessário)
    if not pathVenv.exists():
        print("Criando um ambiente virtual...")
        venv.create(pathVenv , with_pip=True)
    else:
        print("Ambiente já foi criado!")
    # Verifica o arquivo requirements.txt
    instalarRequirements(pathFut)
    # Atualiza bibliotecas
    # Tentar otimizar
    #check_for_updates() 
    print("Ambiente virtual preparado!\n")