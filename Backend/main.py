# Link do colab do código: https://colab.research.google.com/drive/1R8RTxAQ72TZ1_HfuM1KpnZw3b0XzbCNd#scrollTo=h3tl_P7uwiQy

if __name__ == "__main__":
    # pip freeze > Arquivos/requirements.txt
    from pathlib import Path
    # Caminhos utilizados no nosso projeto
    pathFut = Path(__file__)  # Diretório do arquivo atual
    while "fut" not in pathFut.name:  # Subir um nível se o diretório atual for 'fut'
        pathFut = pathFut.parent
    pathVenv = pathFut / ".venv-fut"
    pathApps = pathFut / "Backend" / "apps.py"

    # Organizando o ambiente virtual
    print("Configurando ambiente virtual...")
    from setup import setupAmbienteVirtual
    setupAmbienteVirtual(pathFut, pathVenv)

    # Iniciar execução do programa (leitura do terminal)
    print("Iniciando o sistema:")
    import platform, sys, subprocess
    # Lendo o terminal (entrada será transferida para apps.py)
    args = sys.argv[1:]  # Ler args 
    args_str = " ".join(args) if args else ''   # Converter para string (vazia ou não)
    # Criando o comando de acordo com o SO (executar o codigo com o ambiente virtual)
    soAtual = platform.system()
    if soAtual == "Windows":
        argsAmbienteVirtual = f"{pathVenv.resolve()}\\Scripts\\activate"
        comandoMain = f'cmd /c "{argsAmbienteVirtual} & python {pathApps} {args_str}"'
    else:
        argsAmbienteVirtual = f"bash -i -c 'source {pathVenv}/bin/activate"
        comandoMain = f"{argsAmbienteVirtual} && python3 {pathApps} {args_str}'"  
    try:   
        subprocess.run(comandoMain, shell=True, check=True) # Executar o ambiente virtual e apps.py
    except subprocess.CalledProcessError as e:
        print(f"Erro: {e}")