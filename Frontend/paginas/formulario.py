import streamlit  as st 
import yaml
import os 
from pathlib import Path

def render():
    st.title("Teste Manual")
    #st.write("Conteúdo do formulário.")

    if "ig_lista" not in st.session_state:
        st.session_state.ig_lista = []
    if "profile_lista" not in st.session_state:
        st.session_state.profile_lista = []

    home = Path.home()
    default_path = home / "Projetos" / "stream" / "meu_app" / "temp"
    validator_fhir = 'receberDeUmaFuncao'
    #cuidado com o endereço, este é o do meu pc, modifique  ****
    diretorio_destino_temp = str(default_path)
            
    os.makedirs(diretorio_destino_temp, exist_ok=True)

    st.header("Validação via Formulário Manual")
    with st.form("formulario_manual"):
            id = (st.text_input('ID*')).strip().lower() ##
            descricao = st.text_input("Descrição (Opcional)")##
            #contexto = st.text_input("Contexto") ##
            igs = st.text_input("IGs (Opcional)") ##
            profiles = st.text_input("Profiles (Opcional)")##
            resources = st.text_input("Resources (Opcional)")##
            caminho_instancia = st.text_input("Caminho Instância*")##
            default_validator = "caminho/ou/link/do/validador_padrao"
            botao_validar = st.form_submit_button("Criar Teste")

    if botao_validar:
        if not id or not caminho_instancia:
            st.error("Por favor, preencha ambos os campos obrigatórios.")
        else:
            if igs:
                st.session_state.ig_lista.extend([ig.strip() for ig in igs.split(",") if ig.strip()])
            if profiles:
                st.session_state.profile_lista.extend([profile.strip() for profile in profiles.split(",") if profile.strip()])
            contexto = ''
            dados_teste = {
            "test_id": id,
            "description": descricao,
            "context": contexto,
            "igs": st.session_state.ig_lista,
            "profiles": st.session_state.profile_lista,
            "resources": [item.strip() for item in resources.split(",")] if resources else [],
            "instance_path": caminho_instancia,
            "validator": validator_fhir
        }
        
            if f'{id}.yaml' in os.listdir(diretorio_destino_temp):
                st.text('Arquivo já existe')
            else:
                try:
                    caminho_arquivo = os.path.join(diretorio_destino_temp, f"{id}.yaml")
                    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo_yaml:
                        yaml.dump(dados_teste, arquivo_yaml, allow_unicode=True)
                    st.success(f"Arquivo salvo com sucesso em: {caminho_arquivo}")
                    ...
                except Exception as e:
                    st.error(f'Erro ao salvar arquivo {e}')
                    ...