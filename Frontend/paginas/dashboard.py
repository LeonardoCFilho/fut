import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

def carregar_relatorio(caminho:str) -> dict | None:
    if caminho and os.path.exists(caminho):    
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return dados
        except Exception as e:
            st.error(f'Erro ao ler arquivo json {e}')
            return None


def preparar_dataframe(dados_json):
    registros = []
    for arquivo, conteudo in dados_json.items():
        registros.append({
            'arquivo': arquivo,
            'yaml_valido': conteudo.get('yaml_valido', False),
            'status': conteudo.get('status', False),
            'tempo_execucao': conteudo.get('tempo_de_execucao'),
            'status_real': conteudo.get('status_real'),
            'status_esperado': conteudo.get('status_esperado'),
            'total_correspondencias': len(conteudo.get('correspondencia', [])),
            'esperada_ausente': len(conteudo.get('discordancia', {}).get('issue_esperada_ausente_no_real', [])),
            'real_ausente': len(conteudo.get('discordancia', {}).get('issue_real_ausente_na_esperada', [])),
        })
    return pd.DataFrame(registros)


def render():
    st.title("Dashboard do Relatório FHIR")
    try:
        caminho = r'C:\Users\DD\Desktop\Projetos\novo_streamlit\dados\relatorio.json'
        dados_json = carregar_relatorio(caminho)
        st.success("✅ Arquivo carregado com sucesso!")
        
    except:
        st.warning("⚠️ Nenhum arquivo carregado. Por favor, envie um arquivo JSON.")
        # caminho = st.file_uploader('Escolha um arquivo json', type='json')
        # dados_json = carregar_relatorio(caminho)
        # ...
    if dados_json:
        df = preparar_dataframe(dados_json)
        st.subheader("Tabela de Resultados")
        st.dataframe(df)

        st.subheader("Gráfico Pizza de Validade do YAML")
        yaml_counts = df['yaml_valido'].value_counts().rename({True: 'Válido', False: 'Inválido'})
        fig_yaml = px.pie(values=yaml_counts.values, names=yaml_counts.index, title='Validade dos Arquivos YAML')
        st.plotly_chart(fig_yaml)

        #***********************************
        st.subheader("Comparativo entre Status Esperado e Real")

        # Filtra colunas e remove nulos
        status_df = df[['status_real', 'status_esperado']].dropna()

        # Contagem dos status
        esperado_counts = status_df['status_esperado'].value_counts()
        real_counts = status_df['status_real'].value_counts()

        # DataFrame para gráfico de barras
        comparativo_df = pd.DataFrame({
            'Esperado': esperado_counts,
            'Real': real_counts
        }).fillna(0).reset_index().rename(columns={'index': 'Status'})

        # Layout com duas colunas
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Gráfico de Barras")
            fig_bar = px.bar(
                comparativo_df.melt(id_vars='Status', value_vars=['Esperado', 'Real']),
                x='Status',
                y='value',
                color='variable',
                barmode='group',
                title='Status Esperado vs Real',
                labels={'value': 'Quantidade', 'variable': 'Tipo'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.markdown("#### Gráfico Circular (Donut) do Status Real")
            
            # Ajusta as colunas corretamente
            real_df = real_counts.reset_index()
            real_df.columns = ['status', 'quantidade']

            fig_donut = px.pie(
                real_df,
                names='status',
                values='quantidade',
                hole=0.4,  # transforma em donut
                title='Distribuição dos Status Reais',
                labels={'status': 'Status', 'quantidade': 'Quantidade'}
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        #**************************************

        st.subheader("Erros de Correspondência")
        fig_erro = px.bar(
            df,
            x='arquivo',
            y=['esperada_ausente', 'real_ausente'],
            title='Quantidade de Issues Ausentes',
            labels={'value': 'Qtd de Issues', 'arquivo': 'Arquivo'},
            barmode='group'
        )
        st.plotly_chart(fig_erro)

        st.subheader("Tempo de Execução")
        df_tempo = df.dropna(subset=['tempo_execucao'])
        fig_tempo = px.bar(
            df_tempo,
            x='arquivo',
            y='tempo_execucao',
            title='Tempo de Execução por Arquivo (ms)'
        )
        st.plotly_chart(fig_tempo)
