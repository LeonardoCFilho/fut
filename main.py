from pathlib import Path
import sys
import logging 

def organizarLogs(pathLog: Path):
    """
    Organiza arquivos de log numerados, mantendo um histórico rotativo.

    Args:
        pathLog (Path): Caminho para o arquivo de log principal (ex: `fut.log`).
    """
    numeroMaximoLogs = 5
    # Apagar o ultimo (se existir)
    ultimoLogPossivel = pathLog.with_name(f'fut_{numeroMaximoLogs}.log')
    if ultimoLogPossivel.exists():
        ultimoLogPossivel.unlink()  
    # Renomear em sequencia
    for i in range(numeroMaximoLogs-1, 0, -1):
        tempOldLog = pathLog.with_name(f'fut_{i}.log')
        if tempOldLog.exists():
            tempOldLog.rename(pathLog.with_name(f'fut_{i+1}.log'))


def acharCaminhoProjeto() -> Path:
    """
    Encontra o caminho do diretório do projeto onde o nome do diretório contém 'fut'.
    
    Returns:
        Path: O caminho do diretório do projeto.

    Raises:
        SystemExit: Se o diretório do projeto não for encontrado dentro do número máximo de iterações definidas.
    """
    maxIteracoes = 10
    numIteracoes = 0
    pathFut = Path(__file__)  # Diretório do arquivo atual
    while "fut" not in pathFut.name:  # Subir um nível se o diretório atual não for 'fut'
        pathFut = pathFut.parent
        numIteracoes +=1 
        if numIteracoes >= maxIteracoes:
            sys.exit("Problemas ao encontrar a pasta do projeto, renomeie-a para 'fut' ou 'fut-main'")
    return pathFut


def prepararSistema():
    from Backend.Classes.gerenciador_testes import GerenciadorTestes
    # Preparar para execução
    GerenciadorTestes.get_instance(acharCaminhoProjeto())

if __name__ == "__main__":
    # Caminhos utilizados no nosso projeto
    prepararSistema()
    pathFut = acharCaminhoProjeto()
    pathLog  = pathFut / 'Arquivos' / 'fut_1.log'

    # Logs
    organizarLogs(pathLog) # Garantir que a execução atual terá log próprio
    # Iniciando o log
    logging.basicConfig(level=logging.INFO, # .info, .warning, .error, .critical
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(pathLog.resolve(), mode='a')])
    logger = logging.getLogger(__name__)

    # Iniciar execução do programa (leitura do terminal)
    logger.info("Iniciando o sistema")
    print("Iniciando o sistema...")
    # Lendo o terminal (entrada será transferida para apps.py)
    args = sys.argv[1:]  # Ler args
    if not args: # Nada foi escrito => enviar string vazia
        args = '' 
    if len(args) == 1 and isinstance(args,list): # Lista de 1 elemento == string normal
        args = args[0]

    # Começar a execução em si do cli
    from Backend.terminal_ui import mainMenu
    try:
        mainMenu(args)
        # ...
        print("\n\nPrograma finalizado!")
        logger.info("Execução do sistema finalizada")
    except Exception as e:
        logger.error(f"Erro no sistema de testes: {str(e)}")
        print(f"Erro: {str(e)}")