# Prompt para Continuidade do Projeto FISCSOFT

Copie e cole o prompt abaixo ao iniciar uma nova conversa para dar contexto ao assistente:

---

## Prompt

```
Sou desenvolvedor do projeto FISCSOFT, um sistema desktop de fiscalizacao do IBAMA construido com Python, CustomTkinter e SQLite.

Estrutura do projeto:
- Caminho: C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT
- Banco: SQLite local (fiscsoft.db), com opcao de migracao para MySQL
- Tela de login com 3 perfis: admin/123456, agente/123456, usuario/123456

Fluxo de navegacao (3 janelas):
1. LoginApp (janela 1000x600) - Tela de login
2. Welcome Screen (janela 1200x700) - Painel Geral (Dashboard TCCM) + botao "Acessar Sistema"
3. Main App (janela 1200x700) - Menu Principal com Sidebar + todas as telas

Ao clicar no botao ">" de um TCCM no Painel Geral, fecha a Welcome Screen e abre a Main App ja na tela de detalhes daquele TCCM.

Arquivos principais (sistema interno - main.py):
- main.py: Login (LoginApp), Welcome Screen (_abrir_tela_principal), Menu Principal (_abrir_menu_principal), navegacao (navegar)
- config/styles.py: Cores e fontes (COLORS, FONTS)
- database/conexaodb.py: Conexao com SQLite/MySQL + schema + seed data
- screens/crud_base.py: Classe base para telas com tabela (CrudBase mixin)
- screens/sidebar.py: Menu lateral com 9 itens (inclui Dashboard TCCM)
- screens/menu_inicial.py: Dashboard principal (cards + tabela de notas)
- screens/tccm_dashboard.py: Painel Geral + Detalhes TCCM + Modal Cadastro TCCM + CircularProgressBar
- screens/infratores.py: CRUD Infratores (antes agenteibama.py)
- screens/usuarios.py: CRUD Agentes IBAMA
- screens/itens.py: CRUD Itens
- screens/locais.py: CRUD Locais Cadastrados
- screens/historico.py: Logs de auditoria
- screens/relatorios.py: Monitoramento e aprovacao/rejeicao de Notas Fiscais com conciliacao automatica
- screens/relatorio_entrega.py: Relatorio de entrega com ComboBox de local/itens, impressao e cadastro de local
- screens/cadastrar_usuario.py: Formulario de usuarios
- screens/visualizar_usuario.py: Popup visualizar agente
- screens/visualizar_infrator.py: Popup visualizar infrator

Arquivos principais (sistema externo - fiscsoft_externo/):
- fiscsoft_externo/main_externo.py: Login e navegacao (infrator via CPF)
- fiscsoft_externo/telas/sidebar_externo.py: Menu lateral (3 itens)
- fiscsoft_externo/telas/dashboard_externo.py: Painel com cards + TCCM + ultimas notas
- fiscsoft_externo/telas/notas_fiscais_externo.py: Cadastro de notas com Treeview de itens, ComboBox de processo/itens, upload de PDF
- fiscsoft_externo/telas/relatorio_externo.py: Relatorio detalhado por nota fiscal

Credenciais de teste:
- Sistema interno: admin/123456, agente/123456, usuario/123456
- Sistema externo (CPF/senha): 12345678901/senha123, 23456789012/senha123, 34567890123/senha123, 45678901234/senha123

Banco de dados - Tabelas principais:
- "agente ibama": matricula (PK), login, senha, email, nome_agente, cpf, perfil, status
- infrator: id_infrator (PK auto), cpf, email, senha, nome_infrator, telefone_infrator
- tccm: processo (PK), "agente ibama_matricula" (FK), infrator_id_infrator (FK), total_devido, total_pago, total_validado, data_validade, intervalo, status
- "nota fiscal": nota_fiscal (PK), "agente ibama_matricula" (FK), processo (FK -> tccm.processo), semestre, data, chave_de_acesso, valor_total, status_nota (Pendente/Aprovada/Rejeitada/Correcao Solicitada)
- produtos: lote (PK auto), "nota fiscal_nota_fiscal" (FK), "nota fiscal_agente ibama_matricula" (FK), itens_id (FK -> itens.id), nome_item, quantidade, preco_unitario, data_validade, status_entrega
- itens: id (PK auto), nome, descricao, codigo_interno, categoria, tipo, justificativa, unidade_medida, semestre, quantidade_prevista, status (Ativo/Inativo), notas_fiscais, criado_em
- locais: id (PK auto), cep, endereco, instituicao, responsavel, telefone, criado_em
- logs: id (PK auto), usuario, acao, tabela, descricao, criado_em
- insumo: id_insumo (PK auto), nome, tipo, descricao, justificativa, link, preco_orcado, "infrator_id_infrator" (FK), "produtos_lote" (FK)
- insumo_has_TCCM: Tabela de juncao entre insumo e tccm

Dados de teste no banco:
- 3 agentes ibama (matriculas 0, 1, 2)
- 5 infratores (IDs 1-5, ultimo: Lucas Teixeira CPF 56789012345)
- 5 TCCMs (PROC-2026-001 a PROC-2026-005), sendo PROC-2026-005 com infrator Lucas Teixeira
- 11 itens no catalogo (IDs 1-11)
- 3 locais cadastrados
- Notas Fiscais vinculadas ao PROC-2026-005: NF-2026-0100 (Pendente, R$ 4.800), NF-2026-0101 (Aprovada, R$ 2.250)
- Produtos vinculados: LOTE-2026-0501 (Mouse Logitech MX), LOTE-2026-0502 (Monitor LG 27 4K), LOTE-2026-0503 (Cadeira Ergonomica Executive)

Fluxo TCCM -> Nota Fiscal -> Conciliacao:
- Agente cadastra TCCM com total_devido e infrator
- Infrator cadastra NF vinculada ao processo do TCCM, adicionando itens do catalogo
- Admin aprova NF -> soma produtos (quantidade x preco_unitario) -> atualiza valor_total da NF -> soma ao total_pago do TCCM -> verifica se total_pago >= total_devido -> atualiza status do TCCM
- Tabela produtos usa itens_id (FK) e nome_item para vincular ao catalogo de itens

Fluxo Painel Geral (tccm_dashboard.py):
- TccmDashboardPage: Dashboard panoramico com scroll
  - 5 cards no topo: TCCMs, Notas Fiscais, Itens, Infratores, Agentes
  - Barra circular de progresso (% geral arrecadado)
  - Totais: Devido, Pago, Pendente, Valor em NFs
  - Cards de status: Pendentes, Pagos Parcial, Concluidos
  - Tabela esquerda: Todos os TCCMs com botao ">" para detalhes
  - Tabela direita: Notas Fiscais Recentes
- TccmDetalhesPage: Tela de detalhes do TCCM selecionado
  - Barra de progresso individual
  - Informacoes do TCCM (8 campos em grid)
  - Secao Pessoas: Infrator (nome, CPF, email, telefone) + Agente (nome, matricula, CPF, email)
  - Tabela Notas Fiscais Vinculadas
  - Tabela Itens vinculados (via produtos das NFs)
  - Botao "Voltar" retorna ao Painel Geral
- ModalCadastrarTCCM: Modal para criar novo TCCM
  - Campos: Processo, Total Devido, Total Validado, Data Validade, Intervalo
  - ComboBox: Agente (ativo), Infrator
  - Busca dados do banco para popular ComboBoxes
- CircularProgressBar: Widget de barra circular com Canvas

Fluxo de Navegacao (main.py):
- Login -> Welcome Screen (Painel Geral) -> "Acessar Sistema" -> Main App (Menu Principal)
- Botao ">" no Painel Geral fecha Welcome Screen e abre Main App com TccmDetalhesPage
- Dentro do Main App, sidebar permite navegar entre todas as telas
- Logout retorna ao Login

Fluxo Relatorio de Entrega:
- ComboBox de local de destino (carrega do banco) com exibicao de detalhes
- ComboBox de itens do catalogo (itens ativos) com selecao de quantidade
- Botoes: Imprimir (abre notepad /p), Baixar PDF (gera .txt), + Cadastrar Novo Local
- Botao Gerar Relatorio foi removido (redundante)

Padroes de codigo:
- Queries SQLite usam ? como placeholder
- Tabelas com espacos usam aspas duplas: "agente ibama", "nota fiscal"
- Cores padronizadas: col0=COLORS["text"], demais=COLORS["text_muted"]
- Dividers horizontais com cor #E0E0E0
- Botoes de acao: icones via add_action_buttons()
- row_factory = sqlite3.Row para acesso dict-like
- Senhas SHA-256 legadas, verificadas via verify_password()
- Datas do sao strings ('YYYY-MM-DD'), tratar com _fmt_date() ao formatar
- _fmt_brl() formata valores em R$ (1.234,56)
- Enter binding nos logins: self.bind("<Return>", ...) + unbind no voltar_menu()
- CTkComboBox com bind de scroll (mousewheel) para navegacao por opcoes
- CTkCanvas nao aceita bg="transparent", usar cor solida (ex: COLORS["white"])
- Botoes ">" usam unicode \u25b6 para indicar selecao/abrir detalhes
- Widgets CTkScrollableFrame para listas grandes

Mantenha esse contexto ao ajudar com alteracoes no projeto.
```

---

## Como Usar

1. Abra uma nova conversa no chat
2. Cole o prompt acima
3. Faca sua pergunta ou solicite a alteracao

**Exemplo:**
```
[Prompt colado]

Adicione uma coluna de "Data de Cadastro" na tela de Infratores.
```
