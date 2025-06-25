import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# ESTRUTURA: Funções movidas para o escopo global. Melhora a organização
# sem qualquer impacto visual ou funcional.

@st.cache_data
def load_report_data():
    """
    Carrega e prepara os dados do histórico de testes.
    A lógica interna foi tornada mais robusta.
    """
    data_dir = Path(__file__).absolute().parent.parent.parent
    csv_path = data_dir / "Arquivos" / "historico.csv"
    
    if not csv_path.exists():
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        
        # ROBUSTEZ: Garante que a coluna 'data' exista
        if 'data' not in df.columns:
            st.error("O arquivo 'historico.csv' não contém a coluna 'data'.")
            return pd.DataFrame()
            
        # ROBUSTEZ: `errors='coerce'` previne quebras com datas mal formatadas.
        df['data'] = pd.to_datetime(df['data'], format='%Y/%m/%d - %H:%M', errors='coerce')
        df.dropna(subset=['data'], inplace=True)
        
        # ROBUSTEZ: Ordenar por data aqui (decrescente) torna a seleção do item
        # mais recente (index=0) mais simples e 100% confiável.
        df.sort_values(by='data', ascending=False, inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Erro ao ler ou processar o arquivo CSV: {str(e)}")
        return pd.DataFrame()

# OTIMIZAÇÃO: A geração de gráficos pode ser uma operação cara.
# Colocá-la em cache significa que os gráficos só serão recalculados
# se os dados do `selected_test` mudarem, tornando a resposta da UI mais rápida.
@st.cache_data
def create_charts(selected_test_dict):
    """
    Cria todos os gráficos Plotly com base nos dados de um único teste.
    Mantido 100% fiel à lógica e aparência originais.
    """
    # Para o cache funcionar corretamente com dicionários, é melhor passar uma cópia imutável
    # ou garantir que a função seja puramente dependente da entrada. Passar o dicionário é ok aqui.
    
    # Gráfico 1: Distribuição de status
    validos = selected_test_dict.get("numero_de_testes_validos", 0)
    # Lógica original para totais e inválidos mantida
    totais = selected_test_dict.get("numeros_de_testes_totais", 1) 
    invalidos = totais - validos
    
    status_data = {
        "Status": ["Válidos", "Inválidos"],
        "Quantidade": [validos, invalidos]
    }
    
    fig1 = px.pie(status_data, names="Status", values="Quantidade", 
                  title="Distribuição de Status dos Testes",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    
    # Gráfico 2: Tipos de Erros
    error_data = {
        "Tipo": ["Erros", "Warnings", "Fatais", "Informações"],
        "Quantidade": [
            selected_test_dict.get("quantidade_error_reais_totais", 0),
            selected_test_dict.get("quantidade_warning_reais_totais", 0),
            selected_test_dict.get("quantidade_fatal_reais_totais", 0),
            selected_test_dict.get("quantidade_information_reais_totais", 0)
        ]
    }
    fig2 = px.bar(error_data, x="Tipo", y="Quantidade", 
                  title="Distribuição de Tipos de Erros",
                  color="Tipo",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    
    # Gráfico 3: Taxas de Acerto
    accuracy_data = {
        "Tipo": ["Erros", "Warnings", "Fatais", "Informações"],
        "Taxa (%)": [
            selected_test_dict.get("%_error_reais_acertados", 0)*100,
            selected_test_dict.get("%_warning_reais_acertados", 0)*100,
            selected_test_dict.get("%_fatal_reais_acertados", 0)*100,
            selected_test_dict.get("%_information_reais_acertados", 0)*100
        ]
    }
    fig3 = px.bar(accuracy_data, x="Tipo", y="Taxa (%)", 
                  title="Taxas de Acerto por Tipo de Validação",
                  range_y=[0, 100],
                  color="Tipo",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    
    return fig1, fig2, fig3

def render():
    # Esconder menu lateral (mantido como no original)
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    # Carregar dados
    report_df = load_report_data()
    #TODO: modificar o nome 'execução de testes' para o nome correto da página
    # MELHORIA SUTIL: Uma tela de boas-vindas consistente com a outra página.
    if report_df.empty:
        st.title("📊 Análise Rápida - FHIR")
        st.info("📈 Nenhum dado de teste disponível para gerar os gráficos. Execute uma validação primeiro!", icon="💡")
        st.markdown("""
        Parece que você ainda não executou nenhum conjunto de testes. Para gerar seu primeiro relatório,
        vá para a página de **Execução de Testes** e inicie uma nova validação.

        Assim que um teste for concluído, os resultados aparecerão aqui automaticamente.
    """)
        _, col, _ = st.columns([1, 2, 1])
        col.image("https://cdn-icons-png.flaticon.com/512/6105/6105341.png", width=200, caption="Aguardando dados...")
        return

    # --- Sidebar de Navegação ---
    st.sidebar.title("⚙️ Navegação")
    
    # O DataFrame já vem ordenado, então a lógica fica mais simples e confiável.
    dates = report_df['data'].dt.strftime('%Y/%m/%d %H:%M').unique()
    selected_date = st.sidebar.selectbox(
        "Selecione um teste pela data",
        options=dates,
        index=0  # Mostrar o mais recente por padrão (garantido pela ordenação)
    )
    
    # --- Lógica de Filtragem e Exibição ---
    
    # ROBUSTEZ: Verifica se o filtro retornou algum resultado antes de continuar.
    filtered_df = report_df[report_df['data'].dt.strftime('%Y/%m/%d %H:%M') == selected_date]
    if filtered_df.empty:
        st.error("Erro ao encontrar os dados para a data selecionada. Por favor, recarregue.")
        return
        
    # Converte a linha selecionada para um dicionário para passar para a função de criação de gráficos
    selected_test = filtered_df.iloc[0].to_dict()
    
    # Cabeçalho (mantido idêntico)
    st.title("📊 Análise Rápida - FHIR")
    # Acessa a data do dicionário. `selected_test['data']` ainda é um objeto datetime.
    st.write(f"**Data do teste selecionado:** {selected_test['data'].strftime('%Y/%m/%d %H:%M')}")
    
    # Seção de Métricas Principais (mantida idêntica)
    st.header("📈 Métricas Principais")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Testes", selected_test.get("numeros_de_testes_totais", 0))
    col2.metric("Testes Válidos", 
                  f"{selected_test.get('numero_de_testes_validos', 0)} ({selected_test.get('numero_de_testes_validos', 0)/selected_test.get('numeros_de_testes_totais', 1):.0%})")
    col3.metric("Tempo Médio", f"{selected_test.get('tempo_medio', 0):.1f} seg")
    col4.metric("Tempo Total", f"{selected_test.get('tempo_total', 0):.1f} seg")
    
    # Gráficos (mantidos idênticos na exibição)
    st.header("📊 Visualizações")
    # OTIMIZAÇÃO: A chamada agora usa a função com cache.
    fig1, fig2, fig3 = create_charts(selected_test)
    
    tab1, tab2, tab3 = st.tabs(["Status dos Testes", "Distribuição de Erros", "Taxas de Acerto"])
    
    with tab1:
        st.plotly_chart(fig1, use_container_width=True)
    
    with tab2:
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.plotly_chart(fig3, use_container_width=True)
