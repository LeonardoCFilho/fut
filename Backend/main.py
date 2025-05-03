from pathlib import Path
import sys
import logging 

def organizarLogs(pathLog: Path):
    if pathLog.exists():
        pathOldLog = pathLog.with_name('OLD_fut.log')
        if pathOldLog.exists(): # Já tinha um antigo => sobrescrever
            pathOldLog.unlink()
        pathLog.rename(pathOldLog)

def acharCaminhoProjeto() -> Path:
    maxIteracoes = 10
    numIteracoes = 0
    pathFut = Path(__file__)  # Diretório do arquivo atual
    while "fut" not in pathFut.name:  # Subir um nível se o diretório atual não for 'fut'
        pathFut = pathFut.parent
        numIteracoes +=1 
        if numIteracoes >= maxIteracoes:
            sys.exit("Problemas ao encontrar a pasta do projeto, renomeie-a para 'fut' ou 'fut-main'")
    return pathFut

if __name__ == "__main__":
    # Caminhos utilizados no nosso projeto
    pathFut = acharCaminhoProjeto()
    pathTerminal = pathFut / "Backend" / "terminal.py"
    pathLog  = pathFut / 'Arquivos' / 'fut.log'

    # Logs
    organizarLogs(pathLog) # Garantir que a execução atual terá log próprio
    # Iniciando o log
    logging.basicConfig(level=logging.INFO, # .info, .warning, .error, .critical
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(pathLog.resolve(), mode='a')])
    logger = logging.getLogger(__name__)

    # Iniciar execução do programa (leitura do terminal)
    logger.info("Iniciando o sistema")
    print("Iniciando o sistema:")
    # Lendo o terminal (entrada será transferida para apps.py)
    args = sys.argv[1:]  # Ler args
    if not args: # Nada foi escrito => enviar string vazia
        args = '' 
    if len(args) == 1 and isinstance(args,list): # Lista de 1 elemento == string normal
        args = args[0]

    # Começar a execução em si do cli
    from terminal import mainMenu
    mainMenu(args)
    #try:
    #    mainMenu(args)
    #    print("\n\nPrograma finalizado!")
    #    logger.info("Execução do sistema finalizada")
    #except Exception as e:
    #    logger.error(f"Erro no sistema de testes: {str(e)}")
    #    print(f"Erro: {str(e)}")