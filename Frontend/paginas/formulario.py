import streamlit as st 
import os 
from pathlib import Path
from Backend.fachada_sistema import FachadaSistema

#TODO: formulario p/ criacao de testes esta recebendo já da fachada_sistema.

def render():
    # Configuração inicial
    st.title("🧪 Teste Manual")
    
    # Inicialização de estado
    session_defaults = {
        "ig_lista": [],
        "profile_lista": [],
        "form_submitted": False
    }
    
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Inicialização da Fachada com tratamento de erro
    try:
        fachada = FachadaSistema()
        caminho_projeto = fachada.acharCaminhoProjeto()
        
        if not caminho_projeto or not caminho_projeto.exists():
            st.error("❌ Caminho do projeto não encontrado ou inválido")
            return
            
    except Exception as e:
        st.error(f"⛔ Falha ao inicializar sistema: {str(e)}")
        return

    # Preparação do diretório temporário
    try:
        path_temp_completo = caminho_projeto / 'Arquivos' / '.temp-fut'
        path_temp_completo.mkdir(parents=True, exist_ok=True)
        diretorio_destino_temp = str(path_temp_completo.resolve())
        
    except Exception as e:
        st.error(f"📂 Erro ao acessar diretório temporário: {str(e)}")
        return

    # Formulário principal
    st.header("📝 Validação via Formulário Manual")
    
    with st.form(key="formulario_manual", clear_on_submit=True):
        # Campos do formulário
        col1, col2 = st.columns(2)
        
        with col1:
            id_teste = st.text_input(
                'ID*',
                help="Identificador único para o teste (sem espaços ou caracteres especiais)",
                placeholder="ex: teste_validacao_01"
            ).strip().lower()
            
            descricao = st.text_area(
                "Descrição (Opcional)",
                placeholder="Descreva o propósito deste teste"
            )
            
            caminho_instancia = st.text_input(
                "Caminho Instância*",
                help="Caminho relativo ou absoluto para o arquivo de instância FHIR",
                placeholder="ex: exemplos/paciente.json"
            )
            
        with col2:
            igs = st.text_input(
                "IGs (Opcional) - Separe por vírgula",
                placeholder="ex: br.core, br.paciente"
            )
            
            profiles = st.text_input(
                "Profiles (Opcional) - Separe por vírgula",
                placeholder="ex: Patient, Observation"
            )
            
            resources = st.text_input(
                "Resources (Opcional) - Separe por vírgula",
                placeholder="ex: ValueSet, CodeSystem"
            )
            
            status_esperado = st.selectbox(
                "Status Esperado*",
                options=["", "success", "error", "warning", "information"],
                help="Nível geral esperado da validação"
            )
        
        # Validação e submissão
        submitted = st.form_submit_button("✅ Criar Teste")
        
        if submitted:
            st.session_state.form_submitted = True
            
            # Validação dos campos obrigatórios
            campos_obrigatorios = {
                "ID do Teste": id_teste,
                "Caminho da Instância": caminho_instancia,
                "Status Esperado": status_esperado
            }
            
            campos_faltantes = [nome for nome, valor in campos_obrigatorios.items() if not valor]
            
            if campos_faltantes:
                st.error(f"🚨 Campos obrigatórios faltando: {', '.join(campos_faltantes)}")
                return
                
            # Validação do ID do teste
            if not id_teste.replace("_", "").isalnum():
                st.error("🔤 ID deve conter apenas letras, números e underscores")
                return

    # Processamento após submissão válida
    if st.session_state.form_submitted and not campos_faltantes:
        try:
            # Processamento das listas
            def processar_lista(texto):
                return [item.strip() for item in texto.split(",") if item.strip()] if texto else []
            
            ig_lista = processar_lista(igs)
            profile_lista = processar_lista(profiles)
            resource_lista = processar_lista(resources)

            # Construção do dicionário de teste
            dados_teste = {
                "test_id": id_teste,
                "description": descricao,
                "context": {
                    "igs": ig_lista,
                    "profiles": profile_lista,
                    "resources": resource_lista
                },
                "caminho_instancia": caminho_instancia,
                "resultados_esperados": {
                    "status": status_esperado,
                    "error": [],
                    "warning": [],
                    "fatal": [],
                    "information": [],
                    "invariantes": []
                }
            }

            # Verificação e criação do arquivo
            caminho_arquivo = path_temp_completo / f"{id_teste}.yaml"
            
            if caminho_arquivo.exists():
                st.warning("⚠️ Arquivo já existe e será sobrescrito!")
                
            try:
                # Criação do arquivo via Fachada
                fachada.gerar_arquivo_teste(
                    dados_teste=dados_teste,
                    caminho_arquivo=str(caminho_arquivo))
                
                st.success(f"✔️ Arquivo YAML criado com sucesso!")
                st.code(str(caminho_arquivo), language="text")
                
                # Reset do formulário se necessário
                st.session_state.form_submitted = False
                
            except PermissionError:
                st.error("🔒 Erro de permissão: não foi possível criar o arquivo.")
            except yaml.YAMLError:
                st.error("📄 Erro na formatação YAML ao gerar o arquivo.")
            except Exception as e:
                st.error(f"⛔ Erro inesperado ao criar arquivo: {str(e)}")
                
        except Exception as e:
            st.error(f"⚙️ Erro no processamento do formulário: {str(e)}")