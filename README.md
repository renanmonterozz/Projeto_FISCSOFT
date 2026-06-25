# Projeto_FISCSOFT

Sistema desktop para gerenciamento de fiscalização do IBAMA, construído com CustomTkinter e MySQL.

## Funcionalidades

- Tela de login com autenticação por usuário/senha
- Navegação por sidebar com múltiplas páginas
- Gerenciamento de usuários externos (CRUD)
- Cadastro de agentes IBAMA, infratores, TCCM, notas fiscais, produtos e insumos
- Conexão com banco de dados MySQL

## Estrutura do projeto

```
Projeto_FISCSOFT/
├── main.py              # Ponto de entrada (tela de login e app principal)
├── config/
│   ├── styles.py        # Cores, fontes e constantes visuais
│   └── database.py      # Credenciais de conexão com o banco
├── screens/
│   ├── sidebar.py       # Componente de navegação lateral
│   └── usuarios.py      # Página de gerenciamento de usuários
├── database/
│   ├── connection.py    # Classe de conexão com MySQL
│   └── schema.sql       # Script de criação do banco de dados
├── assets/              # Imagens e ícones do sistema
└── requirements.txt     # Dependências do projeto
```

## Pré-requisitos

- Python 3.8+
- MySQL Server
- pip

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd Projeto_FISCSOFT
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Crie o banco de dados MySQL executando o schema:
```bash
mysql -u root < database/schema.sql
```

5. Atualize as credenciais em `config/database.py` conforme seu ambiente.

## Executando

```bash
python main.py
```

## Dependências

- customtkinter - Interface gráfica moderna baseada em tkinter
- mysql-connector-python - Driver de conexão com MySQL
- Pillow - Processamento de imagens
