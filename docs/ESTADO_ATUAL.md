
# Estado atual

## Em desenvolvimento

- Refatoração de telas e navegação do modo interno (menu/sidebar consolidados).

## Problema atual

- Nenhum pendente. Módulos alterados verificados com `py_compile` + import.

## Última alteração

- Restaurado `screens/tccm_dashboard.py` (remoção anterior desfeita) com sino de notificação de notas fiscais pendentes.
- Telas mescladas: `screens/itens_locais.py` (Itens + Locais) e `screens/usuarios_infratores.py` (Agente + Usuário Externo).
- Renomeações: `relatorio_entrega.py` → `destinacao.py`; `relatorios.py` → `notas_fiscais.py` (menu "Notas Fiscais"); `cadastrar_tccm.py` removido.
- `screens/crud_base.py`: sino de alerta (`build_alerta_nota`/`_notas_pendentes`) no header; `build_table` com altura configurável.
- `screens/cadastro_tccm_completo.py`: botão "Exportar Planilha" (openpyxl).
- Logs de auditoria passam a registrar o usuário logado.

## Próximo passo

- Rodar o app e validar visualmente o fluxo interno (login agente) e externo (CPF).

## Arquivos envolvidos

- `main.py`, `screens/sidebar.py`, `config/permissoes.py`
- `screens/crud_base.py`, `screens/menu_inicial.py`, `screens/tccm_dashboard.py`
- `screens/itens_locais.py`, `screens/usuarios_infratores.py`
- `screens/notas_fiscais.py`, `screens/destinacao.py`, `screens/cadastro_tccm_completo.py`
- `screens/itens.py`, `screens/locais.py`, `screens/usuarios.py`, `screens/infratores.py`, `screens/cadastrar_itens.py`
