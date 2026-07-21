# Relatorio Diario - 20/07/2026

## Projeto: FISCSOFT - Sistema de Fiscalizacao IBAMA

---

## Resumo Executivo

Desenvolvimento da tela **Painel Geral** (Dashboard TCCM) como tela inicial pos-login, com visao panoramica completa do sistema. Implementacao do fluxo de navegacao em 3 janelas e criacao de dados de teste no banco de dados.

---

## Funcionalidades Implementadas

### 1. Painel Geral (screens/tccm_dashboard.py)
- **TccmDashboardPage**: Dashboard panoramico com scroll, contendo:
  - 5 cards de contadores no topo (TCCMs, Notas Fiscais, Itens, Infratores, Agentes)
  - Barra circular de progresso (% geral arrecadado vs total devido)
  - Secao de totais (Devido, Pago, Pendente, Valor em NFs)
  - Cards de status por TCCM (Pendentes, Pagos Parcial, Concluidos)
  - Tabela lateral esquerda: Todos os TCCMs com botao ">" para detalhes
  - Tabela lateral direita: Notas Fiscais Recentes (ultimas 10)
  - Botao "+ Novo TCCM" para cadastrar

### 2. Detalhes do TCCM (TccmDetalhesPage)
- Barra de progresso individual do TCCM
- Informacoes do TCCM (processo, valores, status, validade, intervalo)
- Secao de Pessoas Envolvidas:
  - Infrator: nome, CPF, email, telefone
  - Agente IBAMA: nome, matricula, CPF, email
- Tabela de Notas Fiscais Vinculadas (NF, data, chave de acesso, valor, status)
- Tabela de Itens vinculados (nome, quantidade, preco unitario, subtotal, NF)
- Botao "Voltar" para retornar ao Painel Geral

### 3. Modal de Cadastro TCCM (ModalCadastrarTCCM)
- Campos: Processo, Total Devido, Total Validado, Data Validade, Intervalo
- ComboBox de Agente (carrega agentes ativos do banco)
- ComboBox de Infrator (carrega infratores do banco)
- Validacao de campos obrigatorios e numericos
- Insercao direta no banco SQLite

### 4. Widget de Barra Circular (CircularProgressBar)
- Componente reutilizavel baseado em CTkCanvas
- Exibe percentual, texto e subtexto
- Cor primaria (verde) para progresso, cor de borda para fundo

### 5. Fluxo de Navegacao em 3 Janelas (main.py)
- **Janela 1 - LoginApp** (1000x600): Tela de login
- **Janela 2 - Welcome Screen** (1200x700): Painel Geral + botao "Acessar Sistema"
- **Janela 3 - Main App** (1200x700): Menu Principal com Sidebar + todas as telas
- Botao ">" no Painel Geral fecha Welcome Screen e abre Main App direto nos detalhes do TCCM

### 6. Sidebar Atualizada (screens/sidebar.py)
- Adicionado item "Dashboard TCCM" na navegacao (2o item)

---

## Dados de Teste Inseridos

| Tipo | Dados |
|------|-------|
| Infrator | Lucas Teixeira (CPF: 56789012345, ID: 5) |
| Itens | Mouse Logitech MX (IT-009), Monitor LG 27 4K (IT-010), Cadeira Ergonomica Executive (IT-011) |
| TCCM | PROC-2026-005 - Total Devido: R$ 12.500,00 - Agente: Carlos Silva (0) - Infrator: Lucas Teixeira (5) |
| NFs | NF-2026-0100 (Pendente, R$ 4.800,00) / NF-2026-0101 (Aprovada, R$ 2.250,00) |
| Produtos | LOTE-2026-0501 (2x Mouse @ R$ 1.200) / LOTE-2026-0502 (1x Monitor @ R$ 2.400) / LOTE-2026-0503 (1x Cadeira @ R$ 2.250, entregue) |

---

## Arquivos Modificados/Criados

| Arquivo | Acao |
|---------|------|
| screens/tccm_dashboard.py | **CRIADO** - 1.157 linhas (Painel Geral + Detalhes + Modal + CircularProgressBar) |
| main.py | **MODIFICADO** - Adicionado fluxo Welcome Screen, import TccmDashboardPage, navegacao com processo_tccm |
| screens/sidebar.py | **MODIFICADO** - Adicionado "Dashboard TCCM" na lista nav_items |
| PROMPT_FISCSOFT.md | **CRIADO** - Prompt atualizado do projeto |
| relatorios/RELATORIO_2026-07-20.md | **CRIADO** - Este relatorio |

---

## Stack Utilizada

- Python 3.14
- CustomTkinter (UI desktop)
- SQLite (banco de dados local)
- Canvas (barra circular de progresso)

---

## Proximos Passos Sugeridos

1. Implementar edicao/exclusao de TCCMs
2. Implementar fluxo de conciliacao ao aprovar NF (atualizar total_pago do TCCM automaticamente)
3. Adicionar filtros por status/infrator/agente no Painel Geral
4. Implementar exportacao do Painel Geral em PDF
5. Integrar sistema externo (infrator) com o cadastro de TCCMs

---

## Observacoes

- O CTkCanvas nao aceita `bg="transparent"` - usar cor solida
- Senhas SHA-256 sao legadas no seed do banco (verificadas via verify_password)
- Tabelas com espacos no nome precisam de aspas duplas nas queries SQLite
- O fluxo de 3 janelas (Login -> Welcome -> Main) permite mostrar o Painel Geral como "splash" antes do sistema completo
