from __future__ import annotations

from datetime import datetime

from repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, repository=None):
        self.repository = repository or DashboardRepository()

    def buscar_tccm(self, infrator_id):
        return self.repository.buscar_tccm(infrator_id)

    def listar_notas(self, infrator_id):
        return self.repository.listar_notas(infrator_id)

    def buscar_indicadores(self, infrator_id):
        return self.repository.buscar_indicadores(infrator_id)


def formatar_moeda_brl(valor):
    valor = float(valor or 0)
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data):
    if hasattr(data, "strftime"):
        return data.strftime("%d/%m/%Y")
    if data:
        try:
            return datetime.strptime(str(data), "%Y-%m-%d").strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return str(data)
    return "--"


def status_nota(status):
    status = status or "Pendente"
    if status == "Aprovada":
        return "success", "\u2714"
    if status == "Rejeitada":
        return "danger", "\u2718"
    if status == "Correcao Solicitada":
        return "correction", "\u270F"
    return "warning", "\u26A0"
