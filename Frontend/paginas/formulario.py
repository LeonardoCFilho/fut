import streamlit as st
from pathlib import Path
from Backend.fachada_sistema import FachadaSistema
import yaml

# FUNÇÃO AUXILIAR PARA VERIFICAR COMPATIBILIDADE
def checar_arquivos_compatibilidade(lista_paths):
    """
    Verifica arquivos YAML e separa os que têm 'caminho_instancia'.
    Se o YAML for lista, cada item deve possuir a chave.
    """
    validos, invalidos = [], []
    for path in lista_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if isinstance(data, dict):
                ok = 'caminho_instancia' in data
            elif isinstance(data, list):
                ok = all(isinstance(item, dict) and 'caminho_instancia' in item for item in data)
            else:
                ok = False

            (validos if ok else invalidos).append(path)
        except Exception:
            invalidos.append(path)
    return validos, invalidos


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
            id_teste = st.text_input('ID*').strip().lower()
            descricao = st.text_area("Descrição (Opcional)")
        with col2:
            igs = st.text_input("IGs (Opcional)")
            profiles = st.text_input("Profiles (Opcional)")
            resources = st.text_input("Resources (Opcional)")
            status_esperado = st.selectbox("Status Esperado*", ["", "success", "error", "warning", "information"])

        if st.form_submit_button("✅ Criar Teste"):
            faltantes = []
            if not id_teste:
                faltantes.append("ID do Teste")
            if not status_esperado:
                faltantes.append("Status Esperado")
            if faltantes:
                st.error(f"🚨 Campos obrigatórios faltando: {', '.join(faltantes)}")
            elif not id_teste.replace("_", "").isalnum():
                st.error("🔤 ID deve conter apenas letras, números e underscores")
            else:
                try:
                    def proc(texto): return [i.strip() for i in texto.split(",") if i.strip()] if texto else []

                    dados = {
                        "test_id": id_teste,
                        "description": descricao,
                        "context": {
                            "igs": proc(igs),
                            "profiles": proc(profiles),
                            "resources": proc(resources)
                        },
                        "caminho_instancia": str(fachada.path_fut),
                        "resultados_esperados": {
                            "status": status_esperado,
                            "error": [],
                            "warning": [],
                            "fatal": [],
                            "information": [],
                            "invariantes": []
                        }
                    }

                    caminho_arquivo = diretorio_execucao / f"{id_teste}.yaml"
                    if caminho_arquivo.exists():
                        st.warning("⚠️ Arquivo já existe e será sobrescrito!")

                    # Correção: gerar YAML diretamente com dump para preservar campos
                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        yaml.dump(dados, f, allow_unicode=True, sort_keys=False)

                    st.success(f"✔️ Arquivo YAML '{caminho_arquivo.name}' criado com sucesso!")
                except Exception as e:
                    st.error(f"⛔ Erro ao criar arquivo: {e}")

    st.divider()

    # --- Execução de Teste ---
    st.header("🚀 Executar Testes")
    try:
        arquivos_yaml = sorted(diretorio_execucao.glob('*.yaml')) + sorted(diretorio_execucao.glob('*.yml'))
        if not arquivos_yaml:
            st.info("ℹ️ Nenhum arquivo de teste encontrado no diretório atual.")
            return

        validos, invalidos = checar_arquivos_compatibilidade(arquivos_yaml)
        if invalidos:
            with st.expander("⚠️ Arquivos incompatíveis ignorados"):
                for f in invalidos:
                    st.code(f.name)

        nomes = [f.name for f in validos]
        if not nomes:
            st.info("ℹ️ Nenhum arquivo compatível encontrado.")
            return

        selecao = st.multiselect("Selecione testes para executar:", nomes)
        if st.button("▶️ Iniciar Execução", disabled=not selecao):
            caminhos = [str(diretorio_execucao / name) for name in selecao]
            progress = st.progress(0)
            placeholder = st.empty()
            resultados = []
            for res in fachada.executar_testes_com_entrega_gradual(caminhos):
                if 'progress' in res:
                    progress.progress(res['progress']/100)
                if 'result' in res:
                    resultados.append(res['result'])
                    placeholder.subheader(f"Resultado {res['result'].get('test_id', '')}")
                    placeholder.json(res['result'])
            st.success("✅ Todos os testes concluídos!")
            report = diretorio_execucao / "relatorio_testes.html"
            if report.exists():
                content = report.read_text(encoding='utf-8')
                st.download_button("📥 Baixar Relatório", content, "relatorio_testes.html", "text/html")
                st.components.v1.html(content, height=600)
    except Exception as e:
        st.error(f"⛔ Erro durante execução: {e}")
