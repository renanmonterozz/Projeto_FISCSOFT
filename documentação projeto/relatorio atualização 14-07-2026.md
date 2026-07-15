# Relatório de Atualização - FISCSOFT

**Data:** 14/07/2026  
**Desenvolvedores:** Saulo Dantas  
**Projeto:** FISCSOFT - Sistema de Fiscalização IBAMA

---

## 1. Resumo das Alterações

Esta sessão de trabalho incluiu melhorias na interface, padronização visual, criação de novas telas e migração do banco de dados.

---

## 2. Alterações Realizadas

### 2.1 Renomeação de Arquivo

| Antes | Depois |
|-------|--------|
| `screens/agente_mode/agenteibama.py` | `screens/agente_mode/infratores.py` |

**Motivo:** Evitar confusão entre o nome do arquivo e sua função real (gestão de infratores, não de agentes).

**Arquivos afetados:**
- `screens/agente_mode/infratores.py` (renomeado)
- `main.py` (import atualizado)
- `README.md` (documentação atualizada)

---

### 2.2 Padronização de Cores das Colunas

Implementado padrão uniforme em todas as telas com tabelas:

- **Coluna 0 (identificador principal):** `COLORS["text"]` (#111111)
- **Demais colunas (informação secundária):** `COLORS["text_muted"]` (#666666)

| Tela | Colunas Atualizadas |
|------|---------------------|
| Infratores (`infratores.py`) | Telefone |
| Agentes IBAMA (`usuarios.py`) | Perfil, Status |
| Itens (`itens.py`) | Unidade de Medida |
| Locais Cadastrados (`locais.py`) | Endereço, Instituição, Responsável, Telefone |
| Histórico (`historico.py`) | Usuário, Descrição |
| Relatórios (`relatorios.py`) | Todas exceto coluna 0 |

---

### 2.3 Aumento dos Popups de Visualização

| Popup | Antes | Depois |
|-------|-------|--------|
| Visualizar Agente | `700+X+Y` (sem altura) | `750x680+X+Y` |
| Visualizar Infrator | `700+X+Y` (sem altura) | `750x680+X+Y` |

**Arquivos afetados:**
- `screens/visualizar_usuario.py`
- `screens/visualizar_infrator.py`

---

### 2.4 Padronização do Campo Ações em Locais Cadastrados

| Antes | Depois |
|-------|--------|
| Botões de texto "Editar" / "Excluir" dentro do grid | Ícones 👁 ✏️ 🗑️ (Ver / Editar / Excluir) |

Método `visualizar_local()` adicionado com popup de visualização.

**Arquivo afetado:** `screens/locais.py`

---

### 2.5 Correção de Dividers

| Tela | Cor Anterior | Cor Atual |
|------|-------------|-----------|
| Todas as telas com `add_data_row()` | `#F0F0F0` | `#E0E0E0` |
| Relatórios (`relatorios.py`) | `#F0F0F0` | `#E0E0E0` |

---

## 3. Estrutura Final do Projeto

```
Projeto_FISCSOFT/
├── config/
│   └── styles.py              # Cores e fontes
├── database/
│   ├── conexaodb.py           # Conexão SQLite/MySQL
│   ├── schema.sql             # Schema do banco
│   └── bd_FiscSoft.sql        # Dados de teste
├── screens/
│   ├── agente_mode/
│   │   ├── infratores.py      # CRUD Infratores (renomeado)
│   │   └── cadastrar_infrator.py
│   ├── crud_base.py           # Classe base para tabelas
│   ├── cadastrar_usuario.py
│   ├── historico.py           # Logs de auditoria
│   ├── itens.py               # CRUD Itens
│   ├── locais.py              # CRUD Locais Cadastrados
│   ├── relatorio_entrega.py
│   ├── relatorios.py          # Notas Fiscais
│   ├── sidebar.py             # Menu lateral
│   ├── usuarios.py            # Agentes IBAMA
│   ├── visualizar_infrator.py
│   └── visualizar_usuario.py
├── documentação projeto/
│   └── relatorio atualização 14-07-2026.md
├── main.py                    # Tela de login
├── utils.py                   # Utilitários
├── .env                       # Configurações
└── fiscsoft.db                # Banco SQLite local
```

---

## 4. Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin | 123456 | Administrador |
| agente | 123456 | Agente |
| usuario | 123456 | Usuário Externo |

---

## 5. Para Conectar em Banco Online

1. Alterar `.env`:
   ```env
   DB_TYPE=mysql
   DB_HOST=host.com
   DB_PORT=3306
   DB_NAME=fiscsoft
   DB_USER=usuario
   DB_PASSWORD=senha
   ```

2. Instalar driver:
   ```bash
   pip install mysql-connector-python
   ```

3. Atualizar queries: trocar `?` por `%s` e `"tabela"` por `` `tabela` ``

---

## 6. Commits Pendentes

```bash
git add .
git commit -m "feat: padronização de telas e refatoração de nomes

- Renomeado agenteibama.py para infratores.py
- Padronizado cores de texto das colunas
- Aumentado popups visualizar_usuario e visualizar_infrator
- Adicionada tela Locais Cadastrados com CRUD completo
- Adicionada tela Histórico de Atividades
- Migrado banco de dados para SQLite
- Corrigido divider de relatorios.py"
git push
```

---

**Fim do Relatório**
