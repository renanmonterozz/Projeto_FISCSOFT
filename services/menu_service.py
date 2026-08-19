from __future__ import annotations

from repositories.menu_repository import MenuRepository


class MenuService:
    def __init__(self, repository=None):
        self.repository = repository or MenuRepository()

    def listar_notas(self, processo=None):
        return self.repository.listar_notas(processo)

    def buscar_tccm(self, processo):
        return self.repository.buscar_tccm(processo)

    def buscar_cards(self, processo=None):
        return self.repository.buscar_cards(processo)
