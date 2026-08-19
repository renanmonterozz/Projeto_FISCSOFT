from __future__ import annotations

from datetime import datetime


def converter_data_log(valor):
    if not isinstance(valor, str):
        return valor
    try:
        return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def filtrar_logs(logs, termo=""):
    termo = (termo or "").strip().lower()
    if not termo:
        return list(logs)
    return [
        log for log in logs
        if termo in log["usuario"].lower()
        or termo in log["acao"].lower()
        or termo in log["tabela"].lower()
        or termo in log["descricao"].lower()
    ]


def chave_cor_acao(acao):
    if acao == "exclusao":
        return "danger"
    if acao == "edicao":
        return "warning"
    return "primary"


def truncar_descricao(descricao, limite=80):
    descricao = descricao or ""
    return descricao[:limite] + ("..." if len(descricao) > limite else "")
