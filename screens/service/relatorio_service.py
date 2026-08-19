from __future__ import annotations

from datetime import datetime

from screens.repository.relatorio_repository import RelatorioRepository


class RelatorioService:
    def __init__(self, repository=None):
        self.repository = repository or RelatorioRepository()

    def listar_processos(self, infrator_id):
        return self.repository.listar_processos(infrator_id)

    def listar_dados(self, infrator_id, processo=None, inicio=None, fim=None):
        return self.repository.listar_dados(infrator_id, processo, inicio, fim)

    def buscar_cards(self, infrator_id, processo=None, inicio=None, fim=None):
        return self.repository.buscar_cards(infrator_id, processo, inicio, fim)

    def buscar_detalhes(self, nota_fiscal, infrator_id):
        return self.repository.buscar_detalhes(nota_fiscal, infrator_id)

    def listar_relatorio(self, infrator_id, processo, inicio, fim):
        return self.repository.listar_relatorio(infrator_id, processo, inicio, fim)
