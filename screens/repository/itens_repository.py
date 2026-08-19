from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select

from database.models import Item, ItemSemestre, NotaFiscal, Produto, Tccm
from database.orm import session_scope


class ItensRepository:
    def listar(self, processo=None, semestre_atual=False):
        semestre = self._semestre_atual() if semestre_atual else None
        quantidade_prevista = Item.quantidade_prevista
        if semestre:
            ano, numero, inicio, fim = semestre
            quantidade_prevista = func.coalesce(
                select(ItemSemestre.quantidade_prevista)
                .where(
                    ItemSemestre.itens_id == Item.id,
                    ItemSemestre.ano == ano,
                    ItemSemestre.semestre == numero,
                )
                .scalar_subquery(),
                Item.quantidade_prevista,
            )

        entregue = select(func.sum(Produto.quantidade)).join(
            NotaFiscal,
            (NotaFiscal.nota_fiscal == Produto.nota_fiscal)
            & (NotaFiscal.agente_matricula == Produto.agente_matricula),
        ).where(Produto.itens_id == Item.id)
        if semestre:
            entregue = entregue.where(NotaFiscal.data >= inicio, NotaFiscal.data <= fim)
        entregue = func.coalesce(entregue.scalar_subquery(), 0)

        statement = select(Item, quantidade_prevista, entregue)
        if processo:
            itens_por_nota = select(NotaFiscal.nota_fiscal).where(NotaFiscal.processo == processo)
            statement = statement.where(
                (Item.processo == processo) | Item.notas_fiscais.in_(itens_por_nota)
            )
        statement = statement.order_by(Item.id)

        with session_scope() as session:
            rows = session.execute(statement).all()
        itens = [
            {
                "id": item.id,
                "nome": item.nome or "-",
                "descricao": item.descricao or "-",
                "tipo": item.tipo or "-",
                "justificativa": item.justificativa or "",
                "unidade_medida": item.unidade_medida or "",
                "quantidade_prevista": quantidade or 0,
                "qtd_entregue": entregue or 0,
            }
            for item, quantidade, entregue in rows
        ]
        return itens

    def listar_para_exportacao(self, processo=None):
        with session_scope() as session:
            statement = select(Item).order_by(Item.id)
            if processo:
                statement = statement.where(Item.processo == processo)
            itens = session.scalars(statement).all()
            ids = [item.id for item in itens]
            if not ids:
                return [], [], {}
            semestres = session.execute(
                select(ItemSemestre.ano, ItemSemestre.semestre)
                .where(ItemSemestre.itens_id.in_(ids))
                .distinct()
                .order_by(ItemSemestre.ano, ItemSemestre.semestre)
            ).all()
            quantidades = session.execute(
                select(ItemSemestre.itens_id, ItemSemestre.ano, ItemSemestre.semestre, ItemSemestre.quantidade_prevista)
                .where(ItemSemestre.itens_id.in_(ids))
            ).all()
            dados = [
                {
                    "id": item.id,
                    "nome": item.nome,
                    "descricao": item.descricao,
                    "tipo": item.tipo,
                    "justificativa": item.justificativa,
                    "unidade_medida": item.unidade_medida,
                }
                for item in itens
            ]
            mapa = {(item_id, ano, semestre): quantidade for item_id, ano, semestre, quantidade in quantidades}
            return dados, [(ano, semestre) for ano, semestre in semestres], mapa

    def excluir(self, item_id):
        with session_scope() as session:
            session.execute(delete(ItemSemestre).where(ItemSemestre.itens_id == item_id))
            session.execute(delete(Item).where(Item.id == item_id))

    @staticmethod
    def _semestre_atual():
        now = datetime.now()
        if now.month <= 6:
            return now.year, 1, f"{now.year}-01-01", f"{now.year}-06-30"
        return now.year, 2, f"{now.year}-07-01", f"{now.year}-12-31"

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