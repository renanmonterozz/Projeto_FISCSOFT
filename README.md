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
python main.py            # Sistema interno e externo (infratores via CPF)
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

## Gerar executável (Windows)

Fornecemos um script simples para criar um executável usando PyInstaller.

1. Ative o ambiente virtual conforme a seção *Instalacao*.
2. Instale dependências de build:
```bash
pip install -r requirements-exe.txt
```
3. Execute o script `build_exe.bat` (no Windows) a partir da raiz do projeto:
```bat
build_exe.bat
```

O build padrão gera um diretório `dist\FISCSOFT` contendo o executável e recursos.
Se preferir um único arquivo, edite `build_exe.bat` trocando `--onedir` por `--onefile`.

## Criar instalador Windows (Inno Setup / NSIS)

Após gerar `dist\FISCSOFT`, você pode empacotar um instalador profissional com Inno Setup ou NSIS.

1. Instale uma das ferramentas:
	- Inno Setup: https://jrsoftware.org/isinfo.php (inclui `ISCC.exe`)
	- NSIS: https://nsis.sourceforge.io/ (inclui `makensis.exe`)

2. A partir da raiz do projeto execute:
```bat
build_installer.bat
```

O script tenta usar o Inno Setup (`ISCC`) primeiro e, se não encontrado, o NSIS (`makensis`).

O Inno Setup gerará um arquivo `.exe` conforme definido em `installer.iss`. O NSIS usa `installer_nsi.nsi`.

Observações:
- Customize `installer.iss` e `installer_nsi.nsi` para ajustar ícones, chaves de registro, páginas adicionais ou ações pós-instalação.
- Ambos os instaladores criam atalho no menu Iniciar e um ícone na área de trabalho por padrão.

Nota sobre o ícone do projeto

Coloque o ícone do projeto em `assets/imagens/logo_fiscsoft.ico` para integrá-lo automaticamente ao executável e ao instalador.
Se você só tiver `logo_fiscsoft.png`, pode converter para `.ico` usando ferramentas online ou o ImageMagick:

```bash
magick convert assets/imagens/logo_fiscsoft.png -resize 256x256 assets/imagens/logo_fiscsoft.ico
```

O `build_exe.bat` detecta automaticamente `assets/imagens/logo_fiscsoft.ico` e o usa como ícone do exe e o copia para `dist\FISCSOFT` para que os scripts do instalador o encontrem.
