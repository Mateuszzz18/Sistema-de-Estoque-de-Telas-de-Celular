import sqlite3
NOME_DB = 'Sistema_de_estoque.db'

def conexao_db():
    return sqlite3.connect(NOME_DB)

def criar_tabela():
    conexao = conexao_db()
    cursor = conexao.cursor()

#Tabela Usuarios
    print("Criando tabela de Usuarios")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            cargo TEXT NOT NULL
        )
    ''')

#Tabela Produtos
    print("Criando tabela de Produtos")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            qualidade TEXT NOT NULL,
            cor TEXT,
            preco_custo REAL,
            preco_venda REAL,
            quantidade INTEGER NOT NULL
        )
    ''')

#Tabela Servicos
    print("Criando tabela servicos")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT,
            modelo_aparelho TEXT NOT NULL,
            servico_feito TEXT NOT NULL,
            valor_cobrado REAL,
            data_entrada TEXT NOT NULL,
            data_saida TEXT,
            status TEXT NOT NULL, -- (Ex: 'Na Bancada', 'Pronto', 'Entregue')
            garantia_ate TEXT     -- Data final da garantia
            )
    ''')

    print("Inserindo Usuários")
    
    conexao.commit()
    conexao.close()
