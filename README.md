# Projeto_FISCSOFT

Sistema desktop para gerenciamento de fiscalizacao do IBAMA, construido com CustomTkinter e MySQL.

## Funcionalidades

- Tela de login com autenticacao por usuario/senha (bcrypt)
- Controle de acesso por perfil (Admin / Agente)
- Navegacao por sidebar com multiplas paginas
- Gerenciamento de Agentes IBAMA (CRUD)
- Gerenciamento de Infratores (CRUD)
- Gerenciamento de Itens (CRUD + importacao Excel)
- Monitoramento de Notas Fiscais com acoes (Aprovar/Rejeitar)
- Relatorio de Entrega de Materiais
- Conexao com banco de dados MySQL (Aiven Cloud)

## Estrutura do projeto

```
Projeto_FISCSOFT/
├── main.py                    # Ponto de entrada (login + navegacao)
├── utils.py                   # Hash de senhas (bcrypt)
├── .env.example               # Template de variaveis de ambiente
├── config/
│   └── styles.py              # Cores, fontes e constantes visuais
├── database/
│   ├── conexaodb.py           # Classe Database (com context manager)
│   ├── schema.sql             # Script DDL unificado
│   └── bd_FiscSoft.sql        # Dump com dados de teste
├── screens/
│   ├── crud_base.py           # Mixin reutilizavel para paginas CRUD
│   ├── sidebar.py             # Componente de navegacao lateral
│   ├── usuarios.py            # Gerenciamento de Agentes IBAMA
│   ├── cadastrar_usuario.py   # Formulario cadastro/edicao agente
│   ├── visualizar_usuario.py  # Visualizacao de agente
│   ├── itens.py               # Gerenciamento de Itens + Excel
│   ├── relatorios.py          # Monitoramento de Notas Fiscais
│   ├── relatorio_entrega.py   # Relatorio de Entrega
│   └── agente_mode/
│       ├── infratores.py         # Gerenciamento de Infratores
│       ├── cadastrar_infrator.py  # Formulario cadastro/edicao infrator
│       └── visualizar_infrator.py # Visualizacao de infrator
├── assets/
│   ├── imagens/               # Icones e imagens do sistema
│   └── planilhas/             # Planilhas para importacao
└── requirements.txt           # Dependencias do projeto
```

## Pre-requisitos

- Python 3.8+
- MySQL Server
- pip

## Instalacao

1. Clone o repositorio:
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

3. Instale as dependencias:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados:
   - Copie `.env.example` para `.env` e preencha suas credenciais
   - Execute `database/schema.sql` para criar as tabelas

## Executando

```bash
python main.py
```

## Seguranca

- Senhas armazenadas com bcrypt (hash com salt)
- Credenciais do banco em `.env` (nao versionado)
- Queries parametrizadas (prevencao de SQL Injection)
- Controle de acesso por perfil de usuario

## Dependencias

- customtkinter - Interface grafica moderna baseada em tkinter
- mysql-connector-python - Driver de conexao com MySQL
- Pillow - Processamento de imagens
- pandas - Leitura de planilhas Excel
- python-dotenv - Carregamento de variaveis de ambiente
- bcrypt - Hash seguro de senhas
