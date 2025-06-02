import streamlit as st
import json
from pathlib import Path
import pandas as pd
import os

def render():
    # Carregar dados do relatório
    @st.cache_data
    def load_report_data():
        # Caminho absoluto para a pasta de dados
        data_dir = Path(__file__).absolute().parent.parent.parent
        json_path = data_dir / "Arquivos" / "Testes" /"relatorio.json"
        
        # Verificação robusta do arquivo
        if not json_path.exists():
            st.error(f"Arquivo não encontrado no caminho: {json_path}")
            st.error("Por favor, verifique:")
            st.error(f"1. Se o arquivo existe em {data_dir}")
            st.error(f"2. Se o nome do arquivo está correto (incluindo maiúsculas/minúsculas)")
            st.error(f"3. Conteúdo do diretório: {os.listdir(data_dir)}")
            return {}, {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Separar os casos de teste das estatísticas consolidadas
            test_cases = {k: v for k, v in data.items() if k != "relatorio_final"}
            summary_stats = data.get("relatorio_final", {})
            
            return test_cases, summary_stats
            
        except Exception as e:
            st.error(f"Erro ao ler o arquivo JSON: {str(e)}")
            return {}, {}

    # Função para exibir o relatório no formato Streamlit
    def show_streamlit_report(test_cases, summary_stats):
        st.title("📊 Relatório de Validação FHIR")
        st.caption("Visualização nativa do Streamlit")
        
        # Métricas resumidas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Testes", summary_stats.get("numeros_de_testes_totais", 0))
        col2.metric("Válidos", summary_stats.get("numero_de_testes_validos", 0), 
                   f"{summary_stats.get('numero_de_testes_validos', 0)/summary_stats.get('numeros_de_testes_totais', 1):.0%}")
        col3.metric("Inválidos", 
                   summary_stats.get("numeros_de_testes_totais", 0) - summary_stats.get("numero_de_testes_validos", 0),
                   f"{(summary_stats.get('numeros_de_testes_totais', 0) - summary_stats.get('numero_de_testes_validos', 0))/summary_stats.get('numeros_de_testes_totais', 1):.0%}")
        
        # Contar YAMLs inválidos
        invalid_yaml = sum(1 for test in test_cases.values() if test.get('yaml_valido') is False)
        col4.metric("YAML Inválidos", invalid_yaml)
        
        # Métricas adicionais de performance
        st.divider()
        st.subheader("📈 Estatísticas de Performance")
        
        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
        perf_col1.metric("Tempo Total (segundos)", summary_stats.get("tempo_total", 0))
        perf_col2.metric("Tempo Médio por Teste (segundos)", f"{summary_stats.get('tempo_medio', 0):.1f}")
        perf_col3.metric("Data da Execução", summary_stats.get("data", "N/A"))
        
        st.divider()
        st.subheader("📊 Estatísticas de Erros")
        
        error_col1, error_col2, error_col3, error_col4 = st.columns(4)
        error_col1.metric("Erros Totais", summary_stats.get("quantidade_error_reais_totais", 0))
        error_col2.metric("Warnings Totais", summary_stats.get("quantidade_warning_reais_totais", 0))
        error_col3.metric("Fatais Totais", summary_stats.get("quantidade_fatal_reais_totais", 0))
        error_col4.metric("Informações Totais", summary_stats.get("quantidade_information_reais_totais", 0))
        
        st.divider()
        st.subheader("🎯 Taxas de Acerto")
        
        accuracy_col1, accuracy_col2, accuracy_col3, accuracy_col4 = st.columns(4)
        accuracy_col1.metric("Acerto em Erros", f"{summary_stats.get('%_error_reais_acertados', 0)*100:.1f}%")
        accuracy_col2.metric("Acerto em Warnings", f"{summary_stats.get('%_warning_reais_acertados', 0)*100:.1f}%")
        accuracy_col3.metric("Acerto em Fatais", f"{summary_stats.get('%_fatal_reais_acertados', 0)*100:.1f}%")
        accuracy_col4.metric("Acerto em Informações", f"{summary_stats.get('%_information_reais_acertados', 0)*100:.1f}%")
        
        st.divider()
        
        # Visualização detalhada dos testes
        st.subheader("🧪 Detalhes dos Casos de Teste")
        for test_name, test_data in test_cases.items():
            with st.expander(f"{test_name}", expanded=False):
                # Status principal
                if not test_data.get('yaml_valido'):
                    st.error("YAML inválido")
                    st.write(f"**Motivo:** {test_data.get('motivo_da_invalidez', 'Não especificado')}")
                elif test_data.get('status'):
                    st.success("Validação bem-sucedida")
                else:
                    st.error("Validação falhou")
                    st.write(f"**Motivo:** {test_data.get('motivo_da_invalidez', 'Não especificado')}")
                
                # Detalhes do teste
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.write("**Status Esperado:**", test_data.get('status_esperado', 'N/A'))
                    st.write("**Status Real:**", test_data.get('status_real', 'N/A'))
                    
                    if test_data.get('tempo_de_execucao'):
                        st.write(f"⏱️ **Tempo de execução:** {test_data['tempo_de_execucao']}ms")
                
                with col_right:
                    if test_data.get('correspondencia'):
                        st.write("**Problemas de Correspondência:**")
                        for issue in test_data['correspondencia']:
                            st.error(f"- {issue.get('issue')}: {issue.get('mensagem', 'Sem detalhes')}")
                    
                    if test_data.get('discordancia'):
                        discord = test_data['discordancia']
                        if discord.get('issue_esperada_ausente_no_real'):
                            st.write("**Issues esperadas ausentes:**")
                            for issue in discord['issue_esperada_ausente_no_real']:
                                st.warning(f"- {issue}")
                        
                        if discord.get('issue_real_ausente_na_esperada'):
                            st.write("**Issues reais ausentes:**")
                            for issue in discord['issue_real_ausente_na_esperada']:
                                st.warning(f"- {issue}")

    # Função para exibir o relatório HTML
    def show_html_report(test_cases, summary_stats):
        st.title("🎨 Relatório de Validação FHIR")
        st.caption("Visualização customizada em HTML")
        
        # Carregar template HTML (caminho relativo ao dashboard.py)
        html_path = Path(__file__).parent.parent / "templates" / "index.html"
        html_content = html_path.read_text(encoding='utf-8')
        
        # Preparar dados para o HTML
        report_data = {
            "test_cases": test_cases,
            "summary_stats": summary_stats
        }
        
        # Substituir os dados
        html_content = html_content.replace(
            'const reportData = {};',
            f'const reportData = {json.dumps(report_data)};'
        )
        
        # Exibir o relatório
        st.components.v1.html(html_content, height=1000, scrolling=True)

    # Configuração da página
    st.sidebar.title("⚙️ Configurações")
    view_mode = st.sidebar.radio(
        "Modo de Visualização",
        ("Streamlit", "HTML Customizado"),
        index=0
    )
    
    st.sidebar.divider()
    st.sidebar.info("Selecione o modo de visualização preferido.")
    
    # Carregar dados
    test_cases, summary_stats = load_report_data()
    
    # Exibir relatório no modo selecionado
    if view_mode == "Streamlit":
        show_streamlit_report(test_cases, summary_stats)
    else:
        show_html_report(test_cases, summary_stats)

