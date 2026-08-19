from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from database.models import AgenteIbama, Infrator, Item, ItemSemestre, Tccm
from database.orm import session_scope


class TccmRepository:
    def criar_infrator(self, dados):
        with session_scope() as session:
            infrator = Infrator(
                cpf=dados["cpf"], email=dados["email"], senha="",
                nome_infrator=dados["nome"], telefone_infrator=dados.get("telefone") or None,
            )
            session.add(infrator)

    def criar_agente(self, dados):
        with session_scope() as session:
            agente = AgenteIbama(
                matricula=dados["matricula"], login=dados["login"], senha=dados["senha"],
                email=dados["email"], nome_agente=dados["nome"], cpf=dados["cpf"],
                perfil="agente", status="ativo",
            )
            session.add(agente)

    def listar_dashboard(self):
        with session_scope() as session:
            rows = session.execute(
                select(Tccm, Infrator.nome_infrator, Infrator.cpf)
                .outerjoin(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .order_by(Tccm.processo)
            ).all()
            return [{"processo": t.processo, "total_pago": float(t.total_pago or 0),
                     "total_devido": float(t.total_devido or 0), "status": t.status or "pendente",
                     "data_validade": t.data_validade, "intervalo": t.intervalo or 0,
                     "infrator": nome or "--", "cpf": cpf or "--"} for t, nome, cpf in rows]

    def buscar_detalhes(self, processo):
        with session_scope() as session:
            row = session.execute(
                select(Tccm, Infrator, AgenteIbama)
                .outerjoin(Infrator, Infrator.id_infrator == Tccm.infrator_id)
                .outerjoin(AgenteIbama, AgenteIbama.matricula == Tccm.agente_matricula)
                .where(Tccm.processo == processo)
            ).first()
            if not row:
                return None
            tccm, infrator, agente = row
            return {"processo": tccm.processo, "documento_sei": tccm.documento_sei or "--",
                    "data_inicio": tccm.data_inicio, "semestres": tccm.semestres or 0,
                    "total_pago": float(tccm.total_pago or 0), "data_validade": tccm.data_validade,
                    "total_devido": float(tccm.total_devido or 0), "status": tccm.status or "pendente",
                    "agente_matricula": tccm.agente_matricula, "infrator_id": tccm.infrator_id,
                    "infrator_nome": infrator.nome_infrator if infrator else "--",
                    "infrator_cpf": infrator.cpf if infrator else "--",
                    "infrator_email": infrator.email if infrator else "--",
                    "infrator_telefone": infrator.telefone_infrator if infrator else "--",
                    "agente_nome": agente.nome_agente if agente else "--",
                    "agente_cpf": agente.cpf if agente else "--",
                    "agente_email": agente.email if agente else "--"}
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
