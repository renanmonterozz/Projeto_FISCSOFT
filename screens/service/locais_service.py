from __future__ import annotations


def filtrar_locais(locais, termo=""):
    termo = (termo or "").strip().lower()
    if not termo:
        return list(locais)
    return [
        local for local in locais
        if termo in local["instituicao"].lower()
        or termo in local["endereco"].lower()
        or termo in local["cep"].lower()
        or termo in local["responsavel"].lower()
    ]