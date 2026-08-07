# Projeto_FISCSOFT

Sistema desktop para gerenciamento de Termos de Coordenacao e Controle de Material (TCCM) do IBAMA, construido com CustomTkinter e SQLite.

## Funcionalidades

- Tela de login com autenticacao por usuario/senha (bcrypt + SHA-256 legado)
- Controle de acesso por perfil (Administrador / Agente / Operador)
- Modo externo para infratores (login via CPF)
- Navegacao por sidebar com multiplas paginas (filtrada por perfil)
- Gerenciamento de Agentes IBAMA (CRUD)
- Gerenciamento de Infratores (CRUD)
- Gerenciamento de Itens (CRUD + importacao Excel)
- Monitoramento de Notas Fiscais com acoes (Aprovar/Rejeitar)
- Relatorio de Entrega de Materiais
- Banco de dados SQLite local

## Estrutura do projeto

```
Projeto_FISCSOFT/
├── main.py                    # Ponto de entrada (sistema interno: login + navegacao)
├── utils.py                   # Hash de senhas (bcrypt), verificacao e log de auditoria
├── config/
│   ├── styles.py              # Cores, fontes e constantes visuais
│   └── permissoes.py          # Matriz de permissoes por perfil (paginas e acoes)
├── database/
│   ├── conexaodb.py           # Classe Database (context manager, migracoes, schema SQLite)
│   └── schema.sql             # Referencia do schema (MySQL legado)
├── data/
│   └── fiscsoft.db            # Banco de dados SQLite
├── screens/                   # Telas do sistema interno
│   ├── crud_base.py           # Mixin reutilizavel para paginas CRUD
│   ├── sidebar.py             # Componente de navegacao lateral
│   ├── usuarios.py            # Gerenciamento de Agentes IBAMA
│   ├── infratores.py          # Gerenciamento de Infratores
│   ├── itens.py               # Gerenciamento de Itens + Excel
│   ├── relatorios.py          # Monitoramento de Notas Fiscais
│   └── ...
├── fiscsoft_externo/          # Sistema externo (infratores via CPF)
│   ├── main_externo.py
│   └── telas/
├── assets/
│   ├── imagens/               # Icones e imagens do sistema
│   ├── fontes/                # Fontes (Libre Baskerville)
│   └── planilhas/             # Planilhas para importacao
├── docs/                      # Documentacao e relatorios de sessao
└── requirements.txt           # Dependencias do projeto
```

## Pre-requisitos

- Python 3.8+
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

4. O banco SQLite (`data/fiscsoft.db`) e criado automaticamente ao rodar o sistema.

## Executando

```bash
python main.py            # Sistema interno
python fiscsoft_externo\main_externo.py   # Sistema externo (infratores)
```

## Seguranca

- Senhas armazenadas com bcrypt (hash com salt); compatibilidade com SHA-256 legado
- Queries parametrizadas (prevencao de SQL Injection)
- Controle de acesso por perfil de usuario (telas e acoes)

## Dependencias

- customtkinter - Interface grafica moderna baseada em tkinter
- Pillow - Processamento de imagens
- pandas - Leitura de planilhas Excel
- bcrypt - Hash seguro de senhas
- pywinstyles - Estilo visual em janelas Windows
