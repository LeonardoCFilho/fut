import streamlit as st
from pathlib import Path
from Backend.fachada_sistema import FachadaSistema
import yaml
import os

def render():
    st.title("🧪 Teste Manual e Execução")

    try:
        fachada = FachadaSistema()
    except Exception as e:
        st.error(f"⛔ Falha ao inicializar sistema: {e}")
        return

    diretorio_execucao = Path.cwd()

    # --- Criação de Teste ---
    st.header("📝 Criar Novo Arquivo de Teste")
    with st.form(key="formulario_manual", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id_teste = st.text_input('ID*', help="Identificador único (sem espaços ou caracteres especiais)").strip().lower()
            descricao = st.text_area("Descrição (Opcional)")
            
            # Seção para upload ou caminho da instância FHIR
            st.markdown("**Arquivo de Instância FHIR***")
            arquivo_instancia = st.file_uploader("Selecione o arquivo", 
                                               type=['json', 'xml'],
                                               help="Arquivo JSON/XML contendo o recurso FHIR",
                                               label_visibility="collapsed")
            
            st.markdown("**OU**")
            caminho_instancia = st.text_input("Informe o caminho relativo", 
                                            help="Caminho relativo (ex: 'exemplos/paciente.json')",
                                            label_visibility="collapsed")
        
        with col2:
            igs = st.text_input("IGs (Opcional)", help="Separe por vírgulas (ex: br.core,br.paciente)")
            profiles = st.text_input("Profiles (Opcional)", help="Separe por vírgulas (ex: Patient,Observation)")
            resources = st.text_input("Resources (Opcional)", help="Separe por vírgulas (ex: ValueSet,CodeSystem)")
            status_esperado = st.selectbox("Status Esperado*", ["", "success", "error", "warning", "information"])

        if st.form_submit_button("✅ Criar Teste"):
            # Validações
            faltantes = []
            if not id_teste:
                faltantes.append("ID do Teste")
            if not status_esperado:
                faltantes.append("Status Esperado")
            if not arquivo_instancia and not caminho_instancia:
                faltantes.append("Arquivo de Instância (upload ou caminho)")
            
            if faltantes:
                st.error(f"🚨 Campos obrigatórios faltando: {', '.join(faltantes)}")
            elif not id_teste.replace("_", "").isalnum():
                st.error("🔤 ID deve conter apenas letras, números e underscores")
            else:
                try:
                    # Processar o arquivo de instância
                    instancia_path = None
                    caminho_relativo = None
                    
                    if arquivo_instancia:
                        # Salva o arquivo uploadado no diretório de instâncias
                        instancias_dir = diretorio_execucao / "instancias"
                        instancias_dir.mkdir(exist_ok=True)
                        
                        instancia_path = instancias_dir / arquivo_instancia.name
                        with open(instancia_path, "wb") as f:
                            f.write(arquivo_instancia.getbuffer())
                        
                        caminho_relativo = str(instancia_path.relative_to(diretorio_execucao))
                    
                    elif caminho_instancia:
                        # Verifica se o caminho relativo existe
                        caminho_absoluto = diretorio_execucao / caminho_instancia
                        if not caminho_absoluto.exists():
                            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_instancia}")
                        caminho_relativo = caminho_instancia

                    # Processar listas (IGs, Profiles, Resources)
                    def processar_lista(texto): 
                        return [i.strip() for i in texto.split(",") if i.strip()] if texto else []

                    # Criar estrutura do teste
                    dados = {
                        "test_id": id_teste,
                        "description": descricao,
                        "context": {
                            "igs": processar_lista(igs),
                            "profiles": processar_lista(profiles),
                            "resources": processar_lista(resources)
                        },
                        "caminho_instancia": caminho_relativo,
                        "resultados_esperados": {
                            "status": status_esperado,
                            "error": [],
                            "warning": [],
                            "fatal": [],
                            "information": [],
                            "invariantes": []
                        }
                    }

                    # Salvar arquivo YAML de teste
                    caminho_arquivo = diretorio_execucao / f"{id_teste}.yaml"
                    if caminho_arquivo.exists():
                        st.warning("⚠️ Arquivo já existe e será sobrescrito!")

                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        yaml.dump(dados, f, allow_unicode=True, sort_keys=False)

                    st.success(f"✔️ Arquivo YAML '{caminho_arquivo.name}' criado com sucesso!")
                    st.session_state.arquivo_criado = caminho_arquivo.name
                    
                except Exception as e:
                    st.error(f"⛔ Erro ao criar arquivo: {str(e)}")
                    # Remove arquivo temporário se houve erro
                    if 'instancia_path' in locals() and instancia_path and instancia_path.exists():
                        instancia_path.unlink(missing_ok=True)

    st.divider()

    # --- Execução de Teste ---
    st.header("🚀 Executar Testes")
    
    # Opção 1: Selecionar arquivos do diretório atual
    st.subheader("Arquivos no Diretório Atual")
    arquivos_locais = sorted(diretorio_execucao.glob('*.yaml')) + sorted(diretorio_execucao.glob('*.yml'))
    
    # Seleciona automaticamente o último arquivo criado
    default_selection = []
    if 'arquivo_criado' in st.session_state and st.session_state.arquivo_criado:
        default_selection = [st.session_state.arquivo_criado]
    
    if not arquivos_locais:
        st.info("ℹ️ Nenhum arquivo de teste encontrado no diretório atual.")
    else:
        nomes_locais = [f.name for f in arquivos_locais]
        selecao_local = st.multiselect("Selecione arquivos do diretório atual:", 
                                      nomes_locais,
                                      default=default_selection)
    
    # Opção 2: Upload de arquivos de outros diretórios
    st.subheader("Ou selecione arquivos de outro diretório")
    arquivos_upload = st.file_uploader("Selecione arquivos YAML", 
                                     type=['yaml', 'yml'], 
                                     accept_multiple_files=True,
                                     help="Arquivos YAML contendo definições de teste")
    
    # Preparar lista completa de arquivos para execução
    arquivos_para_executar = []
    
    # Adicionar arquivos locais selecionados
    if 'selecao_local' in locals() and selecao_local:
        arquivos_para_executar.extend([str(diretorio_execucao / name) for name in selecao_local])
    
    # Adicionar arquivos uploadados
    if arquivos_upload:
        # Criar diretório temporário se não existir
        temp_dir = diretorio_execucao / "temp_uploads"
        temp_dir.mkdir(exist_ok=True)
        
        for uploaded_file in arquivos_upload:
            # Salvar arquivo no diretório temporário
            file_path = temp_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            arquivos_para_executar.append(str(file_path))
    
    # Botão de execução
    if st.button("▶️ Iniciar Execução", disabled=not arquivos_para_executar):
        try:
            progress = st.progress(0)
            placeholder = st.empty()
            resultados = []
            
            for res in fachada.executar_testes_com_entrega_gradual(arquivos_para_executar):
                if 'progress' in res:
                    progress.progress(res['progress']/100)
                if 'result' in res:
                    resultados.append(res['result'])
                    with placeholder.container():
                        st.subheader("📊 Resultados Parciais")
                        for resultado in resultados:
                            with st.expander(f"Teste: {resultado.get('test_id', 'N/A')}"):
                                st.json(resultado)
            
            st.success("✅ Todos os testes concluídos!")
            
            # Limpar arquivos temporários após execução
            if arquivos_upload:
                for file_path in arquivos_para_executar:
                    if "temp_uploads" in file_path:
                        Path(file_path).unlink(missing_ok=True)
            
            # Gerar relatório
            report = diretorio_execucao / "relatorio_testes.html"
            if report.exists():
                content = report.read_text(encoding='utf-8')
                st.download_button("📥 Baixar Relatório", content, "relatorio_testes.html", "text/html")
                st.subheader("Pré-visualização do Relatório")
                st.components.v1.html(content, height=600, scrolling=True)
                
        except Exception as e:
            st.error(f"⛔ Erro durante execução: {str(e)}")
        finally:
                # Limpeza final de arquivos temporários
            if arquivos_upload:
                        temp_dir = diretorio_execucao / "temp_uploads"
                        for file in temp_dir.glob("*"):
                            file.unlink(missing_ok=True)
