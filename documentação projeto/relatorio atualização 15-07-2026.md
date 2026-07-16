# Relatório de Atualização - FISCSOFT

**Data:** 15/07/2026  
**Desenvolvedores:** Saulo Dantas  
**Projeto:** FISCSOFT - Sistema de Fiscalização IBAMA

---

## 1. Resumo das Alterações

Esta sessão incluiu a criação do Menu Inicial (Dashboard) para o sistema principal e a criação de um programa separado para usuários externos com acesso somente leitura.

---

## 2. Alterações Realizadas

### 2.1 Criação do Menu Inicial (Dashboard)

Nova tela de boas-vindas exibida ao acessar "Menu Principal" no sidebar.

**Arquivo criado:** `screens/menu_inicial.py`

**Funcionalidades:**
- Título dinâmico: "Menu do Administrador" ou "Menu do Agente" conforme perfil
- 4 cards de resumo: Notas Fiscais, Itens Recebidos, Valor Total(R$), Tccms Ativos
- Tabela "Notas Fiscais Recebidas" com colunas:
  - Numero da NF
  - Chave de acesso
  - Data de Emissao
  - Itens
  - Valor Total(R$)
  - Usuario
  - Status (ícones: ✔ Aprovada, ✘ Rejeitada, ⚠ Pendente)
- Footer com Total de Registros e Valor Total

**Arquivo modificado:** `main.py`
- Adicionado import de `MenuInicialPage`
- Navegação "Menu Principal" agora exibe `MenuInicialPage` em vez de `UsuariosPage`

---

### 2.2 Criação do Programa Externo (fiscsoft_externo)

Programa separado para usuários externos (infratores) com acesso somente leitura ao banco de dados.

**Estrutura criada:**
```
fiscsoft_externo/
├── main_externo.py              # Login e navegação
└── telas/
    ├── __init__.py
    ├── sidebar_externo.py       # Menu lateral (3 itens)
    ├── dashboard_externo.py     # Painel do usuário
    ├── notas_fiscais_externo.py # Listagem de notas (read-only)
    └── relatorio_externo.py     # Relatórios
```

**Funcionalidades:**

| Tela | Descrição |
|------|-----------|
| Login | Autenticação via CPF (tabela infrator) |
| Dashboard | Cards: Meus TCCMs, Notas Fiscais, Valor Total, Pendentes + Info TCCM + Últimas Notas |
| Notas Fiscais | Listagem com filtros (Periodo, Status, Numero NF) - somente leitura |
| Relatório | Detalhamento por nota fiscal com totais |

**Credenciais de teste:**

| CPF | Senha | Nome |
|-----|-------|------|
| 12345678901 | senha123 | João Silva |
| 23456789012 | senha123 | Maria Oliveira |
| 34567890123 | senha123 | Pedro Santos |
| 45678901234 | senha123 | Ana Costa |

**Para executar:**
```bash
cd fiscsoft_externo
python main_externo.py
```

---

### 2.3 Inserção de Dados de Teste

**Notas Fiscais inseridas:**

| Nota Fiscal | Valor | Status |
|-------------|-------|--------|
| NF-2026-001 | R$ 15.750,50 | Aprovada |
| NF-2026-002 | R$ 8.320,00 | Pendente |
| NF-2026-003 | R$ 23.100,75 | Aprovada |
| NF-2026-100 | R$ 4.500,00 | Pendente |

**TCCM inserido:**

| Processo | Total Devido | Status |
|----------|--------------|--------|
| TCCM-2026-0001 | R$ 12.000,00 | pendente |

**Item inserido:**

| Código | Nome | Status |
|--------|------|--------|
| IT-2026-001 | Monitor LG 27" | Ativo |

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
│   │   ├── infratores.py      # CRUD Infratores
│   │   └── cadastrar_infrator.py
│   ├── crud_base.py           # Classe base para tabelas
│   ├── cadastrar_usuario.py
│   ├── historico.py           # Logs de auditoria
│   ├── itens.py               # CRUD Itens
│   ├── locais.py              # CRUD Locais Cadastrados
│   ├── menu_inicial.py        # Dashboard principal (NOVO)
│   ├── relatorio_entrega.py
│   ├── relatorios.py          # Notas Fiscais
│   ├── sidebar.py             # Menu lateral
│   ├── usuarios.py            # Agentes IBAMA
│   ├── visualizar_infrator.py
│   └── visualizar_usuario.py
├── fiscsoft_externo/           # Programa externo (NOVO)
│   ├── main_externo.py
│   └── telas/
│       ├── sidebar_externo.py
│       ├── dashboard_externo.py
│       ├── notas_fiscais_externo.py
│       └── relatorio_externo.py
├── documentação projeto/
│   ├── prompt contexto projeto.md
│   └── relatorio atualização 15-07-2026.md
├── main.py                    # Tela de login
├── utils.py                   # Utilitários
├── .env                       # Configurações
└── fiscsoft.db                # Banco SQLite local
```

---

## 4. Credenciais de Teste

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

## 5. Commits Pendentes

```bash
git add .
git commit -m "feat: menu inicial dashboard e programa externo

- Criado screens/menu_inicial.py com dashboard administrativo
- Cards de resumo: Notas Fiscais, Itens, Valor Total, TCCMs
- Tabela de Notas Fiscais Recebidas com status
- Criado fiscsoft_externo/ como programa separado
- Login via CPF para infratores
- Dashboard, Notas Fiscais e Relatórios (somente leitura)
- Inseridos dados de teste: notas fiscais, TCCM e item"
git push
```

---

**Fim do Relatório**
