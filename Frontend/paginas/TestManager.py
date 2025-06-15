import streamlit as st
import os
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
from Backend.fachada_sistema import FachadaSistema

def render():
    st.title("📂 Test Manager - YAML Files")
    
    # Inicialização da Fachada
    try:
        fachada = FachadaSistema()
        caminho_projeto = fachada.acharCaminhoProjeto()
        if not caminho_projeto:
            st.error("Não foi possível determinar o caminho do projeto")
            return
    except Exception as e:
        st.error(f"Erro ao inicializar sistema: {str(e)}")
        return

    # Configuração de sessão
    session_defaults = {
        'arquivos_recentes': [],
        'conteudo_arquivo': None,
        'confirmar_delete': False,
        'editando': False,
        'show_raw': False
    }
    
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Funções auxiliares
    def atualizar_arquivos_recentes(nome_arquivo):
        recentes = st.session_state.arquivos_recentes
        if nome_arquivo in recentes:
            recentes.remove(nome_arquivo)
        recentes.insert(0, nome_arquivo)
        st.session_state.arquivos_recentes = recentes[:7]

    def get_file_info(file_path):
        stat = file_path.stat()
        return {
            "Nome": file_path.name,
            "Tamanho (KB)": f"{stat.st_size / 1024:.2f}",
            "Modificado": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            "Caminho": str(file_path)
        }

    # Seção de listagem de arquivos
    st.subheader("📋 Lista de Arquivos YAML")
    
    caminho_arquivos = caminho_projeto / 'Arquivos' /'.temp-fut'
    arquivos = []
    
    try:
        if caminho_arquivos.exists():
            arquivos = [caminho_arquivos/arq for arq in os.listdir(caminho_arquivos) 
                        if arq.endswith(('.yaml', '.yml')) and (caminho_arquivos/arq).is_file()]
            
            if not arquivos:
                st.warning("Nenhum arquivo YAML encontrado na pasta.")
                return
            
            # Criar DataFrame com informações dos arquivos
            files_data = [get_file_info(f) for f in arquivos]
            df = pd.DataFrame(files_data)
            
            # Exibir tabela interativa
            st.dataframe(
                df[['Nome', 'Tamanho (KB)', 'Modificado']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Nome": "Arquivo",
                    "Tamanho (KB)": st.column_config.NumberColumn(format="%.2f"),
                    "Modificado": "Última Modificação"
                }
            )
            
            # Seleção de arquivo
            arquivo_selecionado = st.selectbox(
                "Selecione um arquivo para operar:",
                df['Nome'].tolist(),
                index=0,
                key="select_arquivo"
            )
            
            caminho_completo = caminho_arquivos / arquivo_selecionado
        else:
            st.warning("Pasta de arquivos YAML não encontrada")
            return
    except Exception as e:
        st.error(f"Erro ao carregar arquivos: {str(e)}")
        return

    # Operações com arquivos
    st.subheader(f"🔧 Operações: {arquivo_selecionado}")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📖 Ler Arquivo", use_container_width=True):
            try:
                with open(caminho_completo, 'r', encoding='utf-8') as file:
                    conteudo = yaml.safe_load(file)
                    st.session_state.conteudo_arquivo = conteudo
                    atualizar_arquivos_recentes(arquivo_selecionado)
                    st.success("Arquivo carregado com sucesso!")
                    st.session_state.show_raw = False
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {str(e)}")

    with col2:
        if st.button("✏️ Editar Arquivo", use_container_width=True):
            if st.session_state.conteudo_arquivo is None:
                st.warning("Leia o arquivo antes de editar")
            else:
                st.session_state.editando = True

    with col3:
        if st.button("👁️ Mostrar RAW", use_container_width=True):
            st.session_state.show_raw = not st.session_state.show_raw

    with col4:
        if st.button("🗑️ Deletar Arquivo", use_container_width=True):
            st.session_state.confirmar_delete = True

    # Confirmação de deleção
    if st.session_state.confirmar_delete:
        st.warning("⚠️ Tem certeza que deseja deletar este arquivo?")
        col_sim, col_nao = st.columns(2)
        with col_sim:
            if st.button("✅ Confirmar", use_container_width=True):
                try:
                    os.remove(caminho_completo)
                    st.success(f"Arquivo {arquivo_selecionado} removido!")
                    if arquivo_selecionado in st.session_state.arquivos_recentes:
                        st.session_state.arquivos_recentes.remove(arquivo_selecionado)
                    st.session_state.confirmar_delete = False
                    st.session_state.conteudo_arquivo = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao deletar: {str(e)}")
        with col_nao:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.confirmar_delete = False

    # Exibição/Edição de conteúdo
    if st.session_state.conteudo_arquivo:
        st.subheader(f"📝 Conteúdo: {arquivo_selecionado}")
        
        if st.session_state.editando:
            novo_conteudo = st.text_area(
                "Edite o conteúdo YAML:",
                yaml.dump(st.session_state.conteudo_arquivo, allow_unicode=True, sort_keys=False),
                height=400,
                key="editor_yaml"
            )
            
            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                if st.button("💾 Salvar Alterações", use_container_width=True):
                    try:
                        with open(caminho_completo, 'w', encoding='utf-8') as file:
                            yaml.safe_dump(yaml.safe_load(novo_conteudo), file, allow_unicode=True, sort_keys=False)
                        st.session_state.conteudo_arquivo = yaml.safe_load(novo_conteudo)
                        st.session_state.editando = False
                        st.success("Alterações salvas com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
            with col_cancelar:
                if st.button("🚫 Cancelar Edição", use_container_width=True):
                    st.session_state.editando = False
        else:
            data = st.session_state.conteudo_arquivo
            
            if st.session_state.show_raw:
                # Visualização RAW simplificada
                st.code(yaml.dump(data, allow_unicode=True, sort_keys=False), language='yaml')
            else:
                # Visualização organizada em abas
                tab1, tab2 = st.tabs(["Visão Geral", "Detalhes"])
                
                with tab1:
                    # Card de informações básicas
                    st.markdown("### Informações Básicas")
                    cols = st.columns(3)
                    cols[0].metric("Test ID", data.get('test_id', 'N/A'))
                    cols[1].metric("Status Esperado", data.get('resultados_esperados', {}).get('status', 'N/A'))
                    cols[2].metric("Descrição", data.get('description', 'N/A')[:20] + "..." if data.get('description') else 'N/A')
                    
                    # Contexto resumido
                    st.markdown("### Contexto")
                    if 'context' in data:
                        context_cols = st.columns(3)
                        context_cols[0].metric("IGs", len(data['context'].get('igs', [])))
                        context_cols[1].metric("Profiles", len(data['context'].get('profiles', [])))
                        context_cols[2].metric("Resources", len(data['context'].get('resources', [])))
                
                with tab2:
                    # Detalhes completos
                    st.markdown("### Contexto Completo")
                    if 'context' in data:
                        st.json(data['context'], expanded=False)
                    else:
                        st.warning("Nenhum contexto definido")
                    
                    st.markdown("### Resultados Esperados")
                    expected = data.get('resultados_esperados', {})
                    st.json(expected, expanded=False)

    # Seção de arquivos recentes
    if st.session_state.arquivos_recentes:
        st.subheader("⏳ Arquivos Recentes")
        recent_cols = st.columns(4)
        for i, arq in enumerate(st.session_state.arquivos_recentes[:4]):
            with recent_cols[i]:
                if st.button(f"📄 {arq}", key=f"recente_{arq}", use_container_width=True):
                    st.session_state.select_arquivo = arq
                    st.rerun()

    # Upload de novos arquivos
    st.subheader("⬆️ Enviar Novos Arquivos")
    with st.form("upload-form", clear_on_submit=True):
        novo_arquivo = st.file_uploader(
            "Selecione um arquivo YAML para upload",
            type=['yaml', 'yml'],
            key="uploader"
        )
        
        submitted = st.form_submit_button("Enviar Arquivo")
        if submitted and novo_arquivo is not None:
            destino = caminho_arquivos / novo_arquivo.name
            try:
                with open(destino, 'wb') as f:
                    f.write(novo_arquivo.getbuffer())
                st.success(f"Arquivo {novo_arquivo.name} salvo com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro no upload: {str(e)}")