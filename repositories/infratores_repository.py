from __future__ import annotations

from sqlalchemy import delete, select

from database.models import Infrator
from database.orm import session_scope


class InfratoresRepository:
    def criar(self, dados):
        with session_scope() as session:
            infrator = Infrator(
                nome_infrator=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                telefone_infrator=dados["telefone"] or None,
                senha=dados["senha_hash"],
            )
            session.add(infrator)
            session.flush()
            return infrator.id_infrator

    def atualizar(self, infrator_id, dados):
        with session_scope() as session:
            infrator = session.get(Infrator, infrator_id)
            if infrator is None:
                raise LookupError("Infrator nao encontrado.")
            infrator.nome_infrator = dados["nome"]
            infrator.cpf = dados["cpf"]
            infrator.email = dados["email"]
            infrator.telefone_infrator = dados["telefone"] or None
            infrator.senha = dados["senha_hash"]
            session.flush()

    def listar(self):
        with session_scope() as session:
            infratores = session.scalars(select(Infrator).order_by(Infrator.nome_infrator)).all()
        return [
            {
                "id": infrator.id_infrator,
                "nome": infrator.nome_infrator,
                "cpf": infrator.cpf,
                "email": infrator.email,
                "telefone": infrator.telefone_infrator or "-",
            }
            for infrator in infratores
        ]

    def excluir(self, infrator_id):
        with session_scope() as session:
            session.execute(delete(Infrator).where(Infrator.id_infrator == infrator_id))
        return True
