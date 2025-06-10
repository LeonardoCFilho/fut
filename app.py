import sys
import os
from pathlib import Path
# caminho_raiz = Path(__file__).absolute().parent.parent.parent
# sys.path.append(str(caminho_raiz))

#from Backend.fachada_sistema import acharCaminhoProjeto
import streamlit as st
from Frontend.paginas import dashboard, formulario, configuracao, TestManager, dashboardGeral

st.set_page_config(page_title="Minha Aplicação", page_icon="🧪", layout="wide")



# Barra lateral de navegação
pagina = st.sidebar.selectbox(
    "Escolha a página",
    ["📊 Dashboard","🎲 Dados Gerais", "🧱 Test Manager", "📋 Teste Manual", "⚙️ Configuração"]
)

# Chama a função render de acordo com a escolha do usuário
if pagina == "📊 Dashboard":
    dashboard.render()
elif pagina == "🎲 Dados Gerais":
    dashboardGeral.render()
elif pagina == "🧱 Test Manager":
    TestManager.render()
elif pagina == "📋 Teste Manual":
    formulario.render()
elif pagina == "⚙️ Configuração":
    configuracao.render()
