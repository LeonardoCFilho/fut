import streamlit as st
import os
import yaml


def render():
    st.title("Configurações")
    #st.write("Configurações da aplicação.")

    st.header("Configurações")

    # escolha do validador
    validadores_disponiveis = ["validador_padrao", "validador_customizado"]
    validador_selecionado = st.selectbox("Escolha o validador:", validadores_disponiveis)

    # .json do resultado
    manter_json = st.checkbox("Manter arquivo .json do resultado", value=True)

    # timeout em segundos
    timeout = st.number_input("Tempo de timeout (segundos):", min_value=1, max_value=300, value=60, step=1)

    # threads
    max_threads = st.number_input("Número máximo de threads:", min_value=1, max_value=10, value=2, step=1)

    # armazenamento
    #diretorio_armazenamento = st.text_input("Diretório de armazenamento:", value=os.path.join(os.getcwd(), "resultados"))
    pegar_armazenamento = ...
    # botão p/ salvar configurações
    if st.button("Salvar Configurações"):
        # aq p/ salvar essas configurações em um arquivo ou variável de sessão
        #st.success("Configurações salvas com sucesso!")
        
        # salvando aq cm exemplo
        st.session_state.configuracoes = {
            "validador": validador_selecionado,
            "manter_json": manter_json,
            "timeout": timeout,
            "max_threads": max_threads,
            "diretorio_armazenamento": pegar_armazenamento
        }
        
        os.makedirs(pegar_armazenamento, exist_ok=True)
        try:
            caminho_arquivo = os.path.join(pegar_armazenamento, f"Config.yaml")
            with open(caminho_arquivo, 'w', encoding="utf-8") as config:
                yaml.dump(st.session_state.configuracoes, config, allow_unicode=True)
                st.success('Configurações salvas com sucesso!')
        except Exception as e:
            print(f'Erro: {e}')
            ...
