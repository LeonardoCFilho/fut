from asyncio import sleep
from pathlib import Path
import requests
from Classes.inicializador_sistema import InicializadorSistema
class GerenciadorDownloads(InicializadorSistema):
    def __init__(self, pathFut):
        super().__init__(pathFut)

    # Ideia: Faz download de um arquivo a partir de uma URL para o caminho especificado.
    # P.s.: Especificar o tipo de arquivo no nome do arquivo
    def baixaArquivoUrl(self, url, enderecoArquivo, maxTentativas = 3):
        numTentativas = 0
        while numTentativas < maxTentativas:
            try:
                # Iniciando request
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Lança exceção em caso de erro

                # Iniciando download
                enderecoArquivo = Path(enderecoArquivo)
                with enderecoArquivo.open("wb") as arquivo_baixado:
                    for chunk in response.iter_content(chunk_size=8192):
                        arquivo_baixado.write(chunk)
                return 

            # Caso de erro, adicionar logs
            except Exception as e:
                numTentativas += 1 # Contabilizar tentativa
                if numTentativas < maxTentativas:
                    print(f"Erro na tentativa {numTentativas+1} de download, reiniciando...")
                    sleep(3)
                else:
                    raise e