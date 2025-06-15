import streamlit as st
import os
from Backend.fachada_sistema import FachadaSistema
import logging

# Configura o logger para ajudar a depurar
logger = logging.getLogger(__name__)

def render():
    """
    Renderiza a página de configurações, interagindo com a FachadaSistema
    para carregar e salvar as configurações.
    """
    st.title("⚙️ Configuração dos Testes")
    st.caption("Altere os parâmetros de execução dos testes de validação FHIR.")

    try:
        
        fachada = FachadaSistema()
    except Exception as e:
        st.error(f"Não foi possível inicializar o sistema de configuração: {e}")
        st.info("Verifique se o programa está sendo executado a partir do diretório correto do projeto.")
        logger.error(f"Erro ao instanciar FachadaSistema: {e}")
        return

    #  CARREGAR CONFIGURAÇÕES INICIAIS 
    # Usa a fachada para obter cada valor do settings.ini, com valores padrão em caso de falha.
    try:
        timeout_default = int(fachada.obter_configuracao("requests_timeout") or 60)
        max_threads_default = int(fachada.obter_configuracao("max_threads") or 4)
        armazenar_saida_val_str = str(fachada.obter_configuracao("armazenar_saida_validator") or "False")
        armazenar_saida_default = armazenar_saida_val_str.lower() in ["true", "1", "yes"]
        path_validator_default = fachada.obter_configuracao("caminho_validator") or ""

    except Exception as e:
        st.error(f"Erro ao carregar as configurações: {e}")
        logger.error(f"Falha ao chamar obter_configuracao: {e}")
        # Define valores padrão para a aplicação não quebrar
        timeout_default = 60
        max_threads_default = 4
        armazenar_saida_default = False
        path_validator_default = ""


    # WIDGETS DA INTERFACE 

    st.subheader("Validador FHIR")
    
    # Define o índice do selectbox com base no valor carregado
    is_custom_validator = path_validator_default and path_validator_default.lower() != "default"
    validator_index = 1 if is_custom_validator else 0
    
    validador_selecionado = st.selectbox(
        "Escolha o validador a ser utilizado:", 
        ("Padrão (Incluso no sistema)", "Customizado (Executável local)"),
        index=validator_index
    )

    caminho_validator_input = ""
    if validador_selecionado == "Customizado (Executável local)":
        caminho_validator_input = st.text_input(
            "Caminho do executável do validador customizado:",
            value=path_validator_default if is_custom_validator else ""
        )
    
    armazenar_saida_validator = st.checkbox(
        "Armazenar saída completa do Validator a cada execução",
        value=armazenar_saida_default
    )

    st.divider()

    st.subheader("Desempenho e Rede")
    max_threads = st.number_input(
        "Número máximo de threads (testes em paralelo):",
        min_value=1, max_value=50,
        value=max_threads_default
    )

    timeout = st.number_input(
        "Timeout das requisições (segundos):",
        min_value=1, max_value=600,
        value=timeout_default,
        help="Tempo máximo que o sistema aguardará por uma resposta de um servidor externo."
    )

    st.divider()

   #Salvando alterações
   
    if st.button("Salvar Configurações", type="primary", use_container_width=True):
        
        # Define o valor do caminho do validador com base na seleção
        if validador_selecionado == "Customizado (Executável local)":
            # Se o campo estiver vazio, retorna para o padrão para evitar erros
            valor_caminho_validator = caminho_validator_input if caminho_validator_input.strip() else "default"
        else:
            valor_caminho_validator = "default"
            
        # Dicionário com as configurações a serem salvas
        configuracoes_para_salvar = {
            "caminho_validator": valor_caminho_validator,
            "armazenar_saida_validator": armazenar_saida_validator,
            "max_threads": max_threads,
            "requests_timeout": timeout,
        }
        
        sucesso = True
        erros = []

        # Itera sobre cada configuração e usa a fachada para atualizá-la
        for chave, valor in configuracoes_para_salvar.items():
            try:
                if not fachada.atualizar_configuracao(chave, valor):
                    sucesso = False
                    erros.append(f"Falha ao salvar '{chave}'.")
            except Exception as e:
                sucesso = False
                erros.append(f"Erro ao salvar '{chave}': {e}")
                logger.error(f"Erro ao chamar atualizar_configuracao para {chave}: {e}")

        if sucesso:
            st.success('Configurações salvas com sucesso!')
            st.toast('✅ Suas preferências foram atualizadas.')
        else:
            st.error("Ocorreram erros ao salvar algumas configurações:")
            for erro in erros:
                st.write(erro)

