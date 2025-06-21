import streamlit as st
from Backend.fachada_sistema import FachadaSistema
import logging

# Configura o logger
logger = logging.getLogger(__name__)

#cache p/ otimizar o codigo
@st.cache_resource
def inicializar_sistema():
    """Tenta inicializar e retorna a instância da FachadaSistema."""
    try:
        return FachadaSistema()
    except Exception as e:
        logger.error(f"Erro ao instanciar FachadaSistema: {e}")
        return None

@st.cache_data
def carregar_configuracoes(_fachada):
    """
    Carrega todas as configurações usando a fachada.
    Retorna um dicionário com as configurações ou valores padrão.
    """
    config = {}
    try:
        # padrão `or <default>` para lidar com valores ausentes.
        
        try:
            # Usa o valor do .ini como fallback primário
            valor_timeout = _fachada.obter_configuracao("requests_timeout") or "120"
            config['timeout'] = int(valor_timeout)
        except (ValueError, TypeError):
            config['timeout'] = 120 # Fallback final

        try:
            valor_threads = _fachada.obter_configuracao("max_threads") or "8"
            config['max_threads'] = int(valor_threads)
        except (ValueError, TypeError):
            config['max_threads'] = 8
            
        # O padrão para strings/booleanos já estava correto
        armazenar_str = _fachada.obter_configuracao("armazenar_saida_validator") or "False"
        config['armazenar_saida'] = armazenar_str.lower() in ["true", "1", "yes"]
        
        config['path_validator'] = _fachada.obter_configuracao("caminho_validator") or "default"
        
        return config

    except Exception as e:
        # Este erro agora só deve acontecer se a própria fachada falhar de forma inesperada.
        st.error(f"Erro geral ao carregar as configurações: {e}")
        logger.error(f"Falha ao chamar obter_configuracao: {e}")
        # Retorna um dicionário de fallback completo se a comunicação com a fachada falhar
        return {
            'timeout': 120,
            'max_threads': 8,
            'armazenar_saida': False,
            'path_validator': "default"
        }

def salvar_configuracoes(_fachada, novas_configs):
    """
    Salva as novas configurações usando a fachada e reporta o resultado.
    """
    sucesso = True
    erros = []

    for chave, valor in novas_configs.items():
        try:
            if not _fachada.atualizar_configuracao(chave, str(valor)):
                sucesso = False
                erros.append(f"Falha ao salvar '{chave}'.")
        except Exception as e:
            sucesso = False
            erros.append(f"Erro ao salvar '{chave}': {e}")
            logger.error(f"Erro ao chamar atualizar_configuracao para {chave}: {e}")

    if sucesso:
        st.success('Configurações salvas com sucesso!')
        st.toast('✅ Suas preferências foram atualizadas.')
        carregar_configuracoes.clear()
    else:
        st.error("Ocorreram erros ao salvar algumas configurações:")
        for erro in erros:
            st.write(f"- {erro}")

# --- Função Principal de Renderização da Página ---

def render():
    st.title("⚙️ Configuração dos Testes")
    st.caption("Altere os parâmetros de execução dos testes de validação FHIR.")

    fachada = inicializar_sistema()
    if fachada is None:
        st.error("Não foi possível inicializar o sistema de configuração.")
        st.info("Verifique se o programa está sendo executado a partir do diretório correto e se o arquivo de configuração existe.")
        return

    configs_atuais = carregar_configuracoes(fachada)

    # --- WIDGETS DA INTERFACE ---

    st.subheader("Validador FHIR")
    
    path_validator_default = configs_atuais.get('path_validator', "")
    is_custom_validator = path_validator_default and path_validator_default.lower() != "default"
    validator_index = 1 if is_custom_validator else 0
    
    validador_selecionado = st.selectbox(
        "Escolha o validador a ser utilizado:", 
        ("Padrão (Incluso no sistema)", "Customizado (Executável local)"),
        index=validator_index
    )

    caminho_validator_input = ""
    if validador_selecionado == "Customizado (Executável local)":
        caminho_validator_input = st.text_input(
            "Caminho do executável do validador customizado:",
            value=path_validator_default if is_custom_validator else ""
        )
    
    armazenar_saida_validator = st.checkbox(
        "Armazenar saída completa do Validator a cada execução",
        value=configs_atuais.get('armazenar_saida', False)
    )

    st.divider()

    st.subheader("Desempenho e Rede")
    max_threads = st.number_input(
        "Número máximo de threads (testes em paralelo):",
        min_value=1, max_value=50,
        value=configs_atuais.get('max_threads', 8)
    )

    timeout = st.number_input(
        "Timeout das requisições (segundos):",
        min_value=1, max_value=600,
        value=configs_atuais.get('timeout', 120),
        help="Tempo máximo que o sistema aguardará por uma resposta de um servidor externo."
    )

    st.divider()
    
    if st.button("Salvar Configurações", type="primary", use_container_width=True):
        
        if validador_selecionado == "Customizado (Executável local)":
            valor_caminho_validator = caminho_validator_input.strip() if caminho_validator_input.strip() else "default"
        else:
            valor_caminho_validator = "default"
            
        configuracoes_para_salvar = {
            "caminho_validator": valor_caminho_validator,
            "armazenar_saida_validator": armazenar_saida_validator,
            "max_threads": max_threads,
            "requests_timeout": timeout,
        }
        
        salvar_configuracoes(fachada, configuracoes_para_salvar)