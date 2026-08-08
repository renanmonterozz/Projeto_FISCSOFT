# FISCSOFT - Sistema de Inspecao do IBAMA

Desktop (Python/customtkinter + SQLite) para TCCM. Dois modos no mesmo login: interno (agentes/admin) e externo (infratores via CPF).

## Comandos

- Rodar: `& .venv\Scripts\python.exe main.py` (externo so: `fiscsoft_externo\main_externo.py`)
- Sem testes; verificar com `-m py_compile main.py database\conexaodb.py`

## Arquitetura

- `main.py` = entry unico; login interno (`"agente ibama"`) e externo (`infrator` por CPF); telas mapeadas em `navegar()`.
- `config/permissoes.py` = fonte unica de acesso (perfis admin/agente/operador; `pode_acao`/`paginas_do_perfil`).
- Banco: `data/fiscsoft.db` (versionado; users teste admin/agente/operador, infrator CPF 12345678900). Schema inline em `criar_schema()`; `schema.sql` e MySQL legado; migracoes rodam na conexao (`_migrar`/`_migrar_perfis`).
- Tabelas com espaco exigem aspas: `"agente ibama"`, `"nota fiscal"`.
- `_path.py` importado por todas as telas (sys.path) — nao excluir.
- pt-BR; cores/fontes/assets em `config/styles.py`.

## Trabalho (economia de tokens)

- Nao leia o projeto inteiro: comece pelos arquivos relacionados ao pedido; so leia mais com dependencia real; sem buscas globais sem necessidade.
- Menor alteracao possivel; nao refatore/altere arquitetura sem pedido; rode so a verificacao necessaria.
- Nao leia: `.venv/`, `__pycache__/`, `*.pyc`, `*.log`, temporarios/caches, `.git/`, binarios, config sensivel (.env/credenciais).
