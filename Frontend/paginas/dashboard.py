import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

@st.cache_data(ttl=20)  # Cache expira após 5 minutos ou se o arquivo mudar
def load_report_data():
    """
    Carrega e prepara os dados do histórico de testes.
    Versão atualizada para detectar mudanças no arquivo CSV.
    """
    data_dir = Path(__file__).absolute().parent.parent.parent
    csv_path = data_dir / "Arquivos" / "historico.csv"
    
    # Captura o timestamp de modificação do arquivo
    file_timestamp = csv_path.stat().st_mtime if csv_path.exists() else 0
    
    if not csv_path.exists():
        return pd.DataFrame(), file_timestamp
    
    try:
        df = pd.read_csv(csv_path)
        
        if 'data' not in df.columns:
            st.error("O arquivo 'historico.csv' não contém a coluna 'data'.")
            return pd.DataFrame(), file_timestamp
            
        # Conversão robusta de datas
        df['data'] = pd.to_datetime(df['data'], format='%Y/%m/%d - %H:%M', errors='coerce')
        df.dropna(subset=['data'], inplace=True)
        
        # Ordenação decrescente por data (testes mais recentes primeiro)
        df.sort_values(by='data', ascending=False, inplace=True)
        
        return df, file_timestamp
    except Exception as e:
        st.error(f"Erro ao processar o arquivo CSV: {str(e)}")
        return pd.DataFrame(), file_timestamp

def show_report(selected_test):
    st.title("📊 Análise Completa - FHIR")
    st.caption(f"Visualizando teste realizado em: {selected_test['data'].strftime('%Y/%m/%d %H:%M')}")
    
    # Métricas resumidas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Testes", selected_test.get("numeros_de_testes_totais", 0))
    col2.metric("Válidos", selected_test.get("numero_de_testes_validos", 0), 
                f"{selected_test.get('numero_de_testes_validos', 0)/selected_test.get('numeros_de_testes_totais', 1):.0%}")
    col3.metric("Inválidos", 
                selected_test.get("numeros_de_testes_totais", 0) - selected_test.get("numero_de_testes_validos", 0),
                f"{(selected_test.get('numeros_de_testes_totais', 0) - selected_test.get('numero_de_testes_validos', 0))/selected_test.get('numeros_de_testes_totais', 1):.0%}")
    
    # Métricas de performance
    st.divider()
    st.subheader("📈 Estatísticas de Performance")
    
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    perf_col1.metric("Tempo Total (segundos)", selected_test.get("tempo_total", 0))
    perf_col2.metric("Tempo Médio por Teste (segundos)", f"{selected_test.get('tempo_medio', 0):.1f}")
    perf_col3.metric("Data da Execução", selected_test['data'].strftime('%Y/%m/%d %H:%M'))
    
    # Estatísticas de erros
    st.divider()
    st.subheader("📊 Estatísticas de Erros")
    
    error_col1, error_col2, error_col3, error_col4 = st.columns(4)
    error_col1.metric("Erros Totais", selected_test.get("quantidade_error_reais_totais", 0))
    error_col2.metric("Warnings Totais", selected_test.get("quantidade_warning_reais_totais", 0))
    error_col3.metric("Fatais Totais", selected_test.get("quantidade_fatal_reais_totais", 0))
    error_col4.metric("Informações Totais", selected_test.get("quantidade_information_reais_totais", 0))
    
    # Taxas de acerto
    st.divider()
    st.subheader("🎯 Taxas de Acerto")
    
    accuracy_col1, accuracy_col2, accuracy_col3, accuracy_col4 = st.columns(4)
    accuracy_col1.metric("Acerto em Erros", f"{selected_test.get('%_error_reais_acertados', 0)*100:.1f}%")
    accuracy_col2.metric("Acerto em Warnings", f"{selected_test.get('%_warning_reais_acertados', 0)*100:.1f}%")
    accuracy_col3.metric("Acerto em Fatais", f"{selected_test.get('%_fatal_reais_acertados', 0)*100:.1f}%")
    accuracy_col4.metric("Acerto em Informações", f"{selected_test.get('%_information_reais_acertados', 0)*100:.1f}%")

def render():
    # Carrega os dados com o novo sistema de cache
    report_data = load_report_data()
    report_df = report_data[0] if isinstance(report_data, tuple) else report_data
    
    if report_df.empty:
        st.title("📊 Análise Completa - FHIR")
        st.write("")
        st.info("Bem-vindo ao Painel de Relatórios! 👋")
        st.info('🕒 Nenhum relatório de teste foi encontrado. Execute uma validação para visualizar os resultados aqui!')
        st.markdown("""
        Parece que você ainda não executou nenhum conjunto de testes. Para gerar seu primeiro relatório,
        vá para a página de **Execução de Testes** e inicie uma nova validação.

        Assim que um teste for concluído, os resultados aparecerão aqui automaticamente.
        """)
        st.subheader("Aguardando novos resultados...")
        _, col, _ = st.columns([1, 2, 1])
        col.image("https://cdn-icons-png.flaticon.com/512/1484/1484883.png", width=200, caption="Nenhum dado para exibir")
        return

    # Sidebar de navegação
    st.sidebar.title("⚙️ Navegação")
    
    # Obtém datas únicas (já ordenadas decrescentemente)
    dates = report_df['data'].dt.strftime('%Y/%m/%d %H:%M').unique()
    
    selected_date = st.sidebar.selectbox(
        "Selecione um teste pela data",
        options=dates,
        index=0  # Seleciona o mais recente por padrão
    )
    
    # Filtra o teste selecionado
    filtered_df = report_df[report_df['data'].dt.strftime('%Y/%m/%d %H:%M') == selected_date]
    
    if not filtered_df.empty:
        selected_test = filtered_df.iloc[0]
        show_report(selected_test)
    else:
        st.error("Erro: Não foi possível carregar os dados para a data selecionada.")
    
    # Opção para mostrar dados brutos
    st.sidebar.divider()
    if st.sidebar.checkbox("Mostrar dados brutos"):
        st.subheader("📝 Dados Brutos do Teste")
        st.dataframe(report_df, use_container_width=True)

if __name__ == "__main__":
    render()
