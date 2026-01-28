import streamlit as st
import pandas as pd
import hashlib
from supabase import create_client

# Configuração da Página
st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

# Conexão com o Supabase
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar no Supabase: {e}")
        st.stop()

supabase = init_connection()

# Funções

def login(usuario, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    try:
        response = supabase.table('usuarios').select('cargo, senha').eq('usuario', usuario).execute()
        if len(response.data) > 0:
            usuario_encontrado = response.data[0]
            if usuario_encontrado['senha'] == senha_hash:
                return usuario_encontrado['cargo']
        
        return None
    except Exception as e:
        st.error(f"Erro no login: {e}")
        return None

def carregar_dados():
    try:
        response = supabase.table('produtos').select('*').execute()
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar estoque: {e}")
        return pd.DataFrame()

# Função Login
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = None
    st.session_state['cargo'] = None

# Tela de Login
if not st.session_state['logado']:

    login_placeholder = st.empty()

    with login_placeholder.container():
        st.title("Acesso Restrito - SGE (Nuvem ☁️)")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form"):
                st.write("Entre com suas credenciais:")
                usuario_input = st.text_input("Usuário")
                senha_input = st.text_input("Senha", type="password")
                
                botao_entrar = st.form_submit_button("Entrar")
                
                if botao_entrar:
                    cargo_encontrado = login(usuario_input, senha_input)
                    
                    if cargo_encontrado:
                        st.session_state['logado'] = True
                        st.session_state['usuario'] = usuario_input
                        st.session_state['cargo'] = cargo_encontrado
                    
                        login_placeholder.empty() 
                        
                        st.success("Login realizado!")
                        st.rerun() 
                    else:
                        st.error("Usuário ou senha incorretos.")
# Tela do Sistema
else:
    # Menu Lateral
    st.sidebar.title(f"Olá, {st.session_state['usuario']}")
    st.sidebar.caption(f"Cargo: {st.session_state['cargo']}")
    
    menu = st.sidebar.radio("Navegação", ["Serviços", "Estoque", "Adicionar Produto"])
    
    # Botão de Sair 
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

    st.title("📱 Sistema de Gestão de Estoque")

   
    # ABA: Serviços
    if menu == "Serviços":
        st.header("🛠️ Ordem de Serviço")
        st.write("Em breve...")

    # ABA: Estoque
    elif menu == "Estoque":
        st.header("📦 Estoque Atual")

        df_produtos = carregar_dados()
        
        if df_produtos.empty:
            st.warning("Nenhum produto cadastrado ainda.")
        else:
            st.dataframe(df_produtos, use_container_width=True)
            if 'quantidade' in df_produtos.columns:
                total_pecas = df_produtos['quantidade'].sum()
                st.info(f"Total de peças no sistema: {total_pecas}")

    # ABA: Adicionar Produto
    elif menu == "Adicionar Produto":
        if st.session_state['cargo'] == 'admin':
            st.header("📦 Cadastrar Nova Peça")
            
            with st.form("form_cadastro_produto", clear_on_submit=True):
                st.write("### Dados do Produto")
                c1, c2 = st.columns(2)
                with c1:
                    marca = st.pills("Marca", ["Samsung", "Apple", "Motorola", "Xiaomi", "LG"])
                with c2:
                    modelo = st.text_input("Modelo (Ex: A51, iPhone 11)")

                c3, c4 = st.columns(2)
                with c3:
                    qualidade = st.pills("Qualidade", ["Original Importada", "Original Retirada", "Incell", "OLED"])
                with c4:
                    cor = st.text_input("Cor (opcional)")

                st.write("### Valores e Estoque")
                c5, c6, c7 = st.columns(3)
                with c5:
                    preco_custo = st.number_input("Custo (R$)", step=0.50)
                with c6:
                    preco_venda = st.number_input("Venda (R$)", step=0.50)
                with c7:
                    quantidade = st.number_input("Qtd", min_value=1, step=1)

                if st.form_submit_button("💾 Salvar no Estoque"):
                    novo_produto = {
                        "marca": marca,
                        "modelo": modelo,
                        "qualidade": qualidade,
                        "cor": cor,
                        "preco_custo": preco_custo,
                        "preco_venda": preco_venda,
                        "quantidade": quantidade
                    }
                    
                    try:
                        supabase.table("produtos").insert(novo_produto).execute()
                        st.success("Produto cadastrado na nuvem com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
        
        else:
            st.error("🚫 Acesso Negado: Apenas administradores podem cadastrar produtos.")