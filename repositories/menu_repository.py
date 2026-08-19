from __future__ import annotations

from sqlalchemy import func, select

from database.models import Infrator, Item, NotaFiscal, Produto, Tccm
from database.orm import session_scope


class MenuRepository:
    def listar_notas(self, processo=None):
        with session_scope() as session:
            statement = (
                select(
                    NotaFiscal.nota_fiscal,
                    NotaFiscal.data,
                    NotaFiscal.valor_total,
                    NotaFiscal.status_nota,
                    Infrator.nome_infrator,
                    Produto.lote,
                    Produto.nome_item,
                    Produto.quantidade,
                    Item.unidade_medida,
                )
                .select_from(NotaFiscal)
                .outerjoin(Tccm, Tccm.processo == NotaFiscal.processo)
                .outerjoin(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .outerjoin(
                    Produto,
                    (Produto.nota_fiscal == NotaFiscal.nota_fiscal)
                    & (Produto.agente_matricula == NotaFiscal.agente_matricula),
                )
                .outerjoin(Item, Item.id == Produto.itens_id)
                .order_by(NotaFiscal.data.desc())
            )
            if processo:
                statement = statement.where(NotaFiscal.processo == processo)
            rows = session.execute(statement).all()

        notas = {}
        for row in rows:
            chave = row[0]
            nota = notas.setdefault(
                chave,
                {
                    "nota_fiscal": row[0] or "--",
                    "data": row[1],
                    "valor_total": row[2] or 0,
                    "status": row[3] or "Pendente",
                    "infrator": row[4] or "--",
                    "itens_detalhes": [],
                },
            )
            if row[5]:
                nota["itens_detalhes"].append({
                    "nome": row[6] or "--",
                    "quantidade": row[7] or 0,
                    "unidade": row[8] or "un",
                })
        for nota in notas.values():
            nota["qtd_itens"] = len(nota["itens_detalhes"])
        return list(notas.values())

    def buscar_tccm(self, processo):
        with session_scope() as session:
            tccm = session.scalar(select(Tccm).where(Tccm.processo == processo))
            if not tccm:
                return None
            return {
                "processo": tccm.processo,
                "status": tccm.status,
                "documento_sei": tccm.documento_sei,
                "data_inicio": tccm.data_inicio,
                "semestres": tccm.semestres,
                "data_validade": tccm.data_validade,
                "total_devido": tccm.total_devido,
                "total_pago": tccm.total_pago,
            }

    def buscar_cards(self, processo=None):
        with session_scope() as session:
            nota_statement = select(NotaFiscal)
            if processo:
                nota_statement = nota_statement.where(NotaFiscal.processo == processo)
            notas = session.scalars(nota_statement).all()
            nota_ids = {(nota.nota_fiscal, nota.agente_matricula) for nota in notas}
            total_itens = 0
            if nota_ids:
                produtos = session.scalars(select(Produto)).all()
                total_itens = sum(
                    1 for produto in produtos
                    if (produto.nota_fiscal, produto.agente_matricula) in nota_ids
                    and any(
                        nota.nota_fiscal == produto.nota_fiscal
                        and nota.agente_matricula == produto.agente_matricula
                        and nota.status_nota == "Aprovada"
                        for nota in notas
                    )
                )
            aprovadas = [nota for nota in notas if nota.status_nota == "Aprovada"]
            return {
                "total_nf": len({nota.nota_fiscal for nota in notas}),
                "total_itens": total_itens,
                "valor_total": sum((nota.valor_total or 0) for nota in aprovadas),
            }
