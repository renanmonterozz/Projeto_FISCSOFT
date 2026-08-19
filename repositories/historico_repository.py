from __future__ import annotations

from sqlalchemy import select

from database.models import Log
from database.orm import session_scope


class HistoricoRepository:
    def listar(self):
        with session_scope() as session:
            logs = session.scalars(select(Log).order_by(Log.criado_em.desc())).all()
        return [
            {
                "id": log.id,
                "usuario": log.usuario,
                "acao": log.acao,
                "tabela": log.tabela,
                "descricao": log.descricao,
                "data_hora": log.criado_em,
            }
            for log in logs
        ]
