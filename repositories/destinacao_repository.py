from __future__ import annotations

from sqlalchemy import func, select

from database.models import Item, Local, NotaFiscal, Produto
from database.orm import session_scope


class DestinacaoRepository:
    def criar_local(self, dados):
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

    def listar_locais(self):
        with session_scope() as session:
            locais = session.scalars(select(Local).order_by(Local.instituicao)).all()
        return [
            {
                "id": local.id,
                "cep": local.cep,
                "endereco": local.endereco,
                "instituicao": local.instituicao,
                "responsavel": local.responsavel,
                "telefone": local.telefone,
            }
            for local in locais
        ]

    def listar_itens(self, processo=None):
        if processo:
            statement = (
                select(
                    Produto.itens_id,
                    Produto.nome_item,
                    Item.descricao,
                    Item.unidade_medida,
                    func.coalesce(func.sum(Produto.quantidade), 0),
                )
                .join(
                    NotaFiscal,
                    (NotaFiscal.nota_fiscal == Produto.nota_fiscal)
                    & (NotaFiscal.agente_matricula == Produto.agente_matricula),
                )
                .outerjoin(Item, Item.id == Produto.itens_id)
                .where(NotaFiscal.processo == processo)
                .group_by(Produto.itens_id, Produto.nome_item, Item.descricao, Item.unidade_medida)
                .order_by(Produto.nome_item)
            )
            with session_scope() as session:
                rows = session.execute(statement).all()
            return [
                {
                    "id": row[0],
                    "nome": row[1],
                    "descricao": row[2] or row[1],
                    "unidade": row[3],
                    "quantidade": row[4] or 0,
                }
                for row in rows
            ]

        with session_scope() as session:
            itens = session.scalars(
                select(Item).where(Item.status == "Ativo").order_by(Item.nome)
            ).all()
        return [
            {
                "id": item.id,
                "nome": item.nome,
                "descricao": item.descricao,
                "unidade": item.unidade_medida,
                "quantidade": 0,
            }
            for item in itens
        ]
