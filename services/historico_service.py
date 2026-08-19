from __future__ import annotations

from datetime import datetime

from repositories.historico_repository import HistoricoRepository


class HistoricoService:
    def __init__(self, repository=None):
        self.repository = repository or HistoricoRepository()

    def listar(self):
        logs = self.repository.listar()
        for log in logs:
            log["data_hora"] = converter_data_log(log["data_hora"])
        return logs

    def pesquisar(self, termo=""):
        return filtrar_logs(self.listar(), termo)


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
