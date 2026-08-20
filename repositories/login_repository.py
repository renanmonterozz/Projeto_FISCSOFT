from __future__ import annotations

from sqlalchemy import select

from database.models import AgenteIbama, Infrator
from database.orm import session_scope


class LoginRepository:
    def buscar_agente_por_login(self, login):
        with session_scope() as session:
            agente = session.scalar(
                select(AgenteIbama).where(AgenteIbama.login == login)
            )
            if agente is None:
                return None
            return {
                "nome": agente.nome_agente,
                "senha": agente.senha,
                "status": agente.status,
                "perfil": agente.perfil,
            }

    def buscar_infrator_por_cpf(self, cpf):
        with session_scope() as session:
            infrator = session.scalar(
                select(Infrator).where(Infrator.cpf == cpf)
            )
            if infrator is None:
                return None
            return {
                "id": infrator.id_infrator,
                "nome": infrator.nome_infrator,
                "senha": infrator.senha,
            }
