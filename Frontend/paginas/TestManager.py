import streamlit as st
import os
import yaml
from pathlib import Path

def render():
    st.title("Test Manager")

    # carrega arquivos recentementes
    def carregar_arquivos_recentes():
        return st.session_state.get('arquivos_recentes', [])

    # atualiza a lista de arquivos recentes
    def atualizar_arquivos_recentes(nome_arquivo):
        recentes = carregar_arquivos_recentes()
        if nome_arquivo in recentes:
            recentes.remove(nome_arquivo)
        recentes.insert(0, nome_arquivo)
        st.session_state['arquivos_recentes'] = recentes[:7]  #7 arquivos recentes

    st.title("Gerenciador de Testes YAML")


    home = Path.home()
    default_path = home / "Projetos" / "stream" / "meu_app" / "temp"

    # o caminho da pasta
    pasta_destino = st.text_input("Digite o caminho da pasta:", 
                                  str(default_path))

    # verifica se o caminho é valido
    if os.path.isdir(pasta_destino):
        
        arquivos = [arq for arq in os.listdir(pasta_destino) if arq.endswith('.yaml') and os.path.isfile(os.path.join(pasta_destino, arq))]
        
        if arquivos:
            # Opção para exibir todos os arquivos
            #if st.checkbox('Exibir todos os arquivos'):
            for arquivo in arquivos:
                st.write(f'- {arquivo}')
            
            # Campo de texto para filtrar arquivos por nome
            filtro = st.text_input("Filtrar arquivos por nome:")
            arquivos_filtrados = [arq for arq in arquivos if filtro.lower() in arq.lower()] if filtro else arquivos
            
            if arquivos_filtrados:
                st.write("Arquivos encontrados:")
                for arquivo in arquivos_filtrados:
                    st.write(f"- {arquivo}")
                
                # selecionar de um arquivo especifico
                arquivo_selecionado = st.selectbox("Selecione um arquivo para visualizar/editar:", arquivos_filtrados)
                caminho_arquivo = os.path.join(pasta_destino, arquivo_selecionado)

            #botoes coluna
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Ler"):
                        try:
                            with open(caminho_arquivo, 'r', encoding='utf-8') as file:
                                conteudo = yaml.safe_load(file)
                                if conteudo:
                                    for x, y in conteudo.items():
                                        st.write(f'{x}: {y}')
                                else:
                                    st.write('Conteúdo vazio')
                                st.session_state['conteudo_arquivo'] = conteudo
                            atualizar_arquivos_recentes(arquivo_selecionado)
                        except Exception as e:
                            st.error(f"Erro ao ler o arquivo: {e}")
                with col2:
                    if st.button("Editar"):
                        if 'conteudo_arquivo' in st.session_state:
                            conteudo = st.session_state['conteudo_arquivo']
                            novo_conteudo = st.text_area("Edite o conteúdo YAML:", yaml.dump(conteudo, allow_unicode=True), height=300)
                            if st.button("Salvar alterações"):
                                try:
                                    with open(caminho_arquivo, 'w', encoding='utf-8') as file:
                                        yaml.safe_dump(yaml.safe_load(novo_conteudo), file, allow_unicode=True)
                                    st.success("Arquivo salvo com sucesso.")
                                    atualizar_arquivos_recentes(arquivo_selecionado)
                                except Exception as e:
                                    st.error(f"Erro ao salvar o arquivo: {e}")
                        else:
                            st.warning("Por favor, leia o arquivo antes de editá-lo.")

                with col3:
                    if 'confirmar_delete' not in st.session_state:
                        st.session_state.confirmar_delete = False

                    if not st.session_state.confirmar_delete:
                        if st.button("Deletar"):
                            st.session_state.confirmar_delete = True
                    else:
                        st.warning("Tem certeza que deseja deletar?")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Sim, deletar"):
                                try:
                                    os.remove(caminho_arquivo)
                                    st.success("Arquivo deletado com sucesso.")
                                    arquivos.remove(arquivo_selecionado)
                                    if 'conteudo_arquivo' in st.session_state:
                                        del st.session_state['conteudo_arquivo']
                                    if arquivo_selecionado in st.session_state.get('arquivos_recentes', []):
                                        st.session_state['arquivos_recentes'].remove(arquivo_selecionado)
                                    st.session_state.confirmar_delete = False
                                except Exception as e:
                                    st.error(f"Erro ao deletar o arquivo: {e}")
                        with col_b:
                            if st.button("Cancelar"):
                                st.session_state.confirmar_delete = False
                
            else:
                st.warning("Nenhum arquivo corresponde ao filtro fornecido.")

            # exibir arquivos recentes
            arquivos_recentes = carregar_arquivos_recentes()
            if arquivos_recentes:
                st.subheader("Arquivos Recentemente Acessados:")
                for arq in arquivos_recentes:
                    st.write(f"- {arq}")
        else:
            st.warning("A pasta selecionada não contém arquivos YAML.")
    else:
        st.error("O caminho fornecido não é um diretório válido.")
