# FISCSOFT - Projeto de Inspecao do IBAMA

## Visao Geral
Sistema desktop (Python/customtkinter) para gerenciamento de Termos de Coordenacao e Controle de Material (TCCM) do IBAMA.
Dois modos de uso:
- **Interno**: administradores e agentes IBAMA logam com usuario/senha
- **Externo**: infratores acessam via CPF

## Arquitetura
- **main.py**: Login, navegacao entre telas (welcome_app -> main_app com sidebar)
- **screens/**: Telas do sistema (customtkinter + CrudBase)
- **database/**: Conexao SQLite (conexaodb.py), schema SQL, banco fiscsoft.db
- **config/**: Estilos (COLORS, FONTS, ASSETS_DIR) em styles.py
- **utils.py**: Utilitarios (verificacao de senha, registro de logs)
- **assets/**: Icones e imagens PNG

## Fluxo TCCM (principal)
1. Login -> Tela de boas-vindas (TccmDashboardPage) com lista de TCCMs ativos
2. Usuario seleciona um TCCM -> Navega para menu principal com sidebar
3. Conteudo filtrado pelo TCCM selecionado:
   - Menu Principal (MenuInicialPage): NFs e stats do TCCM
   - Itens (ItensPage): itens vinculados ao TCCM via NFs
   - Dashboard TCCM (TccmDetalhesPage): detalhes, pessoas, NFs e itens

## Tabelas do Banco (principais)
- **tccm**: processo (PK), total_pago, total_devido, status, data_validade, intervalo
- **nota fiscal**: nota_fiscal (PK), processo, data, valor_total, status_nota, chave_de_acesso
- **produtos**: lote, quantidade, preco_unitario, nota fiscal_nota_fiscal (FK)
- **itens**: id, nome, descricao, tipo, notas_fiscais (FK para NF)
- **infrator**: id_infrator, nome_infrator, cpf, email
- **agente ibama**: matricula, nome_agente, login, senha, perfil, status

## Navegacao
- Sidebar (screens/sidebar.py): navega por nome de pagina via callback `on_navigate(pagina)`
- `navegar()` em main.py: mapeia nome da pagina para classe da tela
- `processo_tccm`: propagado via closure para filtrar conteudo

## Convencoes
- linguagem: portugues (BR) em UI e codigo
- Estilo visual: COLORS e FONTS de config/styles.py
- CRUDBase (screens/crud_base.py): classe base com build_header, build_filter_container, etc.
- customtkinter (ctk): framework de UI
- Banco: SQLite via Database context manager (database/conexaodb.py)

## Comando para rodar
```bash
cd C:\Users\62504556\Documents\GitHub\Projeto_FISCSOFT
python main.py
```

## Telas principais
- `TccmDashboardPage`: Lista selecionavel de TCCMs (tela de boas-vindas)
- `TccmDetalhesPage`: Detalhes de um TCCM (info, pessoas, NFs, itens)
- `MenuInicialPage`: Dashboard do TCCM com NFs e stats
- `ItensPage`: Lista de itens (filtrados por TCCM quando aplicavel)
- `RelatorioEntregaPage`: Relatorio de entrega de materiais
- `UsuariosPage`: Gestao de agentes
- `InfratoresPage`: Gestao de infratores
- `LocaisPage`: Locais cadastrados
- `RelatoriosPage`: Relatorios gerais
- `HistoricoPage`: Historico de acoes
