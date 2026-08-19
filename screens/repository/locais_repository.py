from __future__ import annotations

from sqlalchemy import delete, select

from database.models import Local
from database.orm import session_scope


class LocaisRepository:
    def listar(self):
        with session_scope() as session:
            locais = session.scalars(select(Local).order_by(Local.id)).all()
        return [
            {
                "id": local.id,
                "cep": local.cep,
                "endereco": local.endereco,
                "instituicao": local.instituicao,
                "responsavel": local.responsavel,
                "telefone": local.telefone or "-",
            }
            for local in locais
        ]

    def excluir(self, local_id):
        with session_scope() as session:
            session.execute(delete(Local).where(Local.id == local_id))
        return True
