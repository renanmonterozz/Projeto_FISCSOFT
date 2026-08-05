# Relatorio de Desenvolvimento - Sessao 21/07/2026

## Contexto
Refatoracao do fluxo de TCCMs no sistema FISCSOFT para tornar a navegacao mais intuitiva, com selecao de TCCM antes de acessar o sistema.

## Alteracoes Realizadas

### 1. TccmDashboardPage (tccm_dashboard.py:640-777)
**Antes**: Dashboard com stats cards, grafico circular de progresso, tabelas de TCCMs e NFs.
**Depois**: Lista selecionavel de TCCMs ativos (pendentes/pago parcial) com botao "Acessar".

- Removido: `build_header_topo`, `build_stats_cards`, `build_progress_section`, `build_tables_section`, `_build_tccm_table`, `_build_nf_table`, `_carregar_dados`, `_atualizar_dados`, `_render_tccm_table`, `_render_nf_table`, `_abrir_detalhes`, `_voltar_ao_dashboard`, `_abrir_modal_cadastro`
- Adicionado: `_build_lista_tccms`, `_carregar_tccms`, `_selecionar`
- Parametro `on_selecionar` passado via `kwargs.pop()` (antes causava erro de kwargs invalidos no CTkFrame)

### 2. TccmDetalhesPage (tccm_dashboard.py:248-637)
**Revertido** para formato original:
- `build_info_section`, `build_pessoas_section`, `build_notas_section`, `build_itens_section`
- Removido: `build_resumo_cards`, `build_progresso_section`, emojis nos headers
- Notas e itens separados em tabelas distintas

### 3. main.py (linhas 195-318)
- `TccmDashboardPage` recebe `on_selecionar` que chama `_abrir_menu_principal` com `processo_tccm`
- `_processo_tccm` salva antes do closure de `navegar()` para preservar o contexto
- `navegar()` propaga `processo_tccm` para MenuInicialPage e ItensPage
- Corrigido: `processo_tccm` era perdido ao navegar via sidebar (parametro default None)

### 4. ItensPage (itens.py:16-151)
- Novo parametro `processo_tccm` no construtor
- `carregar_do_banco()` filtra itens por NFs do TCCM quando `processo_tccm` informado
- Query: `WHERE i.notas_fiscais IN (SELECT nf.nota_fiscal FROM "nota fiscal" nf WHERE nf.processo = ?)`
- Header dinamico: "Itens do TCCM" / "Itens vinculados ao processo X"

### 5. MenuInicialPage (menu_inicial.py:23-309)
- Novo parametro `processo_tccm` no construtor
- `_carregar_notas()` filtra NFs por `WHERE nf.processo = ?`
- `atualizar_cards()` filtra stats (NFs, itens, valor, TCCMs) por processo
- Header dinamico: "TCCM - X" / "Notas fiscais e itens deste processo"

### 6. Filtros de TCCMs ativos
- Query de contagem: `WHERE status != 'concluido'`
- Query de listagem: `WHERE status != 'concluido' ORDER BY processo`
- Apenas TCCMs pendentes ou pagos parcialmente aparecem na lista

## Bug Corrigido
- `TccmDashboardPage.__init__`: `on_selecionar` era passado via `**kwargs` para `CTkFrame.__init__()`, que rejeita parametros desconhecidos. Corrigido com `kwargs.pop("on_selecionar", None)` antes do `super().__init__()`.

## Arquivos Modificados
- `C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT\screens\tccm_dashboard.py`
- `C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT\main.py`
- `C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT\screens\itens.py`
- `C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT\screens\menu_inicial.py`

## Arquivos Criados
- `C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT\AGENTS.md` - Contexto do projeto para IA
- `C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT\opencode.json` - Config do opencode

## Fluxo Final
1. Login (main.py) -> Tela de boas-vindas (TccmDashboardPage)
2. Lista de TCCMs ativos com: Processo, Infrator, Devido, Pago, Validade, Status
3. Clica "Acessar" em um TCCM -> Abre main_app com sidebar
4. Menu Principal: NFs e stats filtrados pelo TCCM
5. Itens na sidebar: itens vinculados ao TCCM via NFs
6. Dashboard TCCM: detalhes completos do TCCM
