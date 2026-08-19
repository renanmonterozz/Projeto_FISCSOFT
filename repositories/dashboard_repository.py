from __future__ import annotations

from sqlalchemy import distinct, func, select

from database.models import NotaFiscal, Tccm
from database.orm import session_scope


class DashboardRepository:
    def buscar_tccm(self, infrator_id):
        with session_scope() as session:
            tccm = session.scalar(
                select(Tccm)
                .where(Tccm.infrator_id == infrator_id)
                .order_by(Tccm.processo)
                .limit(1)
            )
            if tccm is None:
                return None
            return {
                "processo": tccm.processo,
                "total_devido": tccm.total_devido,
                "total_pago": tccm.total_pago,
                "status": tccm.status,
            }

    def listar_notas(self, infrator_id):
        with session_scope() as session:
            notas = session.execute(
                select(NotaFiscal)
                .join(Tccm, NotaFiscal.processo == Tccm.processo)
                .where(Tccm.infrator_id == infrator_id)
                .distinct()
                .order_by(NotaFiscal.data.desc())
            ).scalars().all()
            return [
                {
                    "nota_fiscal": nota.nota_fiscal or "--",
                    "data": nota.data,
                    "valor_total": nota.valor_total or 0,
                    "status": nota.status_nota or "Pendente",
                }
                for nota in notas
            ]

    def buscar_indicadores(self, infrator_id):
        with session_scope() as session:
            total_tccm = session.scalar(
                select(func.count()).select_from(Tccm).where(Tccm.infrator_id == infrator_id)
            ) or 0
            base = (
                select(NotaFiscal)
                .join(Tccm, NotaFiscal.processo == Tccm.processo)
                .where(Tccm.infrator_id == infrator_id)
            ).subquery()
            total_nf = session.scalar(select(func.count(distinct(base.c.nota_fiscal)))) or 0
            valor_total = session.scalar(
                select(func.coalesce(func.sum(base.c.valor_total), 0))
                .where(base.c.status_nota == "Aprovada")
            ) or 0
            total_pendentes = session.scalar(
                select(func.count(distinct(base.c.nota_fiscal)))
                .where(base.c.status_nota == "Pendente")
            ) or 0
            return {
                "total_tccm": total_tccm,
                "total_nf": total_nf,
                "valor_total": valor_total,
                "total_pendentes": total_pendentes,
            }
