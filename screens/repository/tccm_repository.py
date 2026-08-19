from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from database.models import AgenteIbama, Infrator, Item, ItemSemestre, Tccm
from database.orm import session_scope


class TccmRepository:
    def listar_agentes(self):
        with session_scope() as session:
            agentes = session.scalars(
                select(AgenteIbama)
                .where(AgenteIbama.status == "ativo")
                .order_by(AgenteIbama.nome_agente)
            ).all()
            return [(agente.matricula, agente.nome_agente) for agente in agentes]

    def listar_infratores(self):
        with session_scope() as session:
            infratores = session.scalars(
                select(Infrator).order_by(Infrator.nome_infrator)
            ).all()
            return [(infrator.id_infrator, infrator.nome_infrator) for infrator in infratores]

    def listar_itens_processo(self, processo):
        with session_scope() as session:
            itens = session.scalars(
                select(Item)
                .where(Item.processo == processo)
                .order_by(Item.id)
            ).all()
            return [
                {
                    "nome": item.nome,
                    "descricao": item.descricao,
                    "tipo": item.tipo,
                    "justificativa": item.justificativa,
                    "quantidade": item.quantidade_prevista,
                    "unidade_medida": item.unidade_medida,
                }
                for item in itens
            ]

    def criar_com_itens(self, dados, itens):
        with session_scope() as session:
            tccm = Tccm(
                processo=dados["processo"],
                documento_sei=dados["documento_sei"] or None,
                data_inicio=datetime.strptime(dados["data_inicio_db"], "%Y-%m-%d").date(),
                semestres=dados["semestres"],
                total_pago=0,
                total_validado=0,
                total_devido=dados["total_devido"],
                data_validade=None,
                intervalo=dados["semestres"],
                status="pendente",
                agente_matricula=dados["agente_matricula"],
                infrator_id=dados["infrator_id"],
            )
            session.add(tccm)
            session.flush()

            for item_dados in itens:
                item = Item(
                    nome=item_dados["nome"],
                    descricao=item_dados["descricao"],
                    codigo_interno=f"{dados['processo']}-{item_dados['nome'][:10].upper()}",
                    tipo=item_dados["tipo"],
                    justificativa=item_dados["justificativa"],
                    unidade_medida=item_dados["unidade_medida"],
                    quantidade_prevista=item_dados.get("quantidade") or 0,
                    status="Ativo",
                    processo=dados["processo"],
                )
                session.add(item)
                session.flush()

                data_inicio = tccm.data_inicio
                inicio_semestre = 1 if data_inicio.month <= 6 else 2
                for indice, quantidade in enumerate(item_dados.get("quantidades_semestre") or []):
                    deslocamento = inicio_semestre - 1 + indice
                    session.add(ItemSemestre(
                        itens_id=item.id,
                        ano=data_inicio.year + deslocamento // 2,
                        semestre=deslocamento % 2 + 1,
                        quantidade_prevista=quantidade,
                        processo=dados["processo"],
                    ))

            return dados["processo"]
