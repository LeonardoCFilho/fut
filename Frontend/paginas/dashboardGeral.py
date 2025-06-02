import streamlit as st
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import os

def render():
    # Configuração da página (removendo menu lateral)
    #st.set_page_config(layout="wide", page_title="Dashboard FHIR Simplificado", page_icon="⚕️")
    
    # Esconder menu lateral
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    # Carregar dados do relatório
    @st.cache_data
    def load_report_data():
        # Ajuste o caminho conforme sua estrutura de pastas
        data_dir = Path(__file__).absolute().parent.parent.parent
        json_path = data_dir / "Arquivos" / "Testes" /"relatorio.json"
        
        if not json_path.exists():
            st.error(f"Arquivo não encontrado: {json_path}")
            return {}, {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_cases = {k: v for k, v in data.items() if k != "relatorio_final"}
            summary_stats = data.get("relatorio_final", {})
            return test_cases, summary_stats
            
        except Exception as e:
            st.error(f"Erro ao ler JSON: {str(e)}")
            return {}, {}

    # Função para criar gráficos
    def create_charts(summary_stats):
        # Gráfico 1: Distribuição de status
        status_data = {
            "Status": ["Válidos", "Inválidos", "YAML Inválidos"],
            "Quantidade": [
                summary_stats.get("numero_de_testes_validos", 0),
                summary_stats.get("numeros_de_testes_totais", 0) - summary_stats.get("numero_de_testes_validos", 0),
                sum(1 for test in test_cases.values() if test.get('yaml_valido') is False)
            ]
        }
        fig1 = px.pie(status_data, names="Status", values="Quantidade", 
                     title="Distribuição de Status dos Testes",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        
        # Gráfico 2: Tipos de Erros
        error_data = {
            "Tipo": ["Erros", "Warnings", "Fatais", "Informações"],
            "Quantidade": [
                summary_stats.get("quantidade_error_reais_totais", 0),
                summary_stats.get("quantidade_warning_reais_totais", 0),
                summary_stats.get("quantidade_fatal_reais_totais", 0),
                summary_stats.get("quantidade_information_reais_totais", 0)
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
                summary_stats.get("%_error_reais_acertados", 0)*100,
                summary_stats.get("%_warning_reais_acertados", 0)*100,
                summary_stats.get("%_fatal_reais_acertados", 0)*100,
                summary_stats.get("%_information_reais_acertados", 0)*100
            ]
        }
        fig3 = px.bar(accuracy_data, x="Tipo", y="Taxa (%)", 
                     title="Taxas de Acerto por Tipo de Validação",
                     range_y=[0, 100],
                     color="Tipo",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        
        return fig1, fig2, fig3

    # Carregar dados
    test_cases, summary_stats = load_report_data()
    
    if not test_cases:
        st.warning("Nenhum dado foi carregado. Verifique o caminho do arquivo.")
        return
    
    # Cabeçalho
    st.title("📊 Dashboard FHIR - Visão Geral")
    st.write(f"**Data do relatório:** {summary_stats.get('data', 'N/A')}")
    
    # Seção de Métricas Principais
    st.header("📈 Métricas Principais")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Testes", summary_stats.get("numeros_de_testes_totais", 0))
    col2.metric("Testes Válidos", 
               f"{summary_stats.get('numero_de_testes_validos', 0)} ({summary_stats.get('numero_de_testes_validos', 0)/summary_stats.get('numeros_de_testes_totais', 1):.0%})")
    col3.metric("Tempo Médio", f"{summary_stats.get('tempo_medio', 0):.1f} seg")
    col4.metric("YAML Inválidos", sum(1 for test in test_cases.values() if test.get('yaml_valido') is False))
    
    # Gráficos
    st.header("📊 Visualizações")
    fig1, fig2, fig3 = create_charts(summary_stats)
    
    tab1, tab2, tab3 = st.tabs(["Status dos Testes", "Distribuição de Erros", "Taxas de Acerto"])
    
    with tab1:
        st.plotly_chart(fig1, use_container_width=True)
    
    with tab2:
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.plotly_chart(fig3, use_container_width=True)
    
