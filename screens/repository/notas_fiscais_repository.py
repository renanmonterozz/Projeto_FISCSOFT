from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from database.models import AgenteIbama, Infrator, Item, NotaFiscal, Produto, Tccm
from database.orm import session_scope


class NotasFiscaisRepository:
    def listar_monitoramento(self, processo=None):
        with session_scope() as session:
            statement = (
                select(
                    NotaFiscal, Infrator.nome_infrator, Infrator.cpf,
                    Tccm.total_devido, Tccm.total_pago, func.count(Produto.lote),
                )
                .select_from(NotaFiscal)
                .join(Tccm, Tccm.processo == NotaFiscal.processo)
                .join(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .outerjoin(
                    Produto,
                    (Produto.nota_fiscal == NotaFiscal.nota_fiscal)
                    & (Produto.agente_matricula == NotaFiscal.agente_matricula),
                )
                .group_by(NotaFiscal, Infrator.nome_infrator, Infrator.cpf, Tccm.total_devido, Tccm.total_pago)
                .order_by(NotaFiscal.data.desc())
            )
            if processo:
                statement = statement.where(NotaFiscal.processo == processo)
            rows = session.execute(statement).all()
            return [
                {
                    "nota_fiscal": nota.nota_fiscal,
                    "data": nota.data,
                    "valor_total": nota.valor_total or 0,
                    "interessado": nome,
                    "cpf": cpf,
                    "processo": nota.processo,
                    "matricula": nota.agente_matricula,
                    "status": nota.status_nota or "Pendente",
                    "total_devido": total_devido or 0,
                    "total_pago": total_pago or 0,
                    "itens": qtd_itens or 0,
                    "arquivo": nota.arquivo,
                }
                for nota, nome, cpf, total_devido, total_pago, qtd_itens in rows
            ]

    def atualizar_status(self, nota_fiscal, matricula, processo, novo_status):
        with session_scope() as session:
            nota = session.get(NotaFiscal, (nota_fiscal, matricula))
            if nota is None:
                raise LookupError("Nota fiscal nao encontrada.")
            soma = session.scalar(
                select(func.coalesce(func.sum(Produto.quantidade * Produto.preco_unitario), 0))
                .where(Produto.nota_fiscal == nota_fiscal, Produto.agente_matricula == matricula)
            ) or 0
            if soma > 0:
                nota.valor_total = soma
            nota.status_nota = novo_status
            if novo_status == "Aprovada" and processo:
                tccm = session.scalar(select(Tccm).where(Tccm.processo == processo))
                if tccm:
                    tccm.total_pago = (tccm.total_pago or 0) + (soma or nota.valor_total or 0)
                    tccm.status = "concluido" if tccm.total_pago >= tccm.total_devido else "pendente"

    def buscar_detalhes(self, nota_fiscal, infrator_id):
        with session_scope() as session:
            row = session.execute(
                select(NotaFiscal, Tccm.processo, Infrator.nome_infrator, Infrator.cpf)
                .join(Tccm, Tccm.processo == NotaFiscal.processo)
                .join(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .where(NotaFiscal.nota_fiscal == nota_fiscal, Tccm.infrator_id == infrator_id)
                .limit(1)
            ).first()
            if not row:
                return {}
            nota, processo, _, _ = row
            produtos = session.scalars(
                select(Produto).where(Produto.nota_fiscal == nota_fiscal).order_by(Produto.lote)
            ).all()
            return {
                "nota_fiscal": nota.nota_fiscal,
                "data": nota.data,
                "chave": nota.chave_de_acesso,
                "valor_total": nota.valor_total or 0,
                "status": nota.status_nota or "Pendente",
                "processo": processo,
                "itens": [
                    {"nome": p.nome_item or "--", "quantidade": p.quantidade or 0,
                     "preco_unitario": p.preco_unitario or 0,
                     "subtotal": (p.quantidade or 0) * (p.preco_unitario or 0)}
                    for p in produtos
                ],
            }
    def listar_processos(self, infrator_id):
        with session_scope() as session:
            rows = session.execute(
                select(Tccm.processo, Infrator.nome_infrator)
                .join(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .where(Tccm.infrator_id == infrator_id)
                .order_by(Tccm.processo)
            ).all()
            return [(row[0], row[1]) for row in rows]

    def listar_itens_processo(self, processo):
        with session_scope() as session:
            itens = session.scalars(
                select(Item)
                .where(Item.processo == processo, Item.status == "Ativo")
                .order_by(Item.nome)
            ).all()
            return [
                {
                    "id": item.id,
                    "nome": item.nome,
                    "descricao": item.descricao,
                    "unidade": item.unidade_medida,
                }
                for item in itens
            ]

    def criar_nota(self, dados, itens):
        with session_scope() as session:
            agente = session.scalar(
                select(Tccm.agente_matricula)
                .where(Tccm.processo == dados["processo"])
                .limit(1)
            )
            if agente is None:
                raise LookupError("Agente responsavel nao encontrado para o processo.")

            nota = NotaFiscal(
                nota_fiscal=dados["numero"],
                semestre=1,
                data=datetime.strptime(dados["data"], "%Y-%m-%d").date(),
                chave_de_acesso=dados["chave"],
                valor_total=dados["valor_total"],
                agente_matricula=agente,
                status_nota="Pendente",
                processo=dados["processo"],
                arquivo=dados.get("arquivo"),
            )
            session.add(nota)
            session.flush()
            for indice, item in enumerate(itens, start=1):
                session.add(Produto(
                    lote=f"{dados['numero']}-ITEM-{indice}",
                    status_entrega="pendente",
                    quantidade=item["quantidade"],
                    preco_unitario=item["preco_unitario"],
                    nota_fiscal=dados["numero"],
                    agente_matricula=agente,
                    itens_id=item["item_id"],
                    nome_item=item["nome"],
                ))
