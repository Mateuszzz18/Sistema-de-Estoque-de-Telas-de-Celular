# 📱 SGE - Sistema de Gestão de Estoque (Assistência Técnica)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=for-the-badge)

## 📖 Sobre o Projeto
O **SGE (Sistema de Gestão de Estoque)** é uma solução desenvolvida para substituir o controle manual (caderno) em assistências técnicas de smartphones. 

O foco principal é o controle preciso de **Frontais (Telas)**, diferenciando qualidades (OLED, Incell, Original) e gerenciando o fluxo de Ordem de Serviço (O.S.).

Este projeto está sendo construído com foco em **Engenharia de Dados**, utilizando modelagem relacional e boas práticas de desenvolvimento (Git Flow, Clean Code).

---

## 🚀 Funcionalidades Principais (Escopo V1.0)

### 📦 Gestão de Estoque
- **Cadastro Detalhado:** Registro de peças com Marca, Modelo, Cor, Qualidade (Original/Incell) e Preços (Custo/Venda).
- **Controle de Quantidade:** Baixa automática ao vincular peça a um serviço.
- **Alerta de Reposição:** (Futuro) Aviso automático para peças com estoque baixo (<= 1).

### 👥 Sistema de Usuários e Permissões (ACL)
- **Admin (Técnico/Dono):** Acesso total (CRUD). Pode cadastrar produtos e ver margem de lucro.
- **Visualizador (Gestor/Chefe):** Acesso "Read-Only". Pode visualizar dashboard, estatísticas e estoque, mas não pode alterar dados sensíveis nem dar baixa.

### 🛠️ Gestão de Serviços (O.S.)
- **Cronograma de Bancada:** Visualização de serviços ordenados por data de chegada (FIFO).
- **Histórico:** Registro completo do que foi feito, valor cobrado e garantia.

### 📊 Dashboard e Estatísticas
- Modelos com maior saída.
- Lucro estimado sobre peças paradas.
- Status das ordens de serviço.

---

## 🗂️ Estrutura do Banco de Dados
O sistema utiliza **SQLite** pela leveza e portabilidade.
As principais tabelas modeladas são:
1.  **`usuarios`**: Controle de acesso e cargos.
2.  **`produtos`**: Inventário físico.
3.  **`servicos`**: Ordens de serviço e histórico.

---

## 💻 Como Rodar o Projeto

### Pré-requisitos
- Python 3 instalado.
- Git instalado.
