import streamlit as st
import pandas as pd
import hashlib
from supabase import create_client

st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

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
        response = supabase.table('produtos').select('*').order('id').execute()
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar estoque: {e}")
        return pd.DataFrame()

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = None
    st.session_state['cargo'] = None

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
                
                if st.form_submit_button("Entrar"):
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


else:
    st.sidebar.title(f"Olá, {st.session_state['usuario']}")
    st.sidebar.caption(f"Cargo: {st.session_state['cargo']}")
    
    menu = st.sidebar.radio("Navegação", ["Dashboard", "Estoque", "Editar Produto"])
    
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

    st.title("📱 Sistema de Gestão de Estoque")

    if menu == "Dashboard":
        st.header("📊 Painel Gerencial")
        df = carregar_dados()
        if not df.empty:
            # Cálculos simples
            total_itens = df['quantidade'].sum()
            valor_estoque = (df['quantidade'] * df['preco_venda']).sum()
            
            c1, c2 = st.columns(2)
            c1.metric("📦 Total de Peças", total_itens)
            c2.metric("💰 Valor em Estoque", f"R$ {valor_estoque:,.2f}")
            
            st.bar_chart(df['marca'].value_counts())
        else:
            st.info("Sem dados para dashboard.")

    elif menu == "Estoque":
        st.header("📦 Gerenciamento de Estoque")

        if st.session_state['cargo'] == 'Admin': 
            with st.expander("➕ Cadastrar Novo Produto", expanded=False):
                
                # 1. CATEGORIA (FORA DO FORMULÁRIO para atualizar a tela)
                st.write("**O que vamos cadastrar?**")
                categoria_selecionada = st.pills(
                    "Selecione o tipo:", 
                    ["Tela", "Bateria", "Dock de Carga", "Tampa", "Outros"], 
                    selection_mode="single",
                    default="Tela"
                )

                # 2. O FORMULÁRIO
                with st.form("form_cadastro_dinamico", clear_on_submit=True):
                    st.write(f"Cadastrando: **{categoria_selecionada}**")
                    
                    c1, c2 = st.columns(2)
                    with c1: 
                        marca = st.pills("Marca *", ["Samsung", "Apple", "Motorola", "Xiaomi", "LG", "Outros"], selection_mode="single")
                    with c2: 
                        modelo = st.text_input("Modelo do Aparelho *", placeholder="Ex:")

                    c3, c4 = st.columns(2)
                
                    qualidade = None
                    aro = None

                    if categoria_selecionada == "Tela":
                        with c3:
                            qualidade = st.selectbox("Qualidade *", ["Original Nacional/China", "Retirada", "Incell", "OLED"])
                        with c4:
                            aro = st.pills("Aro *", ["Com aro", "Sem aro"], selection_mode="single")
                    
                    elif categoria_selecionada == "Bateria":
                        with c3:
                            qualidade = st.selectbox("Qualidade *", ["Original", "Primeira Linha", "Paralela"])
                        
                        # Bateria não tem aro, definimos valor automático
                        aro = "N/A"
                        with c4:
                            st.info("🔋 Baterias não possuem aro. (Automático)")
                    
                    else:
                        # Para Dock, Tampa e Outros
                        with c3:
                            qualidade = st.selectbox("Qualidade *", ["Original", "Paralela"])
                        aro = "N/A"
                        with c4:
                            st.info(f"🛠️ Item do tipo {categoria_selecionada}.")

      
                    st.write("**Financeiro**")
                    c5, c6, c7 = st.columns(3)
                    with c5:
                        custo = st.number_input("Custo (R$)", min_value=0.0, step=0.50)
                    with c6:
                        venda = st.number_input("Venda (R$)", min_value=0.0, step=0.50)
                    with c7:
                        qtd = st.number_input("Qtd *", min_value=1, step=1, value=1)

           
                    if st.form_submit_button("💾 Salvar Produto"):
                        erros = []
                        if not marca: erros.append("Marca")
                        if not modelo: erros.append("Modelo")
                        if not qualidade: erros.append("Qualidade")
                        
                        if not aro: erros.append("Aro")
                        
                        if len(erros) > 0:
                            st.error(f"❌ Preencha: {', '.join(erros)}")
                        else:
                            novo_prod = {
                                "categoria": categoria_selecionada, 
                                "marca": marca, "modelo": modelo, "aro": aro,
                                "qualidade": qualidade, "quantidade": qtd,
                                "preco_custo": custo, "preco_venda": venda
                            }
                            try:
                                supabase.table("produtos").insert(novo_prod).execute()
                                st.success(f"✅ {modelo} cadastrado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

        st.divider()

        # TABELA DE VISUALIZAÇÃO
        df_produtos = carregar_dados()
        
        if df_produtos.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            with st.expander("🔍 Filtros", expanded=True):
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    busca = st.text_input("Buscar Modelo")
                with col_f2:
                    filtro_aro = st.selectbox("Detalhe", ["Todos", "Com aro", "Sem aro", "N/A"])

            df_show = df_produtos.copy()
            if busca: df_show = df_show[df_show['modelo'].str.contains(busca, case=False)]
            if filtro_aro != "Todos": df_show = df_show[df_show['aro'] == filtro_aro]

            st.dataframe(
                df_show[['marca', 'modelo', 'qualidade', 'aro', 'preco_venda', 'quantidade']], 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "preco_venda": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "modelo": "Modelo",
                    "aro": "Detalhe",
                    "quantidade": st.column_config.NumberColumn("Qtd", format="%d")
                }
            )