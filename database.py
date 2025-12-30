import sqlite3
import os
from dotenv import load_dotenv 

load_dotenv()

NOME_DB = 'Sistema_de_estoque.db'

def conexao_db():
    return sqlite3.connect(NOME_DB)

def criar_tabela():
    conexao = conexao_db()
    cursor = conexao.cursor()

    #  Tabela Usuarios 
    print("Criando tabela de Usuarios")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            cargo TEXT NOT NULL
        )
    ''')

    # Tabela Produtos 
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
            status TEXT NOT NULL, 
            garantia_ate TEXT     
            )
    ''')

    
    senha_admin = os.getenv('SENHA_ADM')
    senha_visualizacao = os.getenv('SENHA_VISUALIZACAO')

    # Verificação de segurança
    if not senha_admin or not senha_visualizacao:
        print("ERRO CRÍTICO: Arquivo .env não encontrado ou senhas faltando!")
        exit() 

    print("Inserindo Usuários...")

    print("Criando Admin...")
    cursor.execute("""
            INSERT OR IGNORE INTO usuarios (username, senha, cargo)
            VALUES (?, ?, ?)
            """, ('Admin', senha_admin, 'admin'))

    print("Criando Chefe...")
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (username, senha, cargo)
        VALUES (?, ?, ?)
        """, ('Analista', senha_visualizacao, 'visualizador'))
    
    conexao.commit()
    conexao.close()
    print("--- Banco de dados configurado com sucesso! ---")

if __name__ == "__main__":
    criar_tabela()