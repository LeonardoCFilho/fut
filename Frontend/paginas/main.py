import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

#para boas qtds de dados é bom usar
cores = {
    'verde':'#008000',
    'vermelho':'#800000',
    'azul':'#4169E1'
    }

@st.cache_data
def carregar_dados():
    try:
        dados = pd.read_csv('dados_2.csv', parse_dates=['data'])
        return dados
    except FileNotFoundError:
        st.error("Arquivo 'dados.csv' não encontrado!")
        return pd.DataFrame(columns=['data', 'total', 'acertos', 'erros'])

dados = carregar_dados()

# titulo da pagina
st.title("Dashboard de Casos de Teste")

# barra lateral para filtrar data
st.sidebar.header("Filtros")
data_inicial = st.sidebar.date_input("Data Inicial", dados['data'].min())
data_final = st.sidebar.date_input("Data Final", dados['data'].max())


# filtrando os dados 
dados_filtrados = dados[
    (dados['data'] >= pd.to_datetime(data_inicial)) & 
    (dados['data'] <= pd.to_datetime(data_final))
]

# ********************************** #
st.title('Todas as Estatísticas')
# criando as 3 colunas iniciais
col1, col2, col3 = st.columns(3)
with col1:
    fig_totais = px.area(
        dados_filtrados,
        x='data',
        y='total',
        title='Testes Totais',
        color_discrete_sequence=[cores['azul']],
    )
    st.plotly_chart(fig_totais, use_container_width=True)
    st.metric("Total de Testes", dados_filtrados['total'].sum())

with col2:
    fig_acertos = px.area(
        dados_filtrados,
        x='data',
        y='acertos',
        title='Acertos Totais',
        color_discrete_sequence=[cores['verde']]
    )
    st.plotly_chart(fig_acertos, use_container_width=True)
    st.metric("Acertos", dados_filtrados['acertos'].sum())

with col3:
    fig_erros = px.area(
        dados_filtrados,
        x='data',
        y='erros',
        title='Erros Totais',
        color_discrete_sequence=[cores['vermelho']]
    )
    st.plotly_chart(fig_erros, use_container_width=True)
    st.metric("Erros", dados_filtrados['erros'].sum())

# *******************************

#declarando barras
chart_data = dados_filtrados[["total", "acertos", "erros"]]
st.bar_chart(chart_data, color=[cor for nome,cor in cores.items()])

###
fig_barras = px.bar(dados_filtrados, 
    x=dados_filtrados.index, 
    y=["total", "acertos", "erros"],
    barmode='group',
    title="Desempenho dos Testes",
    #"color_discrete_sequence= str([cores['azul'], [cores['verde']], [cores['vermelho']]]),
)
st.plotly_chart(fig_barras)

media_testes = dados_filtrados['total'].mean()

st.write(f"Média de testes por período: {media_testes:.2f}\n")

#tabela
st.subheader('Dados Filtrados')
st.dataframe(dados_filtrados)

# grafico de linha
st.subheader("Testes Executados por Período")
fig_linha = px.line(
    dados_filtrados, 
    x='data', 
    y='total', 
    markers=True,
    labels={'data': 'Data', 'total': 'Total de Testes'}
)
st.plotly_chart(fig_linha)

# grafico de Pizza 
st.subheader("Distribuição de Acertos vs. Erros")
totais = dados_filtrados['total'].sum()
acertos_total = dados_filtrados['acertos'].sum()
erros_total = dados_filtrados['erros'].sum()

fig_pizza = px.pie(
    names=['Acertos', 'Erros'],
    values=[acertos_total, erros_total],
    title='Taxa de Sucesso',
    color_discrete_sequence=[cores['verde'], cores['vermelho']]
)
st.plotly_chart(fig_pizza)






