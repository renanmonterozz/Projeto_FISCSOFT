# Relatório de Atualização - FISCSOFT

**Data:** 16/07/2026  
**Desenvolvedores:** Saulo Dantas  
**Projeto:** FISCSOFT - Sistema de Fiscalização IBAMA

---

## 1. Resumo das Alterações

Esta sessão incluiu correções de bugs críticos, implementação de leitura automática de PDF, melhoria na experiência de login, correção de dados duplicados e tratamento correto de status de notas fiscais.

---

## 2. Alterações Realizadas

### 2.1 Correção: Tela de Cadastrar Notas não abria (CTkLabel)

**Problema:** `CTkLabel` recebia parâmetros `border_width` e `border_color`, que não existem nesse widget. Isso lançava `ValueError` durante a construção da tela.

**Correção:** Trocado `CTkLabel` por `CTkFrame` + `CTkLabel` interno para manter a borda visual.

**Arquivo:** `fiscsoft_externo/telas/notas_fiscais_externo.py`

---

### 2.2 Correção: Notas não apareciam no Dashboard externo

**Problema:** O `_salvar()` inseria notas com `"agente ibama_matricula" = 0` hardcoded, mas não existia registro `tccm` vinculando infratores ao agente 0. O `JOIN` entre `nota fiscal` e `tccm` retornava 0 linhas.

**Correções:**
- Adicionados 4 registros `tccm` no seed data (1 por infrator → agente 0)
- `_salvar()` agora busca o `agente ibama_matricula` real do tccm do infrator logado
- Registros inseridos diretamente no banco existente

**Arquivos:** `database/conexaodb.py`, `fiscsoft_externo/telas/notas_fiscais_externo.py`

---

### 2.3 Correção: Erro silencioso com datas do SQLite

**Problema:** Colunas `DATE` no SQLite armazenam strings (`'2026-07-15'`), mas o código chamava `.strftime()` nelas como se fossem `datetime.date`. Isso lançava `AttributeError`, engolido por `except Exception: notas = []`, mostrando sempre "Nenhuma nota fiscal encontrada".

**Correção:** Criada função `_fmt_date()` que trata tanto `datetime.date` quanto strings. Aplicada em todos os arquivos que formatam datas.

**Arquivos afetados:**
- `fiscsoft_externo/telas/dashboard_externo.py`
- `fiscsoft_externo/telas/relatorio_externo.py`
- `screens/relatorios.py`
- `screens/menu_inicial.py`

---

### 2.4 Funcionalidade: Leitura Automática de PDF

Nova funcionalidade que extrai dados de uma nota fiscal eletrônica (NF-e) em PDF e preenche o formulário automaticamente.

**Campos extraídos via regex:**
- Número da nota fiscal
- Chave de acesso (44 dígitos)
- Data de emissão
- Valor total

**Botões na tela de upload:**
- **"LER E ANEXAR PDF"** (vermelho) — lê e preenche automaticamente
- **"ANEXAR SEM LER"** (cinza) — anexa sem ler (PDFs incompatíveis)

**Dependência adicionada:** `pypdf`

**Arquivo:** `fiscsoft_externo/telas/notas_fiscais_externo.py`

---

### 2.5 Renomeação: Dashboard → Menu Inicial

Todas as referências a "Dashboard" no sistema externo foram renomeadas para "Menu Inicial".

**Arquivos afetados:**
- `fiscsoft_externo/telas/sidebar_externo.py` — label no menu lateral
- `fiscsoft_externo/main_externo.py` — permissões, navegação e rota inicial

---

### 2.6 Funcionalidade: Enter para Confirmar Login

Adicionada confirmação com a tecla `Enter` em ambas as telas de login.

**Mecanismo:** `self.bind("<Return>", lambda e: self.fazer_login())` na janela raiz + bindings nos entries individuais. `unbind` no `voltar_menu()`.

**Arquivos:** `main.py`, `fiscsoft_externo/main_externo.py`

---

### 2.7 Correção: AttributeError lbl_total_registros

**Problema:** `_render_rows()` era chamado antes da criação de `lbl_total_registros` e `lbl_valor_total`, causando `AttributeError`.

**Correção:** Invertida a ordem — footer com labels é criado antes de `_render_rows()`.

**Arquivo:** `screens/menu_inicial.py`

---

### 2.8 Correção: Dados duplicados nos Stat Cards

**Problema:** Infrator 1 tinha 2 registros TCCM apontando para o mesmo agente (0), fazendo cada nota ser contada 2x nos cards de stats.

**Exemplo:**
| Card | Antes (errado) | Depois (correto) |
|------|----------------|-------------------|
| Total | 12 | 6 |
| Aprovadas | 4 | 2 |
| Pendentes | 6 | 3 |

**Correções:**
- Removido TCCM duplicado (`TCCM-2026-0001`) do banco
- Queries dos stat cards agora usam `COUNT(DISTINCT nf.nota_fiscal)`

**Arquivos:** `fiscsoft_externo/telas/relatorio_externo.py`, `fiscsoft_externo/telas/dashboard_externo.py`

---

### 2.9 Tratamento do Status "Correção Solicitada"

**Problema:** O status `"Correcao Solicitada"` (definido pelo admin) caía no `else` genérico e aparecia como "Pendente" com ícone ⚠, sendo indistinguível de notas realmente pendentes.

**Correção:** Adicionado branch explícito com ícone ✏️ e cor laranja (`#D97706`).

**Arquivos:** `fiscsoft_externo/telas/relatorio_externo.py`, `fiscsoft_externo/telas/dashboard_externo.py`

---

## 3. Dependências Adicionadas

| Pacote | Versão | Uso |
|--------|--------|-----|
| `fpdf2` | 2.8.7 | Geração de PDFs de teste |
| `pypdf` | 6.14.2 | Leitura/extração de texto de PDFs |

---

## 4. Estrutura Final do Projeto

```
Projeto_FISCSOFT/
├── config/
│   └── styles.py              # Cores e fontes
├── database/
│   ├── conexaodb.py           # Conexão SQLite/MySQL + schema + seed
│   ├── schema.sql             # Schema MySQL
│   └── bd_FiscSoft.sql        # Dump MySQL
├── screens/
│   ├── agente_mode/
│   │   ├── infratores.py      # CRUD Infratores
│   │   └── cadastrar_infrator.py
│   ├── crud_base.py           # Classe base para tabelas
│   ├── cadastrar_usuario.py
│   ├── historico.py           # Logs de auditoria
│   ├── itens.py               # CRUD Itens
│   ├── locais.py              # CRUD Locais Cadastrados
│   ├── menu_inicial.py        # Dashboard principal
│   ├── relatorio_entrega.py
│   ├── relatorios.py          # Notas Fiscais (admin)
│   ├── sidebar.py             # Menu lateral
│   ├── usuarios.py            # Agentes IBAMA
│   ├── visualizar_infrator.py
│   └── visualizar_usuario.py
├── fiscsoft_externo/           # Programa externo
│   ├── main_externo.py
│   └── telas/
│       ├── sidebar_externo.py
│       ├── dashboard_externo.py
│       ├── notas_fiscais_externo.py  # Cadastro + leitura PDF
│       └── relatorio_externo.py
├── documentação projeto/
│   ├── prompt contexto projeto.md
│   ├── relatorio atualização 14-07-2026.md
│   ├── relatorio atualização 15-07-2026.md
│   └── relatorio atualização 16-07-2026.md
├── assets/
│   └── imagens/
├── main.py                    # Login interno (admin/agente)
├── utils.py                   # Utilitários (verify_password)
├── gerar_nota_fiscal_teste.py # Gerador de NF-e de teste
├── nota_fiscal_teste.pdf      # PDF de teste gerado
└── fiscsoft.db                # Banco SQLite local
```

---

## 5. Credenciais de Teste

### Sistema Principal

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin | 123456 | Administrador |
| agente | 123456 | Agente |
| usuario | 123456 | Usuário |

### Sistema Externo

| CPF | Senha | Nome |
|-----|-------|------|
| 12345678901 | senha123 | João Silva |
| 23456789012 | senha123 | Maria Oliveira |
| 34567890123 | senha123 | Pedro Santos |
| 45678901234 | senha123 | Ana Costa |

---

## 6. Status de Notas Fiscais

| Status | Definido por | Ícone | Cor |
|--------|-------------|-------|-----|
| Pendente | Default (infrator cadastra) | ⚠ | Amarelo |
| Aprovada | Admin | ✔ | Verde |
| Rejeitada | Admin | ✘ | Vermelho |
| Correção Solicitada | Admin | ✏️ | Laranja |

---

## 7. Commits Pendentes

```bash
git add .
git commit -m "feat: leitura PDF, correções de login, dados e relatórios

- Corrigido CTkLabel com params inválidos na tela de notas
- Implementada leitura automática de PDF (pypdf) com preenchimento de formulário
- Corrigido tratamento de datas SQLite (string vs date) em 4 arquivos
- Adicionado Enter para confirmar login (admin + externo)
- Corrigido erro de inicialização lbl_total_registros no menu_inicial
- Corrigidos stat cards com COUNT(DISTINCT) para evitar duplicatas
- Removido TCCM duplicado do banco
- Tratado status 'Correcao Solicitada' com ícone e cor próprio
- Renomeado Dashboard para Menu Inicial no sistema externo
- Adicionado tccm seed data para vincular infratores ao agente"
git push
```

---

**Fim do Relatório**
