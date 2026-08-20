from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import or_, select

from database.models import NotaFiscalHistorico
from database.orm import session_scope


class NotaFiscalHistoricoRepository:
    ACOES = ("ENVIO", "APROVACAO", "REJEICAO", "CORRECAO_SOLICITADA", "REENVIO")

    def listar(self, termo="", acao="Todos", processo="", nota_fiscal="",
               data_inicio: date | None = None, data_fim: date | None = None):
        with session_scope() as session:
            statement = select(NotaFiscalHistorico).order_by(
                NotaFiscalHistorico.criado_em.desc(), NotaFiscalHistorico.id.desc()
            )
            termo = (termo or "").strip()
            processo = (processo or "").strip()
            nota_fiscal = (nota_fiscal or "").strip()

            if termo:
                like = f"%{termo}%"
                statement = statement.where(or_(
                    NotaFiscalHistorico.nota_fiscal.ilike(like),
                    NotaFiscalHistorico.processo.ilike(like),
                    NotaFiscalHistorico.usuario.ilike(like),
                    NotaFiscalHistorico.motivo.ilike(like),
                    NotaFiscalHistorico.acao.ilike(like),
                ))
            if acao and acao != "Todos":
                statement = statement.where(NotaFiscalHistorico.acao == acao)
            if processo:
                statement = statement.where(NotaFiscalHistorico.processo.ilike(f"%{processo}%"))
            if nota_fiscal:
                statement = statement.where(NotaFiscalHistorico.nota_fiscal.ilike(f"%{nota_fiscal}%"))
            if data_inicio:
                statement = statement.where(NotaFiscalHistorico.criado_em >= datetime.combine(data_inicio, datetime.min.time()))
            if data_fim:
                statement = statement.where(NotaFiscalHistorico.criado_em < datetime.combine(data_fim, datetime.max.time()))

            return [
                {
                    "id": registro.id,
                    "nota_fiscal": registro.nota_fiscal,
                    "processo": registro.processo,
                    "agente_matricula": registro.agente_matricula,
                    "usuario": registro.usuario,
                    "acao": registro.acao,
                    "motivo": registro.motivo,
                    "criado_em": registro.criado_em,
                }
                for registro in session.scalars(statement).all()
            ]

    def registrar_evento(self, nota_fiscal, processo, acao, agente_matricula=None,
                         usuario=None, motivo=None):
        if acao not in self.ACOES:
            raise ValueError("Acao de auditoria invalida.")
        with session_scope() as session:
            session.add(NotaFiscalHistorico(
                nota_fiscal=nota_fiscal,
                processo=processo,
                agente_matricula=agente_matricula,
                usuario=usuario,
                acao=acao,
                motivo=motivo,
            ))
