import streamlit as st
import pandas as pd
import hashlib
from supabase import create_client

st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

# Conexão com banco de dados
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

# Login 
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

# Carregar dados do estoque
def carregar_dados():
    try:
        response = supabase.table('produtos').select('*').order('id').execute()
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar estoque: {e}")
        return pd.DataFrame()

# Inicialização da sessão para controle de login
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

# Interface principal após login
else:
    st.sidebar.title(f"Olá, {st.session_state['usuario']}")
    st.sidebar.caption(f"Cargo: {st.session_state['cargo']}")
    
    menu = st.sidebar.radio("Navegação", ["Dashboard", "Ordem de Serviço", "Estoque"])
    
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

    st.title("📱 Sistema de Gestão de Estoque")

    # Dashboard 
    if menu == "Dashboard":
        st.header("📊 Painel Gerencial")
        df_produtos = carregar_dados()
        if not df_produtos.empty:
            total_itens = df_produtos['quantidade'].sum()
            valor_estoque = (df_produtos['quantidade'] * df_produtos['preco_venda']).sum()
            
            c1, c2 = st.columns(2)
            c1.metric("📦 Total de Peças", total_itens)
            c2.metric("💰 Valor em Estoque", f"R$ {valor_estoque:,.2f}")
            
            st.bar_chart(df_produtos['marca'].value_counts())
        else:
            st.info("Sem dados para dashboard.")

    #Ordem de serviço
    elif menu == "Ordem de Serviço":
        st.header("🔧 Controle de Ordens de Serviço")
        try:
            response = supabase.table('servicos').select('*').order('id', desc=True).execute()
            df_os = pd.DataFrame(response.data)
        except Exception as e:
            st.error(f"Erro ao carregar OS: {e}")
            df_os = pd.DataFrame()

        col_esq, col_dir = st.columns([1.5, 1])

        with col_esq:
            st.subheader("📋 Na Bancada")
            
            if df_os.empty:
                st.info("Nenhuma O.S. registrada.")
            else:
                status_filter = st.pills("Filtrar Status:", ["Aberto", "Em Andamento", "Pronto", "Entregue", "Todos"], selection_mode="single", default="Aberto")
                
                if status_filter != "Todos":
                    df_view = df_os[df_os['status'] == status_filter]
                else:
                    df_view = df_os

                for index, row in df_view.iterrows():
                    icone = "🔴" if row['status'] == "Aberto" else "🟡" if row['status'] == "Em Andamento" else "🟢"
                    
                    with st.expander(f"{icone} {row['id']} - {row['aparelho_modelo']} ({row['cliente_nome']})"):
                        st.write(f"**Defeito:** {row['defeito_relatado']}")
                        st.write(f"**Senha:** {row['aparelho_senha']}")
                        st.caption(f"Entrada: {str(row['data_entrada'])[:10]}")
                        
                        if st.button("🛠️ Gerenciar", key=f"btn_os_{row['id']}"):
                            st.session_state['os_selecionada'] = row.to_dict()
                            st.rerun()
                            
        with col_dir:
            
            os_atual = st.session_state.get('os_selecionada')

            if os_atual:
                st.subheader(f"✏️ Editando OS #{os_atual['id']}")
                
                # 1. ESCOLHA FORA DO FORM
                tipo_senha_edit = st.pills(
                    "Alterar Tipo de Bloqueio:", 
                    ["Padrão (Desenho)", "PIN / Senha"], 
                    selection_mode="single", 
                    default="Padrão (Desenho)"
                )
                
                # 2. O FORMULÁRIO DE EDIÇÃO
                with st.form("form_editar_os"):
                    st.write("**Dados do Cliente (Editáveis)**")
                    c_cli1, c_cli2 = st.columns(2)
                    with c_cli1:
                        novo_nome = st.text_input("Nome", value=os_atual['cliente_nome'])
                    with c_cli2:
                        novo_contato = st.text_input("Contato", value=os_atual.get('cliente_contato', ''))

                    st.write("**Dados do Aparelho**")
                    novo_modelo = st.text_input("Modelo", value=os_atual['aparelho_modelo'])
                    novo_defeito = st.text_area("Defeito Relatado", value=os_atual['defeito_relatado'])

                    # Lógica da Senha (Mantida)
                    nova_senha = os_atual.get('aparelho_senha', '') 
                    
                    if tipo_senha_edit == "Padrão (Desenho)":
                         c_s1, c_s2 = st.columns([3, 1])
                         with c_s1:
                             nova_senha = st.text_input("Senha", value=os_atual.get('aparelho_senha', ''))
                         with st.popover("🔢 Ver Mapa"):
                                    st.markdown("""
                                    **Imagine as bolinhas numeradas:**
                                    
                                    1️⃣  —  2️⃣  —  3️⃣
                                    
                                    4️⃣  —  5️⃣  —  6️⃣
                                    
                                    7️⃣  —  8️⃣  —  9️⃣
                                    
                                    ---
                                    **Exemplos Comuns:**
                                    * **L:** 1-4-7-8
                                    * **Z:** 1-2-3-5-7-8-9
                                    * **Quadrado:** 1-2-5-4
                                    """) 
                    else: 
                         nova_senha = st.text_input("Nova Senha / PIN")

                    st.divider()
                    
                    lista_status = ["Aberto", "Em Andamento", "Pronto", "Entregue"]
                    status_atual_banco = os_atual.get('status', 'Aberto')
                    default_status = status_atual_banco if status_atual_banco in lista_status else "Aberto"
                    novo_status = st.pills("Status Atual", lista_status, selection_mode="single", default=default_status)

                    servico = st.text_area("Serviço Realizado", value=os_atual.get('servico_feito', '') or "")
                    valor = st.number_input("Valor Total (R$)", value=float(os_atual.get('valor_total', 0.0) or 0.0), step=10.0)

                    c_save, c_close = st.columns(2)
                    
                    with c_save:
                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                            supabase.table("servicos").update({
                                "cliente_nome": novo_nome,
                                "cliente_contato": novo_contato,
                                "aparelho_modelo": novo_modelo,
                                "defeito_relatado": novo_defeito,
                                "aparelho_senha": nova_senha,
                                "status": novo_status,
                                "servico_feito": servico,
                                "valor_total": valor
                            }).eq("id", os_atual['id']).execute()
                            
                            st.success("OS Atualizada!")
                            del st.session_state['os_selecionada']
                            st.rerun()
                    
                    with c_close:
                        if st.form_submit_button("❌ Fechar", use_container_width=True):
                            del st.session_state['os_selecionada']
                            st.rerun()

                    st.divider() 
                    
                    c_check, c_del = st.columns([3, 2]) 
                    with c_check:
                        st.write("") 
                        confirmar = st.checkbox("Confirmar exclusão", key="check_del")
                        
                    with c_del:
                        if st.form_submit_button("🗑️ Excluir", use_container_width=True):
                            if confirmar:
                                try:
                                    supabase.table("servicos").delete().eq("id", os_atual['id']).execute()
                                    st.success("OS apagada.")
                                    del st.session_state['os_selecionada']
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                            else:
                                st.warning("Marque a caixa ao lado!")
                                        
            else:
                with st.expander("➕ Nova Ordem de Serviço", expanded=False):
                    
                    st.write("**Segurança do Aparelho**")
                    tipo_senha = st.pills(
                        "Tipo de Bloqueio:", 
                        ["Padrão (Desenho)", "PIN / Senha"], 
                        selection_mode="single", 
                        default="Padrão (Desenho)"
                    )

                    with st.form("form_nova_os", clear_on_submit=True):
                        st.write("**Dados do Cliente**")
                        nome = st.text_input("Nome *")
                        contato = st.text_input("Contato")
                        
                        st.write("**Dados do Aparelho**")
                        modelo = st.text_input("Modelo *", placeholder="Ex: iPhone 11")
                        
                        senha = ""
                        if tipo_senha == "Padrão (Desenho)":
                            c_pass1, c_pass2 = st.columns([3, 1])
                            with c_pass1:
                                senha = st.text_input("Senha", placeholder="Ex: 1-4-7-8 (L)")
                            with c_pass2:
                                st.write("") 
                                st.write("")
                                with st.popover("🔢 Ver Mapa"):
                                    st.markdown("""
                                    **Imagine as bolinhas numeradas:**
                                    
                                    1️⃣  —  2️⃣  —  3️⃣
                                    
                                    4️⃣  —  5️⃣  —  6️⃣
                                    
                                    7️⃣  —  8️⃣  —  9️⃣
                                    
                                    ---
                                    **Exemplos Comuns:**
                                    * **L:** 1-4-7-8
                                    * **Z:** 1-2-3-5-7-8-9
                                    * **Quadrado:** 1-2-5-4
                                    """)
                        else:
                            senha = st.text_input("Senha / PIN", placeholder="Ex: 123456")

                        defeito = st.text_area("Defeito Relatado *")
                        
                        if st.form_submit_button("🚀 Abrir O.S."):
                            if not nome or not modelo or not defeito:
                                st.error("Preencha obrigatórios (*)")
                            else:
                                nova_os = {
                                    "cliente_nome": nome,
                                    "cliente_contato": contato,
                                    "aparelho_modelo": modelo,
                                    "aparelho_senha": senha,
                                    "defeito_relatado": defeito,
                                    "status": "Aberto",
                                    "valor_total": 0.0
                                }
                                try:
                                    supabase.table("servicos").insert(nova_os).execute()
                                    st.success("OS Aberta!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
    # Estoque
    elif menu == "Estoque":
        st.header("📦 Gerenciamento de Estoque")
        df_produtos = carregar_dados()
        if df_produtos.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            busca = st.text_input("🔎 Buscar Modelo", placeholder="Digite o modelo para pesquisar...")
    
            df_show = df_produtos.copy()
            
            if busca: 
                df_show = df_show[df_show['modelo'].str.contains(busca, case=False)]

            st.write(f"**Resultados:** {len(df_show)} itens encontrados.")
            
            st.dataframe(
                df_show[['id', 'categoria', 'modelo', 'preco_venda', 'quantidade']], 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "preco_venda": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "modelo": "Modelo",
                    "quantidade": st.column_config.NumberColumn("Qtd", format="%d")
                }
            )

            # Edição de Produtos (Apenas para Admin)
            if st.session_state['cargo'] == 'Admin': 
                with st.expander("✏️ Editar Produto Existente", expanded=False):
                    
                    if df_produtos.empty or df_show.empty:
                        st.warning("Selecione ou busque um produto acima para editar.")
                    else:
                        df_show['label_edicao'] = df_show['id'].astype(str) + " - " + df_show['modelo']
                        escolha_edicao = st.selectbox("Escolha o produto:", df_show['label_edicao'].unique())
                        
                        if escolha_edicao:
                            id_editar = int(escolha_edicao.split(" - ")[0])
                            item_atual = df_produtos[df_produtos['id'] == id_editar].iloc[0]

                            with st.form("form_editar_produto"):
                                st.write(f"Editando: **{item_atual['modelo']}** ({item_atual.get('categoria', 'Geral')})")

                                c1, c2 = st.columns(2)
                                with c1:
                                    lista_marcas = ["Samsung", "Apple", "Motorola", "Xiaomi", "LG", "Outros"]
                                    val_marca = item_atual['marca'] if item_atual['marca'] in lista_marcas else None
                                    nova_marca = st.pills("Marca", lista_marcas, selection_mode="single", default=val_marca)
                                    
                                with c2:
                                    novo_modelo = st.text_input("Modelo / Descrição", value=item_atual['modelo'])
                                cat_atual = item_atual.get('categoria', 'Tela')
                                
                                if cat_atual == "Tela":
                                    lista_qual = ["Original Nacional/China", "Retirada", "Incell", "OLED"]
                                elif cat_atual == "Bateria":
                                    lista_qual = ["Original", "Primeira Linha", "Paralela"]
                                else:
                                    lista_qual = ["Original", "Primeira Linha", "Paralela"]

                                val_qual = item_atual['qualidade'] if item_atual['qualidade'] in lista_qual else None
                                
                                nova_qualidade = st.pills("Qualidade", lista_qual, selection_mode="single", default=val_qual)

                                st.write("**Financeiro**")
                                c5, c6, c7 = st.columns(3)
                                with c5:
                                    novo_custo = st.number_input("Custo", value=float(item_atual['preco_custo']), step=0.50)
                                with c6:
                                    novo_venda = st.number_input("Venda", value=float(item_atual['preco_venda']), step=0.50)
                                with c7:
                                    nova_qtd = st.number_input("Qtd", value=int(item_atual['quantidade']), step=1)

                                if st.form_submit_button("🔄 Atualizar Dados"):
                                    dados_update = {
                                        "marca": nova_marca,
                                        "modelo": novo_modelo,
                                        "qualidade": nova_qualidade,
                                        "preco_custo": novo_custo,
                                        "preco_venda": novo_venda,
                                        "quantidade": nova_qtd
                                    }
                                    try:
                                        supabase.table("produtos").update(dados_update).eq("id", id_editar).execute()
                                        st.success(f"Produto atualizado com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar: {e}")

            st.divider()

        # Cadastro de Novos Produtos (Apenas para Admin)
        if st.session_state['cargo'] == 'Admin': 
            with st.expander("➕ Cadastrar Novo Produto", expanded=False):
                st.write("**O que vamos cadastrar?**")
                categoria_selecionada = st.pills(
                    "Selecione o tipo:", 
                    ["Tela", "Bateria", "Dock de Carga"], 
                    selection_mode="single",
                    default="Tela"
                )

                with st.form("form_cadastro_dinamico", clear_on_submit=True):
                    st.write(f"Cadastrando: **{categoria_selecionada}**")
                    
                    c1, c2 = st.columns(2)
                    with c1: 
                        marca = st.pills("Marca *", ["Samsung", "Apple", "Motorola", "Xiaomi", "LG", "Outros"], selection_mode="single")
                    with c2: 
                        modelo = st.text_input("Modelo do Aparelho *", placeholder="Ex:")

                    qualidade = None

                    if categoria_selecionada == "Tela":
                            qualidade = st.pills("Qualidade *", ["Original Nacional/China", "Retirada", "Incell", "OLED"])
                    
                    elif categoria_selecionada == "Bateria":
                            qualidade = st.pills("Qualidade *", ["Original", "Primeira Linha", "Paralela"])
                    
                    else:
                            qualidade = st.pills("Qualidade *", ["Original", "Primeira Linha", "Paralela"])
      
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
                        
                        if len(erros) > 0:
                            st.error(f"❌ Preencha: {', '.join(erros)}")
                        else:
                            novo_prod = {
                                "categoria": categoria_selecionada, 
                                "marca": marca, "modelo": modelo,
                                "qualidade": qualidade, "quantidade": qtd,
                                "preco_custo": custo, "preco_venda": venda
                            }
                            try:
                                supabase.table("produtos").insert(novo_prod).execute()
                                st.success(f"✅ {modelo} cadastrado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")