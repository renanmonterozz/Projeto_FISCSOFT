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

Arquivos principais (sistema interno - main.py):
- main.py: Login e navegação (admin/agente)
- config/styles.py: Cores e fontes (COLORS, FONTS)
- database/conexaodb.py: Conexão com SQLite/MySQL + schema + seed data
- screens/crud_base.py: Classe base para telas com tabela
- screens/sidebar.py: Menu lateral com 8 itens
- screens/menu_inicial.py: Dashboard principal (cards + tabela de notas)
- screens/infratores.py: CRUD Infratores (antes agenteibama.py)
- screens/usuarios.py: CRUD Agentes IBAMA
- screens/itens.py: CRUD Itens
- screens/locais.py: CRUD Locais Cadastrados
- screens/historico.py: Logs de auditoria
- screens/relatorios.py: Monitoramento e aprovação/rejeição de Notas Fiscais com conciliação automática
- screens/relatorio_entrega.py: Relatório de entrega com ComboBox de local/itens, impressão e cadastro de local
- screens/cadastrar_usuario.py: Formulário de usuários
- screens/visualizar_usuario.py: Popup visualizar agente
- screens/visualizar_infrator.py: Popup visualizar infrator

Arquivos principais (sistema externo - fiscsoft_externo/):
- fiscsoft_externo/main_externo.py: Login e navegação (infrator via CPF)
- fiscsoft_externo/telas/sidebar_externo.py: Menu lateral (3 itens)
- fiscsoft_externo/telas/dashboard_externo.py: Painel com cards + TCCM + últimas notas
- fiscsoft_externo/telas/notas_fiscais_externo.py: Cadastro de notas com Treeview de itens, ComboBox de processo/itens, upload de PDF
- fiscsoft_externo/telas/relatorio_externo.py: Relatório detalhado por nota fiscal

Credenciais de teste:
- Sistema interno: admin/123456, agente/123456, usuario/123456
- Sistema externo (CPF/senha): 12345678901/senha123, 23456789012/senha123, 34567890123/senha123, 45678901234/senha123

Banco de dados - Tabelas principais:
- "agente ibama": matricula (PK), login, senha, email, nome_agente, cpf, perfil, status
- infrator: id_infrator (PK auto), cpf, email, senha, nome_infrator
- tccm: processo (PK), "agente ibama_matricula" (FK), infrator_id_infrator (FK), total_devido, total_pago, status
- "nota fiscal": nota_fiscal (PK), "agente ibama_matricula" (FK), processo (FK → tccm.processo), data, chave_de_acesso, valor_total, status_nota (Pendente/Aprovada/Rejeitada/Correcao Solicitada)
- produtos: lote (PK auto), "nota fiscal_nota_fiscal" (FK), itens_id (FK → itens.id), nome_item, quantidade, preco_unitario
- itens: id (PK auto), nome, descricao, codigo_interno, categoria, unidade_medida, status (Ativo/Inativo)
- locais: id (PK auto), cep, endereco, instituicao, responsavel, telefone
- logs: id (PK auto), usuario, acao, tabela, descricao

Fluxo TCCM → Nota Fiscal → Conciliação:
- TCCM é cadastrado com total_devido e status
- Infrator cadastra NF vinculada ao processo do TCCM, adicionando itens do catálogo
- Admin aprova NF → soma produtos (quantidade × preco_unitario) → atualiza valor_total da NF → soma ao total_pago do TCCM → verifica se total_pago >= total_devido → atualiza status do TCCM
- Tabela produtos usa itens_id (FK) e nome_item para vincular ao catálogo de itens

Fluxo Relatório de Entrega:
- ComboBox de local de destino (carrega do banco) com exibição de detalhes (CEP, endereço, instituição, responsável, telefone)
- ComboBox de itens do catálogo (itens ativos) com seleção de quantidade
- Botões: Imprimir (abre notepad /p), Baixar PDF (gera .txt), + Cadastrar Novo Local
- Botão Gerar Relatório foi removido (redundante)

Padrões de código:
- Queries SQLite usam ? como placeholder
- Tabelas com espaços usam aspas duplas: "agente ibama", "nota fiscal"
- Cores padronizadas: col0=COLORS["text"], demais=COLORS["text_muted"]
- Dividers horizontais com cor #E0E0E0
- Botões de ação: ícones via add_action_buttons()
- row_factory = sqlite3.Row para acesso dict-like
- Senhas SHA-256 legadas, verificadas via verify_password()
- Datas do SQLite são strings ('YYYY-MM-DD'), tratar com _fmt_date() ao formatar
- Enter binding nos logins: self.bind("<Return>", ...) + unbind no voltar_menu()
- CTkComboBox com bind de scroll (mousewheel) para navegação por opções

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
