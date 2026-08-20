from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select, update

from database.models import (
    AgenteIbama,
    Infrator,
    Item,
    NotaFiscal,
    NotaFiscalHistorico,
    Produto,
    Tccm,
)
from database.orm import session_scope


class NotasFiscaisRepository:
    @staticmethod
    def _registrar_historico(session, nota, acao, motivo=None, agente_id=None, usuario=None):
        session.add(NotaFiscalHistorico(
            nota_fiscal=nota.nota_fiscal,
            processo=nota.processo,
            agente_matricula=agente_id,
            usuario=usuario,
            acao=acao,
            motivo=motivo,
        ))

    def listar_pendencias_alerta(self, tccm_id=None):
        with session_scope() as session:
            statement = (
                select(NotaFiscal.processo, func.count(NotaFiscal.nota_fiscal))
                .where(NotaFiscal.status_nota.not_in(("Aprovada", "Rejeitada")))
                .group_by(NotaFiscal.processo)
            )
            if tccm_id:
                statement = statement.where(NotaFiscal.processo == tccm_id)
            return [(processo, quantidade) for processo, quantidade in session.execute(statement).all()]

    def listar_processos_com_correcao(self, tccm_id=None):
        with session_scope() as session:
            statement = (
                select(NotaFiscal.processo)
                .where(NotaFiscal.status_nota == "Correcao Solicitada")
                .distinct()
            )
            if tccm_id:
                statement = statement.where(NotaFiscal.processo == tccm_id)
            return list(session.scalars(statement).all())

    def listar_por_tccm(self, tccm_id):
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
            statement = statement.where(NotaFiscal.processo == tccm_id)
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

    def listar_monitoramento(self, processo=None):
        return self.listar_por_tccm(processo) if processo else []

    def buscar_por_id_e_tccm(self, nota_id, tccm_id):
        with session_scope() as session:
            return session.scalar(
                select(NotaFiscal).where(
                    NotaFiscal.nota_fiscal == nota_id,
                    NotaFiscal.processo == tccm_id,
                )
            )

    def buscar_agente_id(self, nome):
        with session_scope() as session:
            agente = session.scalar(
                select(AgenteIbama).where(
                    (AgenteIbama.nome_agente == nome) | (AgenteIbama.login == nome)
                )
            )
            return agente.matricula if agente else None

    def atualizar_status(
        self, nota_fiscal, matricula, tccm_id, novo_status,
        agente_id=None, motivo=None, usuario=None,
    ):
        with session_scope() as session:
            nota = session.scalar(
                select(NotaFiscal).where(
                    NotaFiscal.nota_fiscal == nota_fiscal,
                    NotaFiscal.agente_matricula == matricula,
                    NotaFiscal.processo == tccm_id,
                )
            )
            if nota is None:
                raise LookupError("Nota fiscal nao encontrada neste TCCM.")
            if nota.status_nota in ("Aprovada", "Rejeitada"):
                raise ValueError("Esta nota fiscal ja foi finalizada.")
            if novo_status == "Aprovada":
                if agente_id is None:
                    raise ValueError("Agente responsavel nao informado.")
                produtos = session.scalars(
                    select(Produto).where(
                        Produto.nota_fiscal == nota_fiscal,
                        Produto.agente_matricula == matricula,
                    )
                ).all()
                if not produtos:
                    raise ValueError("A nota fiscal nao possui itens.")
                itens = {}
                for produto in produtos:
                    if produto.quantidade <= 0 or produto.itens_id is None:
                        raise ValueError("A nota fiscal possui item ou quantidade invalida.")
                    item = session.get(Item, produto.itens_id)
                    if item is None or item.status != "Ativo" or item.processo != tccm_id:
                        raise ValueError("A nota fiscal possui item invalido para o TCCM.")
                    disponivel = (item.quantidade_prevista or 0) - (item.quantidade_entregue or 0)
                    if produto.quantidade > disponivel:
                        raise ValueError(f"Quantidade excede o previsto para o item '{item.nome}'.")
                    if item.id in itens:
                        itens[item.id] = (item, itens[item.id][1] + produto.quantidade)
                    else:
                        itens[item.id] = (item, produto.quantidade)

                soma = sum(produto.quantidade * produto.preco_unitario for produto in produtos)
                tccm = session.scalar(select(Tccm).where(Tccm.processo == tccm_id))
                if tccm is None:
                    raise LookupError("TCCM nao encontrado.")
                for item, quantidade in itens.values():
                    disponivel = (item.quantidade_prevista or 0) - (item.quantidade_entregue or 0)
                    if quantidade > disponivel:
                        raise ValueError(f"Quantidade excede o previsto para o item '{item.nome}'.")
                    item.quantidade_entregue = (item.quantidade_entregue or 0) + quantidade
                nota.valor_total = soma
                tccm.total_pago = (tccm.total_pago or 0) + soma
                tccm.status = "concluido" if tccm.total_pago >= tccm.total_devido else "pendente"
                nota.agente_decisao = agente_id
                nota.data_decisao = datetime.now()
                self._registrar_historico(
                    session, nota, "APROVACAO", agente_id=agente_id, usuario=usuario
                )
            elif novo_status == "Rejeitada":
                nota.agente_decisao = agente_id
                nota.data_decisao = datetime.now()
                self._registrar_historico(
                    session, nota, "REJEICAO", motivo, agente_id, usuario
                )
            elif novo_status == "Correcao Solicitada":
                nota.agente_decisao = agente_id
                nota.data_decisao = datetime.now()
                self._registrar_historico(
                    session, nota, "CORRECAO_SOLICITADA", motivo, agente_id, usuario
                )
            nota.status_nota = novo_status

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
                "matricula": nota.agente_matricula,
                "arquivo": nota.arquivo,
                "processo": processo,
                "itens": [
                    {"item_id": p.itens_id, "nome": p.nome_item or "--", "quantidade": p.quantidade or 0,
                     "preco_unitario": p.preco_unitario or 0,
                     "subtotal": (p.quantidade or 0) * (p.preco_unitario or 0)}
                    for p in produtos
                ],
            }

    def reenviar_nota(self, nota_fiscal, processo, infrator_id, dados, itens, usuario=None):
        with session_scope() as session:
            nota = session.scalar(
                select(NotaFiscal)
                .join(Tccm, Tccm.processo == NotaFiscal.processo)
                .where(
                    NotaFiscal.nota_fiscal == nota_fiscal,
                    NotaFiscal.processo == processo,
                    Tccm.infrator_id == infrator_id,
                )
            )
            if nota is None:
                raise LookupError("Nota fiscal nao encontrada neste TCCM.")

            numero_anterior = nota.nota_fiscal
            matricula = nota.agente_matricula

            session.execute(delete(Produto).where(
                Produto.nota_fiscal == nota_fiscal,
                Produto.agente_matricula == matricula,
            ))
            session.flush()

            nota.nota_fiscal = dados["numero"]
            nota.chave_de_acesso = dados["chave"]
            nota.data = datetime.strptime(dados["data"], "%Y-%m-%d").date()
            nota.valor_total = dados["valor_total"]
            nota.arquivo = dados.get("arquivo")
            nota.status_nota = "Pendente"
            nota.agente_decisao = None
            nota.data_decisao = None

            if numero_anterior != dados["numero"]:
                session.execute(
                    update(NotaFiscalHistorico)
                    .where(
                        NotaFiscalHistorico.nota_fiscal == numero_anterior,
                        NotaFiscalHistorico.processo == processo,
                    )
                    .values(nota_fiscal=dados["numero"])
                )

            for indice, item in enumerate(itens, start=1):
                session.add(Produto(
                    lote=f"{dados['numero']}-ITEM-{indice}",
                    status_entrega="pendente",
                    quantidade=item["quantidade"],
                    preco_unitario=item["preco_unitario"],
                    nota_fiscal=dados["numero"],
                    agente_matricula=matricula,
                    itens_id=item["item_id"],
                    nome_item=item["nome"],
                ))
            self._registrar_historico(session, nota, "REENVIO", usuario=usuario)

    def listar_historico(self, nota_fiscal, processo=None):
        with session_scope() as session:
            statement = select(NotaFiscalHistorico).where(
                NotaFiscalHistorico.nota_fiscal == nota_fiscal,
            )
            if processo:
                statement = statement.where(NotaFiscalHistorico.processo == processo)
            return [
                {
                    "nota_fiscal": registro.nota_fiscal,
                    "processo": registro.processo,
                    "agente_matricula": registro.agente_matricula,
                    "usuario": registro.usuario,
                    "acao": registro.acao,
                    "motivo": registro.motivo,
                    "criado_em": registro.criado_em,
                }
                for registro in session.scalars(
                    statement.order_by(NotaFiscalHistorico.criado_em.asc())
                ).all()
            ]
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
            self._registrar_historico(
                session, nota, "ENVIO", usuario=dados.get("usuario")
            )
