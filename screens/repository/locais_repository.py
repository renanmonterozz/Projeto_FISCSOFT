from __future__ import annotations

from sqlalchemy import delete, select

from database.models import Local
from database.orm import session_scope


class LocaisRepository:
    def criar(self, dados):
        with session_scope() as session:
            local = Local(
                cep=dados["cep"],
                endereco=dados["endereco"],
                instituicao=dados["instituicao"],
                responsavel=dados["responsavel"],
                telefone=dados.get("telefone") or None,
            )
            session.add(local)
            session.flush()
            return local.id

    def atualizar(self, local_id, dados):
        with session_scope() as session:
            local = session.get(Local, local_id)
            if local is None:
                raise LookupError("Local nao encontrado.")
            local.cep = dados["cep"]
            local.endereco = dados["endereco"]
            local.instituicao = dados["instituicao"]
            local.responsavel = dados["responsavel"]
            local.telefone = dados.get("telefone") or None

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
