import streamlit as st
import sqlite3
import pandas as pd
import hashlib

st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

def login (usuario, senha):
    conn = sqlite3.connect('Sistema_de_estoque.db')
    cursor = conn.cursor()

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    cursor.execute("SELECT cargo FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_hash))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:   
        return resultado[0]
    return None

def carregar_dados():
    conn = sqlite3.connect('Sistema_de_estoque.db')
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = None
    st.session_state['cargo'] = None

if not st.session_state['logado']:
    
    st.title("Acesso Restrito - SGE")
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
                    st.success("Login realizado! Carregando...")
                    st.rerun() 
                else:
                    st.error("Usuário ou senha incorretos.")

else:
    # === TELA DO SISTEMA (SÓ APARECE SE ESTIVER LOGADO) ===
    
    # Menu Lateral
    st.sidebar.title(f"Olá, {st.session_state['usuario']}")
    st.sidebar.caption(f"Cargo: {st.session_state['cargo']}")
    
    menu = st.sidebar.selectbox("Navegação", ["Estoque", "Adicionar Produto", "Serviços"])
    
    # Botão de Sair (Logout)
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

    st.title("📱 Sistema de Gestão de Estoque")

    # --- ABA: ESTOQUE ---
    if menu == "Estoque":
        st.header("📦 Estoque Atual")
        df_produtos = carregar_dados()
        
        if df_produtos.empty:
            st.warning("Nenhum produto cadastrado ainda.")
        else:
            st.dataframe(df_produtos, use_container_width=True)
            total_pecas = df_produtos['quantidade'].sum()
            st.info(f"Total de peças no sistema: {total_pecas}")

    # --- ABA: ADICIONAR PRODUTO ---
    elif menu == "Adicionar Produto":
        # Verificação de Cargo: Só ADMIN pode ver essa tela
        if st.session_state['cargo'] == 'admin':
            st.header("📦 Cadastrar Nova Peça")
            
            with st.form("form_cadastro_produto", clear_on_submit=True):
                st.write("### Dados do Produto")
                c1, c2 = st.columns(2)
                with c1:
                    marca = st.selectbox("Marca", ["Samsung", "Apple", "Motorola", "Xiaomi", "LG"])
                with c2:
                    modelo = st.text_input("Modelo (Ex: A51, iPhone 11)")

                c3, c4 = st.columns(2)
                with c3:
                    qualidade = st.selectbox("Qualidade", ["Original Importada", "Original Retirada", "Incell", "OLED"])
                with c4:
                    cor = st.text_input("Cor")

                st.write("### Valores e Estoque")
                c5, c6, c7 = st.columns(3)
                with c5:
                    preco_custo = st.number_input("Custo (R$)", step=0.50)
                with c6:
                    preco_venda = st.number_input("Venda (R$)", step=0.50)
                with c7:
                    quantidade = st.number_input("Qtd", min_value=1, step=1)

                if st.form_submit_button("💾 Salvar no Estoque"):
                     st.success("Simulação: Produto Salvo!")
                     # Aqui entra o INSERT no banco depois
        
        else:
            # Se for o CHEFE (Visualizador) tentando entrar aqui:
            st.error("🚫 Acesso Negado: Apenas administradores podem cadastrar produtos.")

    # --- ABA: SERVIÇOS ---
    elif menu == "Serviços":
        st.header("🛠️ Ordem de Serviço")
        st.write("Em breve...")