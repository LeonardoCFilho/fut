import streamlit as st
import os
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
from Backend.fachada_sistema import FachadaSistema



# utilizando cache para a inicialização da fachada.
@st.cache_resource
def inicializar_fachada():
    """Inicializa e retorna uma instância da FachadaSistema."""
    return FachadaSistema()

# Cache para a leitura dos metadados dos arquivos.
# A lista de arquivos só será lida do disco se algo mudar (novo arquivo, etc.).
# O ttl (time-to-live) de 600 segundos (10 minutos) invalida o cache periodicamente
# para que a lista de arquivos seja atualizada caso haja mudanças externas.
@st.cache_data(ttl=600)
def carregar_metadados_arquivos(caminho_projeto):
    """
    Lista todos os arquivos YAML e retorna um DataFrame com seus metadados.
    Esta função é otimizada para ser executada poucas vezes.
    """
    #caminho_arquivos_yaml = caminho_projeto / 'Arquivos' / '.temp-fut'
    #Path.cwd() adicionado 
    caminho_arquivos_yaml = Path.cwd()
    if not caminho_arquivos_yaml.is_dir():
        caminho_arquivos_yaml.mkdir(parents=True, exist_ok=True)
        return pd.DataFrame(columns=["Nome", "Tamanho (KB)", "Modificado", "Caminho"])

    files_data = []
    for f in caminho_arquivos_yaml.iterdir():
        if f.is_file() and f.suffix.lower() in ('.yaml', '.yml'):
            try:
                stat = f.stat()
                files_data.append({
                    "Nome": f.name,
                    "Tamanho (KB)": f"{stat.st_size / 1024:.2f}",
                    "Modificado": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    "Caminho": str(f)
                })
            except FileNotFoundError:
                # O arquivo pode ter sido deletado entre o iterdir e o stat
                continue
    
    if not files_data:
        return pd.DataFrame(columns=["Nome", "Tamanho (KB)", "Modificado", "Caminho"])
        
    return pd.DataFrame(files_data)

# OTIMIZAÇÃO: Cache para o conteúdo de um arquivo específico.
# O arquivo só será lido do disco uma vez, a menos que ele mude.
@st.cache_data
def ler_conteudo_yaml(caminho_arquivo):
    """Lê e parseia o conteúdo de um arquivo YAML, com cache."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.error(f"Arquivo '{caminho_arquivo.name}' não encontrado.")
        return None
    except yaml.YAMLError as e:
        st.error(f"Erro de sintaxe no arquivo YAML: {e}")
        return None

# --- Função Principal da Página ---

def render():
    st.title("📂 Test Manager - YAML Files")

    # OTIMIZAÇÃO: Usa a função com cache para inicializar o sistema
    try:
        fachada = inicializar_fachada()
        caminho_projeto = fachada.acharCaminhoProjeto()
        if not caminho_projeto:
            st.error("Não foi possível determinar o caminho do projeto.")
            return
    except Exception as e:
        st.error(f"Erro ao inicializar o sistema: {str(e)}")
        return

    # Configuração de sessão (sem mudanças)
    if 'hidden_files' not in st.session_state:
        st.session_state.hidden_files = set()
    
    session_defaults = {'confirmar_delete': False, 'editando': False}
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # OTIMIZAÇÃO: Carrega todos os metadados de uma vez usando a função com cache
    df_todos_arquivos = carregar_metadados_arquivos(caminho_projeto)

    # Função auxiliar para upload (agora sem st.rerun(), é mais limpo)
    def salvar_arquivos_enviados(uploaded_files, target_path):
        if not uploaded_files: return
        target_path.mkdir(parents=True, exist_ok=True)
        for file in uploaded_files:
            try:
                with open(target_path / file.name, 'wb') as f: f.write(file.getbuffer())
                st.session_state.hidden_files.discard(file.name)
                st.success(f"Arquivo '{file.name}' salvo.")
            except Exception as e:
                st.error(f"Erro ao salvar '{file.name}': {e}")
        # OTIMIZAÇÃO: Invalida o cache para forçar a releitura da lista de arquivos
        carregar_metadados_arquivos.clear()
        st.rerun()

    # Seção de upload inicial
    if df_todos_arquivos.empty:
        st.warning("Nenhum arquivo YAML encontrado.")
        with st.container(border=True):
            st.subheader("➕ Adicionar Arquivos YAML")
            uploaded_files = st.file_uploader("Selecione arquivos", type=['yaml', 'yml'], accept_multiple_files=True, label_visibility="collapsed")
            if uploaded_files:
                #caminho_base_arquivos = caminho_projeto / 'Arquivos' / '.temp-fut'
                caminho_base_arquivos = Path.cwd()
                salvar_arquivos_enviados(uploaded_files, caminho_base_arquivos)
        return

    # Filtra o DataFrame para mostrar apenas arquivos não ocultos
    df_visiveis = df_todos_arquivos[~df_todos_arquivos['Nome'].isin(st.session_state.hidden_files)]

    st.subheader("📋 Lista de Arquivos YAML")
    if df_visiveis.empty:
        st.info("Todos os arquivos estão ocultos.")
        if st.button("Mostrar Todos", key="show_all"):
            st.session_state.hidden_files.clear()
            st.rerun()
        return

    # Seleção de arquivo
    nomes_arquivos = df_visiveis['Nome'].tolist()
    try:
        idx = nomes_arquivos.index(st.session_state.get('selected_file'))
    except (ValueError, TypeError):
        idx = 0
    
    arquivo_selecionado = st.selectbox(
        "Selecione um arquivo:", nomes_arquivos, index=idx, key="selected_file"
    )
    caminho_completo = Path(df_visiveis.set_index('Nome').loc[arquivo_selecionado, 'Caminho'])
    
    st.dataframe(
        df_visiveis[['Nome', 'Tamanho (KB)', 'Modificado']],
        hide_index=True, use_container_width=True,
        column_config={"Nome": "Arquivo", "Tamanho (KB)": st.column_config.NumberColumn(format="%.2f")}
    )

    # Operações com arquivos
    st.subheader(f"🔧 Operações: {arquivo_selecionado}")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("✏️ Editar/Ver", use_container_width=True):
        st.session_state.editando = True
        # A leitura do arquivo ocorrerá na seção de edição
    
    if col2.button("🗑️ Remover da Lista", use_container_width=True):
        st.session_state.confirmar_delete = True

    if col3.button("🔄 Recarregar Lista", use_container_width=True, help="Força a releitura da lista de arquivos do disco"):
        carregar_metadados_arquivos.clear()
        st.rerun()

    # Lógica de confirmação de ocultação
    if st.session_state.get('confirmar_delete'):
        st.warning(f"⚠️ Ocultar '{arquivo_selecionado}' da lista?")
        col_sim, col_nao, _ = st.columns([1, 1, 4])
        if col_sim.button("✅ Sim", key="confirm_hide", use_container_width=True):
            st.session_state.hidden_files.add(arquivo_selecionado)
            st.session_state.confirmar_delete = False
            st.session_state.pop(f"conteudo_{arquivo_selecionado}", None) # Limpa cache de conteúdo se houver
            st.rerun()
        if col_nao.button("❌ Não", key="cancel_hide", use_container_width=True):
            st.session_state.confirmar_delete = False
            st.rerun()

    # Exibição/Edição de conteúdo
    if st.session_state.get('editando'):
        st.markdown("---")
        st.subheader(f"📝 Conteúdo de: {arquivo_selecionado}")
        
        # OTIMIZAÇÃO: Usa a função com cache para ler o conteúdo do arquivo
        conteudo_arquivo = ler_conteudo_yaml(caminho_completo)

        if conteudo_arquivo is not None:
            novo_conteudo_str = st.text_area(
                "Edite o conteúdo YAML:",
                yaml.dump(conteudo_arquivo, allow_unicode=True, sort_keys=False, indent=2),
                height=400, key="editor_yaml"
            )
            col_s, col_c, col_raw = st.columns(3)
            if col_s.button("💾 Salvar", use_container_width=True):
                try:
                    conteudo_validado = yaml.safe_load(novo_conteudo_str)
                    with open(caminho_completo, 'w', encoding='utf-8') as f:
                        yaml.safe_dump(conteudo_validado, f, allow_unicode=True, sort_keys=False, indent=2)
                    ler_conteudo_yaml.clear() # Limpa o cache para este arquivo
                    carregar_metadados_arquivos.clear() # Limpa o cache da lista (data modif. mudou)
                    st.session_state.editando = False
                    st.success("Alterações salvas!")
                    st.rerun()
                except (yaml.YAMLError, IOError) as e:
                    st.error(f"Erro ao salvar: {e}")

            if col_c.button("🚫 Fechar", use_container_width=True):
                st.session_state.editando = False
                st.rerun()

    # Seções finais (upload e mostrar ocultos)
    st.markdown("---")
    with st.expander("⬆️ Adicionar Mais Arquivos"):
        novos_arquivos = st.file_uploader("Selecione", type=['yaml', 'yml'], accept_multiple_files=True, key="bottom_uploader")
        if novos_arquivos:
            #caminho_antigo = caminho_projeto / 'Arquivos' / '.temp-fut'
            caminho = Path.cwd()
            salvar_arquivos_enviados(novos_arquivos, caminho)
            
    if st.session_state.hidden_files:
        if st.button("👁️ Mostrar Arquivos Ocultos"):
            st.session_state.hidden_files.clear()
            st.rerun()
