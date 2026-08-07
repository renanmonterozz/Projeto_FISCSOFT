# Relatório de Atualização - FISCSOFT

**Data:** 17/07/2026
**Desenvolvedores:** Saulo Dantas
**Projeto:** FISCSOFT - Sistema de Fiscalização IBAMA

---

## 1. Resumo das Alterações

Implementação do fluxo completo TCCM → Nota Fiscal → Conciliação automática, redesign da tela de cadastro de NF (itens via catálogo + Treeview), redesign do relatório de entrega (itens via ComboBox, impressão Windows, cadastro de local funcional) e ajustes nos JOINs de todos os arquivos para usar `processo` como ligação entre NF e TCCM.

---

## 2. Alterações Realizadas

### 2.1 Schema: Coluna `processo` em Nota Fiscal

Adicionada coluna `processo` (FK → `tccm.processo`) na tabela `"nota fiscal"` para vincular diretamente a nota ao TCCM, substituindo a ligação indireta por `agente ibama_matricula`.

Colunas adicionadas em `produtos`: `itens_id` (FK → `itens.id`) e `nome_item`.

**Arquivo:** `database/conexaodb.py`

---

### 2.2 Tela de Cadastro de Notas (Sistema Externo) — Reescrita

**Problema:** Formulário antigo usava campos de texto livres para itens, sem vinculação ao catálogo.

**Solução:**
- ComboBox de Processo que lista TCCMs do infrator logado (JOIN com infrator)
- Seção de Itens com Treeview (`ttk.Treeview`) para visualizar itens adicionados
- ComboBox de Itens carregados do catálogo (`tabela itens`, status Ativo)
- Campo de quantidade
- Botão "ANEXAR PDF" simplificado (sem leitura automática)
- Botão "LIMPAR" que reseta todos os campos

**Arquivo:** `fiscsoft_externo/telas/notas_fiscais_externo.py`

---

### 2.3 Conciliação Automática na Aprovação de NF

**Problema:** Ao aprovar uma nota fiscal, o `total_pago` do TCCM não era atualizado automaticamente.

**Solução:** Quando admin aprova NF em `screens/relatorios.py`:
1. Soma `quantidade × preco_unitario` dos produtos da NF
2. Atualiza `valor_total` da nota fiscal
3. Soma ao `total_pago` do TCCM vinculado (via `processo`)
4. Verifica se `total_pago >= total_devido` → atualiza status do TCCM para "Concluido"

**Arquivo:** `screens/relatorios.py`

---

### 2.4 Atualização dos JOINs em Todos os Arquivos

Todos os JOINs entre `"nota fiscal"` e `tccm` foram atualizados para usar `nf.processo = t.processo` (FK direta), substituindo o JOIN via `agente ibama_matricula`.

**Arquivos afetados:**
- `screens/relatorios.py`
- `screens/menu_inicial.py`
- `fiscsoft_externo/telas/dashboard_externo.py`
- `fiscsoft_externo/telas/relatorio_externo.py`

---

### 2.5 Relatório de Entrega — Redesign Completo

**Alterações:**
- Botão "Gerar Relatório" removido (redundante com Baixar PDF / Imprimir)
- "Imprimir" agora abre a janela de impressão do Windows (`notepad.exe /p`)
- "Baixar PDF" gera arquivo `.txt` com `filedialog.asksaveasfilename`
- Seção de itens substituída por ComboBox do catálogo `itens` (itens ativos) com `_carregar_itens_catalogo()`
- Método `_gerar_texto_relatorio()` centraliza geração do texto (usado por Imprimir e Baixar PDF)
- Seção de "Local de Destino" substituída por ComboBox com detalhes do local selecionado (CEP, endereço, instituição, responsável, telefone)
- Bind de scroll com mousewheel em ComboBoxes de itens e locais
- Botão "+ Cadastrar Novo Local" funcional com formulário completo (tamanho `500x520`)
- `usuario_logado` passado via `main.py` para `RelatorioEntregaPage`

**Arquivos:** `screens/relatorio_entrega.py`, `main.py`

---

### 2.6 Atualização do Prompt de Contexto

O prompt de contexto do projeto foi atualizado com:
- Descrição do fluxo TCCM → NF → Conciliação
- Descrição do relatório de entrega com ComboBoxes
- Schema atualizado (coluna `processo`, `itens_id`, `nome_item`)
- Padrão de CTkComboBox com bind de scroll

**Arquivo:** `documentação projeto/prompt contexto projeto.md`

---

## 3. Arquivos Modificados

| Arquivo | Tipo de Alteração |
|---------|-------------------|
| `database/conexaodb.py` | Schema (processo FK, itens_id, nome_item) |
| `fiscsoft_externo/telas/notas_fiscais_externo.py` | Reescrita completa |
| `screens/relatorios.py` | JOINs + conciliação automática |
| `screens/menu_inicial.py` | JOINs atualizados |
| `fiscsoft_externo/telas/dashboard_externo.py` | JOINs atualizados |
| `fiscsoft_externo/telas/relatorio_externo.py` | JOINs atualizados |
| `screens/relatorio_entrega.py` | Redesign completo |
| `main.py` | Passa usuario_logado |
| `documentação projeto/prompt contexto projeto.md` | Atualização do prompt |

---

## 4. Status do Projeto

### Fluxo TCCM → NF → Conciliação
- [x] Schema com FK `processo` em nota fiscal
- [x] Cadastro NF com itens do catálogo (Treeview)
- [x] Aprovação automática com conciliação
- [x] JOINs atualizados em todos os arquivos

### Relatório de Entrega
- [x] ComboBox de local de destino
- [x] ComboBox de itens do catálogo
- [x] Imprimir via Windows
- [x] Baixar PDF (txt)
- [x] Cadastrar local funcional
- [ ] Scroll com mouse nos ComboBoxes (parcial — bind注册ado mas dropdown nativo não responde)

---

**Fim do Relatório**
