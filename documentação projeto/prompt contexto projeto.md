# Prompt para Continuidade do Projeto FISCSOFT

Copie e cole o prompt abaixo ao iniciar uma nova conversa para dar contexto ao assistente:

---

## Prompt

```
Sou desenvolvedor do projeto FISCSOFT, um sistema desktop de fiscalização do IBAMA construído com Python, CustomTkinter e SQLite.

Estrutura do projeto:
- Caminho: C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT
- Banco: SQLite local (fiscsoft.db), com opção de migração para MySQL
- Tela de login com 3 perfis: admin/123456, agente/123456, usuario/123456

Arquivos principais:
- main.py: Login e navegação
- config/styles.py: Cores e fontes (COLORS, FONTS)
- database/conexaodb.py: Conexão com SQLite/MySQL
- screens/crud_base.py: Classe base para telas com tabela
- screens/sidebar.py: Menu lateral com 8 itens
- screens/infratores.py: CRUD Infratores (antes agenteibama.py)
- screens/usuarios.py: CRUD Agentes IBAMA
- screens/itens.py: CRUD Itens
- screens/locais.py: CRUD Locais Cadastrados
- screens/historico.py: Logs de auditoria
- screens/relatorios.py: Monitoramento de Notas Fiscais
- screens/cadastrar_usuario.py: Formulário de usuários
- screens/visualizar_usuario.py: Popup visualizar agente
- screens/visualizar_infrator.py: Popup visualizar infrator

Padrões de código:
- Queries SQLite usam ? como placeholder
- Tabelas com espaços usam aspas duplas: "agente ibama", "nota fiscal"
- Cores padronizadas: col0=COLORS["text"], demais=COLORS["text_muted"]
- Dividers horizontais com cor #E0E0E0
- Botões de ação: ícones 👁 ✏️ 🗑️ via add_action_buttons()
- row_factory = sqlite3.Row para acesso dict-like
- Senhas SHA-256 legadas, verificadas via verify_password()

Mantenha esse contexto ao ajudar com alterações no projeto.
```

---

## Como Usar

1. Abra uma nova conversa no chat
2. Cole o prompt acima
3. Faça sua pergunta ou solicite a alteração

**Exemplo:**
```
[Prompt colado]

Adicione uma coluna de "Data de Cadastro" na tela de Infratores.
```
