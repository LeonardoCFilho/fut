import streamlit as st 
import os 
from pathlib import Path
from Backend.fachada_sistema import FachadaSistema

#TODO: formulario p/ criacao de testes esta recebendo já da fachada_sistema.
def render():
    st.title("Teste Manual")

    if "ig_lista" not in st.session_state:
        st.session_state.ig_lista = []
    if "profile_lista" not in st.session_state:
        st.session_state.profile_lista = []

    home = Path.home()
    #default_path = home / "Projetos" / "stream" / "meu_app" / "temp"
    default_path = Path(__file__).absolute().parent.parent.parent
    path_temp_completo = default_path / '.temp-fut'
    validator_fhir = 'receberDeUmaFuncao'
    diretorio_destino_temp = str(path_temp_completo)
            
    os.makedirs(diretorio_destino_temp, exist_ok=True)

    st.header("Validação via Formulário Manual")
    with st.form("formulario_manual"):
        id_teste = st.text_input('ID*').strip().lower()
        descricao = st.text_input("Descrição (Opcional)")
        igs = st.text_input("IGs (Opcional) - Separe por vírgula")
        profiles = st.text_input("Profiles (Opcional) - Separe por vírgula")
        resources = st.text_input("Resources (Opcional) - Separe por vírgula")
        caminho_instancia = st.text_input("Caminho Instância*")
        status_esperado = st.selectbox(
            "Status Esperado*",
            ["", "success", "error", "warning", "information"],
            help="Nível geral esperado da validação"
        )
        botao_validar = st.form_submit_button("Criar Teste")

    if botao_validar:
        if not id_teste or not caminho_instancia or not status_esperado:
            st.error("Por favor, preencha os campos obrigatórios: ID, Caminho Instância e Status Esperado.")
        else:
            # Processa listas (IGs, Profiles, Resources)
            ig_lista = [ig.strip() for ig in igs.split(",")] if igs else []
            profile_lista = [profile.strip() for profile in profiles.split(",")] if profiles else []
            resource_lista = [res.strip() for res in resources.split(",")] if resources else []

            # Constrói o dicionário no formato exato que a função espera
            dados_teste = {
                "test_id": id_teste,
                "description": descricao,
                "igs": ", ".join(ig_lista) if ig_lista else "",  # String separada por vírgulas
                "profiles": ", ".join(profile_lista) if profile_lista else "",  # String separada por vírgulas
                "resources": ", ".join(resource_lista) if resource_lista else "",  # String separada por vírgulas
                "caminho_instancia": caminho_instancia,
                "status": status_esperado,
                "error": "",  # Pode ser ajustado para receber inputs específicos
                "warning": "",
                "fatal": "",
                "information": "",
                "invariantes": "",  # Pode ser ajustado para receber expressões
            }

            caminho_arquivo = os.path.join(diretorio_destino_temp, f"{id_teste}.yaml")
            
            if os.path.exists(caminho_arquivo):
                st.warning('Arquivo já existe e será sobrescrito!')
            
            try:
                fachada = FachadaSistema()
                
                # Chama a função com os parâmetros corretos
                fachada.gerar_arquivo_teste(
                    dados_teste=dados_teste,
                    caminho_arquivo=caminho_arquivo
                )
                st.success(f"Arquivo YAML criado com sucesso em: {caminho_arquivo}")
            except PermissionError:
                st.error("Erro de permissão: não foi possível criar o arquivo.")
            except Exception as e:
                st.error(f"Erro inesperado ao criar arquivo: {str(e)}")
