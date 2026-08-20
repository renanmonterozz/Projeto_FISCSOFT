"""Controle de acesso por perfil do sistema interno.

Perfis suportados:
- admin: Administrador — acesso total (gerencia usuarios e aprova notas).
- agente: Agente IBAMA — operacao do dia a dia (cadastra/edita, mas nao
  gerencia usuarios nem aprova notas).
- operador: Operador — somente leitura (visualiza dados, sem alteracoes).

Para adicionar novos perfis no futuro, basta:
1. Incluir a chave em PERFIS e no alias normalizar_perfil();
2. Definir as paginas em PAGINAS_POR_PERFIL;
3. Definir as acoes em ACOES_POR_PERFIL.
"""

PERFIS = ("admin", "agente", "operador")

# Mapeia os valores gravados no banco ("Administrador", "admin", etc.)
# para a chave canonica usada no codigo.
_ALIAS_PERFIL = {
    "admin": "admin",
    "administrador": "admin",
    "agente": "agente",
    "operador": "operador",
    "usuario": "operador",
    "user": "operador",
}

# Paginas que cada perfil pode acessar (visao geral / sidebar).
# Obs.: "Itens" reune itens + locais; "Agente" reune agentes + usuarios externos.
PAGINAS_POR_PERFIL = {
    "admin": {
        "Menu Principal",
        "Dashboard TCCM",
        "Itens",
        "Destinacao",
        "Agente",
        "Notas Fiscais",
        "Historico",
        "Auditoria NF",
    },
    "agente": {
        "Menu Principal",
        "Dashboard TCCM",
        "Itens",
        "Destinacao",
        "Agente",
        "Notas Fiscais",
        "Auditoria NF",
    },
    "operador": {
        "Menu Principal",
        "Itens",
        "Notas Fiscais",
        "Auditoria NF",
    },
}

# Acoes que cada perfil pode executar dentro das telas.
# Quem nao possui a acao ainda visualiza os dados, porem sem os botoes
# de criacao/edicao/exclusao/aprovacao correspondentes.
ACOES_POR_PERFIL = {
    "admin": {
        "criar_tccm",
        "aprovar_nota",
        "gerenciar_usuarios",
        "gerenciar_infratores",
        "gerenciar_itens",
        "gerenciar_locais",
    },
    "agente": {
        "criar_tccm",
        "gerenciar_infratores",
        "gerenciar_itens",
        "gerenciar_locais",
        "aprovar_nota",
    },
    "operador": set(),
}

# Paginas do sistema externo (infrator) — unico perfil disponivel.
PAGINAS_EXTERNO = {"Menu Inicial", "Cadastrar Notas", "Relatorio"}

PAGINA_ALIASES = {
    "menu principal": "Menu Principal",
    "menu inicial": "Menu Principal",
    "registro": "Itens",
    "registros": "Itens",
    "itens": "Itens",
    "locais cadastrados": "Locais Cadastrados",
    "usuarios": "Agente",
    "usuários": "Agente",
    "usuario": "Agente",
    "usuario externo": "Agente",
    "agente": "Agente",
    "destinacao": "Destinacao",
    "notas fiscais": "Notas Fiscais",
    "nota fiscal": "Notas Fiscais",
    "historico": "Historico",
    "histórico": "Historico",
    "auditoria": "Auditoria NF",
    "auditoria nf": "Auditoria NF",
    "dashboard tccm": "Dashboard TCCM",
    "cadastro tccm": "Cadastro TCCM",
    "cadastro": "Cadastro TCCM",
}


def normalizar_pagina(pagina):
    """Converte aliases visuais de menu para o nome canonico do sistema."""
    if pagina is None:
        return None
    chave = str(pagina).strip()
    if not chave:
        return chave
    return PAGINA_ALIASES.get(chave.casefold(), chave)


def normalizar_perfil(perfil):
    """Converte o valor gravado no banco (ex.: 'Administrador') na chave canonica."""
    if not perfil:
        return "operador"
    chave = str(perfil).strip().lower()
    return _ALIAS_PERFIL.get(chave, "operador")


def paginas_do_perfil(perfil):
    """Retorna o conjunto de paginas liberadas para o perfil."""
    return PAGINAS_POR_PERFIL.get(normalizar_perfil(perfil), set())


def pode_acessar(perfil, pagina):
    """True se o perfil pode acessar a pagina."""
    return normalizar_pagina(pagina) in paginas_do_perfil(perfil)


def pode_acao(perfil, acao):
    """True se o perfil pode executar a acao (criar/editar/excluir/aprovar)."""
    return acao in ACOES_POR_PERFIL.get(normalizar_perfil(perfil), set())
