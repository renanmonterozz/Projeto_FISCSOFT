from __future__ import annotations

from repositories.nota_fiscal_historico_repository import NotaFiscalHistoricoRepository


class NotaFiscalHistoricoService:
    ACOES = NotaFiscalHistoricoRepository.ACOES

    def __init__(self, repository=None):
        self.repository = repository or NotaFiscalHistoricoRepository()

    def listar(self, termo="", acao="Todos", processo="", nota_fiscal="",
               data_inicio=None, data_fim=None):
        return self.repository.listar(
            termo=termo,
            acao=acao,
            processo=processo,
            nota_fiscal=nota_fiscal,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

    def registrar_evento(self, nota_fiscal, processo, acao, agente_matricula=None,
                         usuario=None, motivo=None):
        return self.repository.registrar_evento(
            nota_fiscal=nota_fiscal,
            processo=processo,
            acao=acao,
            agente_matricula=agente_matricula,
            usuario=usuario,
            motivo=motivo,
        )

    @staticmethod
    def rotulo_acao(acao):
        return {
            "ENVIO": "Envio",
            "APROVACAO": "Aprovacao",
            "REJEICAO": "Rejeicao",
            "CORRECAO_SOLICITADA": "Correcao solicitada",
            "REENVIO": "Reenvio",
        }.get(acao, acao or "--")
