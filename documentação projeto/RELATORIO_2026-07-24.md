# Relatorio Diario - 24/07/2026

## Projeto: FISCSOFT - Sistema de Fiscalizacao IBAMA

---

## Resumo Executivo

Correcao de bug critico na tela de Itens do TCCM (itens nao apareciam na listagem). Reformulacao da tela de Relatorio Externo do infrator: popup de detalhes maior e redimensionavel, colunas com layout `place`, calendario para selecao de periodo, e geracao de relatorio em arquivo .txt.

---

## Funcionalidades Implementadas / Corrigidas

### 1. Bug Fix: Itens nao apareciam na tela de Itens do TCCM
- **Causa raiz**: Itens cadastrados no TCCM eram inseridos com `notas_fiscais = NULL` e sem vinculo ao TCCM. A query de listagem filtrava por `notas_fiscais IN (NFs do processo)`, mas `NULL IN (...)` e sempre falso no SQL.
- **Solucao**:
  - Adicionada coluna `processo VARCHAR(100)` na tabela `itens` (database/conexaodb.py)
  - Migração `ALTER TABLE` adicionada no metodo `_migrar()` da classe Database (roda a cada conexao, garantindo compatibilidade com bancos existentes)
  - Atualizados INSERTs em `cadastro_tccm_completo.py` e `tccm_dashboard.py` para incluir `processo`
  - Atualizada query SELECT em `itens.py` para filtrar `WHERE i.processo = ? OR i.notas_fiscais IN (...)`

### 2. Popup de Detalhes do Relatorio Externo (fiscsoft_externo/telas/relatorio_externo.py)
- Janela aumentada de `650x550` para `900x680`
- `minsize(750, 550)` adicionado
- Redimensionamento habilitado (`resizable(True, True)`)
- Layout migrado de `pack/grid` para `place` com posicao relativa (relx, relwidth, rely, relheight)
- Scroll de itens removido `height=120` (agora expande com o popup)
- Botao "Fechar" sempre visivel na parte inferior

### 3. Tabela de Relatorio Externo - Colunas com `place`
- Cabeecalho e linhas de dados reajustados com `col_cfg` usando `place`:
  - Numero NF: relx=0.0, relwidth=0.22, anchor="w"
  - Data Emissao: relx=0.22, relwidth=0.18, center
  - Valor(R$): relx=0.40, relwidth=0.18, center
  - Qtd Itens: relx=0.58, relwidth=0.16, center
  - Status: relx=0.74, relwidth=0.14, center
  - Detalhes: relx=0.88, relwidth=0.12, center
- Itens da NF no popup de detalhes tambem reajustados com mesmo padrao `place`

### 4. Calendario para Selecao de Periodo (CalendarioPopup)
- Widget `CalendarioPopup` (CTkToplevel) com:
  - Grade de dias do mes com navegacao < / >
  - Selecao de data de inicio (clique 1) e data de fim (clique 2)
  - Destaque visual nas datas selecionadas (cor primary)
  - Botoes "Limpar" e "Confirmar"
  - Formato de saida: date objects (date_inicio, date_fim)
- Substituiu o campo de texto "Periodo (mm/aaaa)" na barra de filtros
- Filtro aplicado automaticamente apos selecao do periodo

### 5. Geracao de Relatorio em Arquivo
- Botao "Gerar Relatorio" agora:
  - Valida se periodo foi selecionado
  - Consulta NFs do infrator no periodo via SQL com filtro de datas
  - Para cada NF, busca itens vinculados na tabela `produtos`
  - Gera arquivo .txt com relatorio completo (dados NF + itens com qtd, preco unitario, subtotal)
  - Salva via dialogo "Salvar como" do sistema
  - Nome sugerido: `relatorio_dd-mm-aaaa_a_dd-mm-aaaa.txt`

### 6. Botao "Selecionar Periodo" Padronizado
- Altura: 38px (igual ao "Gerar Relatorio")
- Cor: COLORS["primary"] com texto branco
- Fonte: size_body bold

---

## Arquivos Modificados

| Arquivo | Acao |
|---------|------|
| database/conexaodb.py | **MODIFICADO** - Coluna `processo` na tabela itens + metodo `_migrar()` na classe Database |
| screens/cadastro_tccm_completo.py | **MODIFICADO** - INSERT inclui `processo` |
| screens/tccm_dashboard.py | **MODIFICADO** - INSERT inclui `processo` |
| screens/itens.py | **MODIFICADO** - Query filtrada por `processo` OR `notas_fiscais` |
| fiscsoft_externo/telas/relatorio_externo.py | **MODIFICADO** - Popup detalhes, colunas place, calendario, geracao relatorio |

---

## Stack Utilizada

- Python 3.14
- CustomTkinter (UI desktop)
- SQLite (banco de dados local)
- ALTER TABLE (migracao de schema)
- customtkinter CTkToplevel (popup de calendario)

---

## Proximos Passos Sugeridos

1. Implementar edicao/exclusao de TCCMs
2. Implementar fluxo de conciliacao ao aprovar NF
3. Implementar exportacao do Painel Geral em PDF
4. Integrar sistema externo (infrator) com o cadastro de TCCMs
5. Adicionar validacao de duplicidade de processo
6. Adicionar filtros adicionais ao relatorio externo (Status, Processo)

---

## Observacoes

- A coluna `processo` na tabela `itens` e o vinculo direto entre itens e TCCMs. Itens criados pelo cadastro TCCM recebem `processo` no INSERT. Itens importados por Excel ficam sem vinculo.
- O metodo `_migrar()` da classe Database roda a cada conexao, garantindo que a coluna `processo` exista mesmo em bancos ja criados antes da alteracao de schema.
- O CalendarioPopup usa `date` do Python para armazenar as datas, convertendo para `strftime('%Y-%m-%d')` nas queries SQL.
- A tela `ItensPage` (screens/itens.py) nao e mais utilizada no fluxo principal - itens sao cadastrados apenas via cadastro TCCM.
