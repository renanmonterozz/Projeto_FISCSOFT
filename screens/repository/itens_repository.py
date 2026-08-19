from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from database.models import Item, ItemSemestre, Tccm
from database.orm import session_scope


class ItensRepository:
    def criar(self, dados, processo=None):
        with session_scope() as session:
            proximo_id = (session.scalar(select(func.max(Item.id))) or 0) + 1
            item = Item(
                nome=dados["nome"],
                descricao=dados["descricao"] or dados["nome"],
                codigo_interno=f"IT-{proximo_id:03d}",
                tipo=dados["tipo"],
                justificativa=dados["justificativa"],
                unidade_medida=dados["unidade"],
                quantidade_prevista=dados["quantidade"],
                status="Ativo",
                processo=processo,
            )
            session.add(item)
            session.flush()
            self._salvar_quantidades_semestre(session, item.id, dados["quantidade"], processo)
            return item.id

    def atualizar(self, item_id, dados, processo=None):
        with session_scope() as session:
            item = session.get(Item, item_id)
            if item is None:
                raise LookupError("Item nao encontrado.")
            item.nome = dados["nome"]
            item.descricao = dados["descricao"] or dados["nome"]
            item.tipo = dados["tipo"]
            item.justificativa = dados["justificativa"]
            item.unidade_medida = dados["unidade"]
            item.quantidade_prevista = dados["quantidade"]
            self._salvar_quantidades_semestre(session, item.id, dados["quantidade"], processo)

    @staticmethod
    def _salvar_quantidades_semestre(session, item_id, quantidade, processo):
        tccm = None
        if processo:
            tccm = session.scalar(select(Tccm).where(Tccm.processo == processo))

        if tccm and tccm.semestres:
            data_inicio = tccm.data_inicio
            total_semestres = int(tccm.semestres) or 1
        else:
            data_inicio = datetime.now()
            total_semestres = 1

        if isinstance(data_inicio, str):
            try:
                data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            except ValueError:
                data_inicio = datetime.now()
        if not data_inicio:
            data_inicio = datetime.now()

        inicio_semestre = 1 if data_inicio.month <= 6 else 2
        base, resto = divmod(quantidade, total_semestres)

        for indice in range(total_semestres):
            deslocamento = (inicio_semestre - 1) + indice
            ano = data_inicio.year + deslocamento // 2
            semestre = deslocamento % 2 + 1
            quantidade_semestre = base + (1 if indice < resto else 0)
            existente = session.scalar(
                select(ItemSemestre).where(
                    ItemSemestre.itens_id == item_id,
                    ItemSemestre.ano == ano,
                    ItemSemestre.semestre == semestre,
                )
            )
            if existente:
                existente.quantidade_prevista = quantidade_semestre
                existente.processo = processo
            else:
                session.add(ItemSemestre(
                    itens_id=item_id,
                    ano=ano,
                    semestre=semestre,
                    quantidade_prevista=quantidade_semestre,
                    processo=processo,
                ))