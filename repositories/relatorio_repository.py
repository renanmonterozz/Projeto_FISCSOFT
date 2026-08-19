from __future__ import annotations

from sqlalchemy import func, select

from database.models import Infrator, NotaFiscal, Produto, Tccm
from database.orm import session_scope


class RelatorioRepository:
    def listar_relatorio(self, infrator_id, processo, inicio, fim):
        dados = self.listar_dados(infrator_id, processo, inicio, fim)
        itens_por_nf = {}
        for nota in dados:
            detalhes = self.buscar_detalhes(nota["nota_fiscal"], infrator_id)
            itens_por_nf[nota["nota_fiscal"]] = detalhes.get("itens", []) if detalhes else []
        return dados, itens_por_nf
    def listar_processos(self, infrator_id):
        with session_scope() as session:
            rows = session.execute(
                select(Tccm.processo, Infrator.nome_infrator)
                .join(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .where(Tccm.infrator_id == infrator_id)
                .order_by(Tccm.processo)
            ).all()
            return [(row[0], row[1]) for row in rows]

    def listar_dados(self, infrator_id, processo=None, inicio=None, fim=None):
        with session_scope() as session:
            statement = (
                select(NotaFiscal.nota_fiscal, NotaFiscal.data, NotaFiscal.valor_total,
                       NotaFiscal.status_nota, func.count(Produto.lote))
                .join(Tccm, Tccm.processo == NotaFiscal.processo)
                .outerjoin(Produto, (Produto.nota_fiscal == NotaFiscal.nota_fiscal)
                           & (Produto.agente_matricula == NotaFiscal.agente_matricula))
                .where(Tccm.infrator_id == infrator_id)
                .group_by(NotaFiscal.nota_fiscal, NotaFiscal.data, NotaFiscal.valor_total, NotaFiscal.status_nota)
                .order_by(NotaFiscal.data.desc())
            )
            if processo:
                statement = statement.where(NotaFiscal.processo == processo)
            if inicio:
                statement = statement.where(NotaFiscal.data >= inicio)
            if fim:
                statement = statement.where(NotaFiscal.data <= fim)
            rows = session.execute(statement).all()
            return [{"nota_fiscal": r[0] or "--", "data": r[1], "valor_total": r[2] or 0,
                     "status": r[3] or "Pendente", "qtd_itens": r[4] or 0} for r in rows]

    def buscar_cards(self, infrator_id, processo=None, inicio=None, fim=None):
        dados = self.listar_dados(infrator_id, processo, inicio, fim)
        return {
            "total": len(dados),
            "aprovadas": sum(1 for item in dados if item["status"] == "Aprovada"),
            "pendentes": sum(1 for item in dados if item["status"] == "Pendente"),
            "valor_total": sum(item["valor_total"] for item in dados if item["status"] == "Aprovada"),
        }

    def buscar_detalhes(self, nota_fiscal, infrator_id):
        with session_scope() as session:
            row = session.execute(
                select(NotaFiscal, Tccm.processo)
                .join(Tccm, Tccm.processo == NotaFiscal.processo)
                .where(NotaFiscal.nota_fiscal == nota_fiscal, Tccm.infrator_id == infrator_id)
            ).first()
            if not row:
                return {}
            nota, processo = row
            produtos = session.scalars(select(Produto).where(Produto.nota_fiscal == nota_fiscal).order_by(Produto.lote)).all()
            return {
                "nota_fiscal": nota.nota_fiscal, "data": nota.data,
                "chave": nota.chave_de_acesso, "valor_total": nota.valor_total or 0,
                "status": nota.status_nota or "Pendente", "processo": processo,
                "matricula": nota.agente_matricula, "arquivo": nota.arquivo,
                "itens": [{"item_id": p.itens_id, "nome": p.nome_item or "--", "quantidade": p.quantidade or 0,
                           "preco_unitario": p.preco_unitario or 0,
                           "subtotal": (p.quantidade or 0) * (p.preco_unitario or 0)} for p in produtos],
            }
