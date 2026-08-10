# CONTEXTO COMPLETO — PROJETO FISCSOFT

## 1. Identificação do projeto

**Nome:** FISCSOFT

**Descrição:** Sistema desktop de fiscalização do IBAMA.

**Tecnologias principais:**

* Python
* CustomTkinter
* SQLite
* Possibilidade de migração para MySQL

**Caminho do projeto:**

`C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT`

**Banco principal:**

`fiscsoft.db`

O projeto possui um sistema interno e um sistema externo, com fluxos relacionados a agentes, infratores, TCCMs, notas fiscais, produtos, itens e relatórios.

---

# 2. Objetivo deste documento

Este arquivo contém o **contexto completo do FISCSOFT** para ser utilizado por agentes de IA durante tarefas de desenvolvimento.

Ele deve ser consultado quando a tarefa exigir conhecimento amplo da arquitetura, dos fluxos, do banco de dados ou das regras já estabelecidas no projeto.

Este documento não substitui a análise dos arquivos reais do projeto.

Quando houver diferença entre este documento e o código atual, o código atual deve ser considerado a fonte de verdade para a implementação.

Não assumir que uma informação deste documento continua válida sem verificar o código quando a tarefa depender de detalhes de implementação.

---

# 3. Estrutura geral dos sistemas

O FISCSOFT possui dois ambientes principais:

## 3.1 Sistema interno

Responsável pelo funcionamento interno do sistema, incluindo:

* login;
* agentes;
* infratores;
* TCCMs;
* itens;
* locais;
* notas fiscais;
* relatórios;
* histórico/auditoria;
* dashboard;
* administração.

## 3.2 Sistema externo

Responsável pelo acesso do infrator e pelas funcionalidades relacionadas ao envio e acompanhamento de notas fiscais.

---

# 4. Fluxo principal de navegação

O sistema interno possui três etapas principais de navegação:

1. `LoginApp`
2. `Welcome Screen`
3. `Main App`

## 4.1 LoginApp

Janela de login com tamanho aproximado de:

`1000x600`

## 4.2 Welcome Screen

Janela de aproximadamente:

`1200x700`

Apresenta:

* Painel Geral;
* Dashboard TCCM;
* botão "Acessar Sistema".

## 4.3 Main App

Janela de aproximadamente:

`1200x700`

Contém:

* Menu Principal;
* Sidebar;
* telas administrativas;
* telas de consulta;
* relatórios;
* demais funcionalidades internas.

## 4.4 Navegação a partir do TCCM

Ao clicar no botão `>` de um TCCM no Painel Geral:

1. a Welcome Screen é fechada;
2. a Main App é aberta;
3. o sistema abre diretamente a tela de detalhes daquele TCCM.

---

# 5. Arquivos principais — sistema interno

## `main.py`

Responsável por:

* Login;
* `LoginApp`;
* Welcome Screen;
* `_abrir_tela_principal`;
* `_abrir_menu_principal`;
* navegação;
* função `navegar`.

## `config/styles.py`

Responsável por:

* cores;
* fontes;
* `COLORS`;
* `FONTS`.

## `database/conexaodb.py`

Responsável por:

* conexão com SQLite/MySQL;
* schema;
* seed data;
* migração automática;
* método `_migrar`.

## `screens/crud_base.py`

Classe base para telas que utilizam tabelas.

Possui a estrutura `CrudBase mixin`.

## `screens/sidebar.py`

Menu lateral.

A versão atual possui 9 itens, incluindo o Dashboard TCCM.

## `screens/menu_inicial.py`

Dashboard principal com:

* cards;
* tabela de notas.

## `screens/tccm_dashboard.py`

Responsável pelo Painel Geral e pelos detalhes dos TCCMs.

Contém:

* `TccmDashboardPage`;
* `TccmDetalhesPage`;
* `ModalCadastrarTCCM`;
* `CircularProgressBar`.

## `screens/infratores.py`

CRUD de infratores.

Anteriormente identificado como:

`agenteibama.py`

## `screens/usuarios.py`

CRUD de Agentes IBAMA.

## `screens/itens.py`

CRUD de itens.

## `screens/locais.py`

CRUD de locais cadastrados.

## `screens/historico.py`

Responsável pelos logs de auditoria.

## `screens/relatorios.py`

Responsável pelo monitoramento e:

* aprovação de Notas Fiscais;
* rejeição de Notas Fiscais;
* conciliação automática.

## `screens/relatorio_entrega.py`

Responsável pelo relatório de entrega.

Possui:

* ComboBox de local;
* ComboBox de itens;
* impressão;
* cadastro de local.

## `screens/cadastrar_usuario.py`

Formulário de usuários.

## `screens/visualizar_usuario.py`

Popup para visualizar agente.

## `screens/visualizar_infrator.py`

Popup para visualizar infrator.

---

# 6. Arquivos principais — sistema externo

O sistema externo está localizado em:

`fiscsoft_externo/`

## `main.py`

Responsável pelo login unificado e navegação dos dois modos (interno e externo):

* login interno (`"agente ibama"`);
* login externo (infrator por CPF);
* navegação interna e externa.

## `fiscsoft_externo/telas/sidebar_externo.py`

Menu lateral externo com 3 itens.

## `fiscsoft_externo/telas/dashboard_externo.py`

Painel externo com:

* cards;
* TCCM;
* últimas notas.

## `fiscsoft_externo/telas/notas_fiscais_externo.py`

Responsável pelo cadastro de notas fiscais pelo infrator.

Possui:

* seleção de processo/TCCM;
* seleção de itens;
* filtro de itens pelo processo do TCCM;
* Treeview de itens;
* upload de PDF;
* extração automática de dados;
* botão "Enviar para Agente";
* botão "Limpar Tudo";
* botão "Voltar".

Os itens são filtrados utilizando o processo do TCCM e o status ativo.

## `fiscsoft_externo/telas/relatorio_externo.py`

Responsável pelo relatório detalhado por nota fiscal.

Possui:

* `CalendarioPopup`;
* seleção de período;
* geração de relatório `.txt`.

---

# 7. Fluxo de Nota Fiscal Externa

O fluxo principal é:

`Infrator → TCCM → Itens → Nota Fiscal → Agente → Aprovação/Rejeição`

## 7.1 Seleção do processo

O infrator seleciona o processo correspondente ao TCCM.

## 7.2 Seleção dos itens

O sistema permite adicionar somente itens vinculados ao TCCM.

O filtro utiliza a coluna:

`itens.processo`

e considera:

`status = 'Ativo'`

## 7.3 Envio da NF

Ao clicar em:

`Enviar para Agente`

o sistema:

1. grava a Nota Fiscal;
2. utiliza o status `Pendente`;
3. vincula a NF à matrícula do agente responsável pelo TCCM;
4. grava os itens na tabela `produtos`.

O lote dos produtos utiliza o formato:

`numero-ITEM-n`

## 7.4 Processamento interno

O administrador pode aprovar ou rejeitar a NF em:

`screens/relatorios.py`

A aprovação realiza a conciliação automática.

---

# 8. Credenciais de teste

As credenciais de teste existentes na documentação original são:

## Sistema interno

* `admin/123456`
* `agente/123456`
* `usuario/123456`

## Sistema externo

* `12345678901/senha123`
* `23456789012/senha123`
* `34567890123/senha123`
* `45678901234/senha123`

Estas informações são apenas dados de teste documentados para o projeto.

---

# 9. Banco de dados

O banco principal é SQLite:

`fiscsoft.db`

Existe possibilidade de migração para MySQL.

A conexão e a estrutura principal estão relacionadas a:

`database/conexaodb.py`

O método:

`Database._migrar()`

realiza migrações automáticas do schema.

Exemplo documentado:

`ALTER TABLE itens ADD COLUMN processo`

---

# 10. Tabelas principais

## `"agente ibama"`

Campos principais:

* `matricula` — PK;
* `login`;
* `senha`;
* `email`;
* `nome_agente`;
* `cpf`;
* `perfil`;
* `status`.

## `infrator`

Campos principais:

* `id_infrator` — PK auto;
* `cpf`;
* `email`;
* `senha`;
* `nome_infrator`;
* `telefone_infrator`.

## `tccm`

Campos principais:

* `processo` — PK;
* `"agente ibama_matricula"` — FK;
* `infrator_id_infrator` — FK;
* `total_devido`;
* `total_pago`;
* `total_validado`;
* `data_validade`;
* `intervalo`;
* `status`.

## `"nota fiscal"`

Campos principais:

* `nota_fiscal` — PK;
* `"agente ibama_matricula"` — FK;
* `processo` — FK para `tccm.processo`;
* `semestre`;
* `data`;
* `chave_de_acesso`;
* `valor_total`;
* `status_nota`.

Status documentados:

* `Pendente`;
* `Aprovada`;
* `Rejeitada`;
* `Correcao Solicitada`.

## `produtos`

Campos principais:

* `lote` — PK auto;
* `"nota fiscal_nota fiscal"` — FK;
* `"nota fiscal_agente ibama_matricula"` — FK;
* `itens_id` — FK para `itens.id`;
* `nome_item`;
* `quantidade`;
* `preco_unitario`;
* `data_validade`;
* `status_entrega`.

## `itens`

Campos principais:

* `id` — PK auto;
* `nome`;
* `descricao`;
* `codigo_interno`;
* `categoria`;
* `tipo`;
* `justificativa`;
* `unidade_medida`;
* `semestre`;
* `quantidade_prevista`;
* `status`;
* `notas_fiscais`;
* `processo` — FK para `tccm.processo`;
* `criado_em`.

Status documentados:

* `Ativo`;
* `Inativo`.

## `locais`

Campos principais:

* `id` — PK auto;
* `cep`;
* `endereco`;
* `instituicao`;
* `responsavel`;
* `telefone`;
* `criado_em`.

## `logs`

Campos principais:

* `id` — PK auto;
* `usuario`;
* `acao`;
* `tabela`;
* `descricao`;
* `criado_em`.

## `insumo`

Campos principais:

* `id_insumo`;
* `nome`;
* `tipo`;
* `descricao`;
* `justificativa`;
* `link`;
* `preco_orcado`;
* `"infrator_id_infrator"` — FK;
* `"produtos_lote"` — FK.

## `insumo_has_TCCM`

Tabela de junção entre:

`insumo`

e:

`tccm`.

---

# 11. Dados de teste documentados

A documentação atual registra:

* 3 agentes IBAMA;
* matrículas `0`, `1` e `2`;
* 5 infratores;
* IDs `1-5`;
* último infrator documentado: Lucas Teixeira;
* CPF documentado: `56789012345`;
* 5 TCCMs;
* processos `PROC-2026-001` até `PROC-2026-005`;
* `PROC-2026-005` associado ao infrator Lucas Teixeira;
* 11 itens no catálogo;
* 3 locais cadastrados.

Notas Fiscais documentadas para `PROC-2026-005`:

* `NF-2026-0100` — Pendente — R$ 4.800;
* `NF-2026-0101` — Aprovada — R$ 2.250.

Produtos documentados:

* `LOTE-2026-0501` — Mouse Logitech MX;
* `LOTE-2026-0502` — Monitor LG 27 4K;
* `LOTE-2026-0503` — Cadeira Ergonômica Executive.

---

# 12. Fluxo TCCM → Nota Fiscal → Conciliação

Fluxo documentado:

1. O agente cadastra o TCCM.
2. O TCCM possui `total_devido` e infrator.
3. O infrator cadastra uma Nota Fiscal vinculada ao processo do TCCM.
4. O infrator adiciona itens do catálogo.
5. O administrador aprova a Nota Fiscal.
6. O sistema soma os produtos:

   `quantidade × preco_unitario`
7. O resultado atualiza `valor_total` da Nota Fiscal.
8. O valor é somado ao `total_pago` do TCCM.
9. O sistema verifica:

   `total_pago >= total_devido`
10. O status do TCCM é atualizado de acordo com o resultado.

A tabela `produtos` utiliza `itens_id` e `nome_item` para vincular os produtos ao catálogo.

---

# 13. Dashboard TCCM

Arquivo:

`screens/tccm_dashboard.py`

## 13.1 TccmDashboardPage

Dashboard panorâmico com scroll.

Possui 5 cards no topo:

* TCCMs;
* Notas Fiscais;
* Itens;
* Infratores;
* Agentes.

Também possui:

* barra circular de progresso;
* percentual geral arrecadado;
* total devido;
* total pago;
* total pendente;
* valor em NFs;
* cards de status.

Cards de status:

* Pendentes;
* Pagos Parcial;
* Concluídos.

Também possui:

### Tabela esquerda

Todos os TCCMs com botão:

`>`

para acessar os detalhes.

### Tabela direita

Notas Fiscais recentes.

---

# 14. TccmDetalhesPage

Tela de detalhes do TCCM selecionado.

Possui:

* barra de progresso individual;
* informações do TCCM;
* grid com 8 campos;
* seção de pessoas;
* tabela de Notas Fiscais vinculadas;
* tabela de itens vinculados.

## Pessoas

### Infrator

Exibe:

* nome;
* CPF;
* email;
* telefone.

### Agente

Exibe:

* nome;
* matrícula;
* CPF;
* email.

## Itens

Os itens são apresentados por meio dos produtos das Notas Fiscais.

## Navegação

Possui botão:

`Voltar`

que retorna ao Painel Geral.

---

# 15. ModalCadastrarTCCM

Modal para criação de novo TCCM.

Campos:

* Processo;
* Total Devido;
* Total Validado;
* Data Validade;
* Intervalo.

Possui ComboBoxes para:

* Agente ativo;
* Infrator.

Os dados são carregados do banco para popular os ComboBoxes.

---

# 16. CircularProgressBar

Widget de barra circular.

Utiliza:

`Canvas`

para desenhar o progresso.

---

# 17. Fluxo de relatório externo

Arquivo:

`fiscsoft_externo/telas/relatorio_externo.py`

## CalendarioPopup

Utiliza:

`CTkToplevel`

Possui:

* grade de dias;
* navegação de mês;
* navegação para mês anterior;
* seleção da data inicial;
* seleção da data final.

As datas são armazenadas como objetos `date`.

## Filtro de período

O filtro é aplicado automaticamente após a seleção do período.

A tabela de NFs utiliza colunas configuradas com:

`place`

e:

`col_cfg`

com:

* `relx`;
* `relwidth`;
* `anchor`.

## Popup de detalhes

Tamanho documentado:

`900x680`

É redimensionável.

Os elementos utilizam `place`.

## Geração do relatório

O botão:

`Gerar Relatório`

gera um arquivo `.txt` contendo:

* NFs;
* itens;
* informações do período selecionado.

---

# 18. Fluxo de navegação completo

O fluxo documentado é:

`Login`

↓

`Welcome Screen`

↓

`Painel Geral`

↓

`Acessar Sistema`

↓

`Main App`

↓

`Menu Principal`

↓

`Sidebar`

↓

`Telas`

Ao clicar no botão `>` de um TCCM:

`Painel Geral`

↓

`TccmDetalhesPage`

Dentro da Main App, a Sidebar permite navegar entre as telas.

O logout retorna ao Login.

---

# 19. Relatório de Entrega

Arquivo:

`screens/relatorio_entrega.py`

## Local de destino

Possui ComboBox que carrega locais do banco.

Ao selecionar um local, são exibidos detalhes como:

* CEP;
* endereço;
* instituição;
* responsável;
* telefone.

## Itens

Possui ComboBox de itens do catálogo.

São considerados itens ativos.

Permite selecionar quantidade.

## Botões

* `Imprimir`;
* `Baixar PDF`;
* `+ Cadastrar Novo Local`.

O botão `Imprimir` abre:

`notepad /p`

O botão `Baixar PDF` gera um arquivo `.txt`.

O botão:

`Gerar Relatório`

foi removido por ser redundante.

---

# 20. Padrões de código

## SQL

Queries SQLite utilizam:

`?`

como placeholder.

Exemplo conceitual:

```python
cursor.execute(
    "SELECT * FROM tabela WHERE campo = ?",
    (valor,)
)
```

## Tabelas com espaços

Tabelas com espaços utilizam aspas duplas.

Exemplos:

```sql
"agente ibama"
```

```sql
"nota fiscal"
```

## SQLite Row Factory

O banco utiliza:

```python
row_factory = sqlite3.Row
```

permitindo acesso semelhante a dicionário.

## Senhas

Existem senhas SHA-256 legadas.

A verificação é feita utilizando:

`verify_password()`.

## Datas

As datas do SQLite são strings no formato:

`YYYY-MM-DD`

Ao formatar datas, utilizar:

`_fmt_date()`.

## Valores em reais

A documentação registra a utilização de:

`_fmt_brl()`

para formatar valores em:

`R$ 1.234,56`

## Enter no Login

O login utiliza:

```python
self.bind("<Return>", ...)
```

e realiza `unbind` em:

`voltar_menu()`.

## CTkComboBox

Existe bind de scroll/mousewheel para navegação pelas opções.

## CTkCanvas

`CTkCanvas` não aceita:

```python
bg="transparent"
```

Deve ser utilizada uma cor sólida, por exemplo:

```python
COLORS["white"]
```

## Botões de seleção

Os botões `>` utilizam:

```text
\u25B6
```

para indicar seleção/abertura de detalhes.

## Listas grandes

Utilizar:

`CTkScrollableFrame`

para listas grandes.

## Layout de tabelas

As colunas utilizam:

```python
col_cfg = [
    (relx, relwidth, anchor),
    ...
]
```

em conjunto com `place`.

## Migração automática

O banco utiliza:

`Database._migrar()`

para alterações de schema.

As migrações utilizam `ALTER TABLE` e tratamento de `OperationalError`.

---

# 21. Filtros de período

As consultas de período utilizam a lógica:

```sql
WHERE nf.data >= ? AND nf.data <= ?
```

com datas convertidas/formadas utilizando:

```sql
strftime('%Y-%m-%d')
```

As datas inicial e final do calendário são objetos `date`.

---

# 22. Regras para alterações futuras

Ao trabalhar neste projeto:

1. Verifique primeiro os arquivos diretamente relacionados à tarefa.
2. Utilize este documento como contexto geral.
3. Não presuma que a documentação está mais atualizada que o código.
4. Quando a tarefa envolver implementação, verifique o código real antes de alterar.
5. Preserve os padrões existentes quando eles ainda forem utilizados pelo projeto.
6. Não refatore partes não relacionadas à tarefa.
7. Não altere arquitetura sem solicitação.
8. Não altere banco de dados sem verificar as relações existentes.
9. Ao alterar tabelas, considere as chaves estrangeiras e os fluxos de TCCM/NF/produtos.
10. Ao alterar uma tela, preserve os padrões de layout já utilizados.
11. Ao alterar o fluxo de navegação, verifique as três etapas:

    * Login;
    * Welcome Screen;
    * Main App.
12. Ao alterar funcionalidades relacionadas a TCCM, verifique também as relações com:

    * infrator;
    * agente;
    * Nota Fiscal;
    * produtos;
    * itens.
13. Ao alterar a conciliação, preserve a lógica:
    `quantidade × preco_unitario`
14. Ao trabalhar com relatórios, verificar os filtros de período e o formato das datas.
15. Não modificar funcionalidades não relacionadas à solicitação.

---

# 23. Uso deste documento pelo OpenCode

Este arquivo é um **contexto completo de referência**.

Ele não precisa ser carregado em todas as tarefas.

Utilizá-lo principalmente quando a tarefa envolver:

* arquitetura;
* fluxo entre sistemas;
* banco de dados;
* TCCMs;
* Notas Fiscais;
* conciliação;
* dashboard;
* navegação;
* integração entre telas;
* regras de negócio;
* alteração estrutural.

Para tarefas pequenas, deve-se preferir analisar somente os arquivos diretamente envolvidos.

---

# 24. Fonte do contexto

Este documento foi consolidado a partir do contexto existente do projeto FISCSOFT fornecido pelo desenvolvedor.

As informações representam o estado documentado do projeto no momento da elaboração deste arquivo.

Quando necessário, o código-fonte atual deve ser consultado para confirmar detalhes de implementaçã

# Prompt para Continuidade do Projeto FISCSOFT

Copie e cole o prompt abaixo ao iniciar uma nova conversa para dar contexto ao assistente:

---

## Prompt

```
Sou desenvolvedor do projeto FISCSOFT, um sistema desktop de fiscalização do IBAMA construído com Python, CustomTkinter e SQLite.

Estrutura do projeto:
- Caminho: C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT
- Banco: SQLite local (fiscsoft.db), com opção de migração para MySQL
- Tela de login com 3 perfis: admin/123456, agente/123456, usuario/123456

Arquivos principais (sistema interno - main.py):
- main.py: Login e navegação (admin/agente)
- config/styles.py: Cores e fontes (COLORS, FONTS)
- database/conexaodb.py: Conexão com SQLite/MySQL + schema + seed data + migração automática (_migrar)
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
- fiscsoft_externo/telas/sidebar_externo.py: Menu lateral (3 itens)
- fiscsoft_externo/telas/dashboard_externo.py: Painel com cards + TCCM + últimas notas
- fiscsoft_externo/telas/notas_fiscais_externo.py: Cadastro de notas com Treeview de itens, ComboBox de processo/itens, upload de PDF
- fiscsoft_externo/telas/relatorio_externo.py: Relatório detalhado por nota fiscal com CalendarioPopup para seleção de período e geração de relatório em .txt

Credenciais de teste:
- Sistema interno: admin/123456, agente/123456, usuario/123456
- Sistema externo (CPF/senha): 12345678901/senha123, 23456789012/senha123, 34567890123/senha123, 45678901234/senha123

Banco de dados - Tabelas principais:
- "agente ibama": matricula (PK), login, senha, email, nome_agente, cpf, perfil, status
- infrator: id_infrator (PK auto), cpf, email, senha, nome_infrator
- tccm: processo (PK), "agente ibama_matricula" (FK), infrator_id_infrator (FK), total_devido, total_pago, status
- "nota fiscal": nota_fiscal (PK), "agente ibama_matricula" (FK), processo (FK → tccm.processo), data, chave_de_acesso, valor_total, status_nota (Pendente/Aprovada/Rejeitada/Correcao Solicitada)
- produtos: lote (PK auto), "nota fiscal_nota_fiscal" (FK), itens_id (FK → itens.id), nome_item, quantidade, preco_unitario
- itens: id (PK auto), nome, descricao, codigo_interno, categoria, unidade_medida, status (Ativo/Inativo), notas_fiscais, processo (FK → tccm.processo)
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

Fluxo Relatório Externo (fiscsoft_externo/telas/relatorio_externo.py):
- CalendarioPopup: CTkToplevel com grade de dias, navegação mês/anterior, seleção data início/fim
- Filtro de período aplicado automaticamente após seleção
- Tabela de NFs com colunas usando `place` + `col_cfg` (relx, relwidth, anchor)
- Popup de detalhes (900x680, redimensionável) com `place` em todos os elementos
- Botão "Gerar Relatório" gera arquivo .txt com NFs e itens do período selecionado
- Database._migrar(): migra schema automaticamente a cada conexão (ex: ALTER TABLE itens ADD COLUMN processo)

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
- Layout com `place` usando `col_cfg = [(relx, relwidth, anchor), ...]` para alinhar colunas em tabelas
- Database._migrar() para migrações automáticas (ALTER TABLE com try/except OperationalError)
- CalendarioPopup: seleção de período com data_inicio e fim como date objects
- Filtro de período em queries SQL: `WHERE nf.data >= ? AND nf.data <= ?` com strftime('%Y-%m-%d')

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
