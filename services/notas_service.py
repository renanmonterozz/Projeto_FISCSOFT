from __future__ import annotations

from datetime import datetime

from repositories.notas_fiscais_repository import NotasFiscaisRepository


class RegraNotaError(ValueError):
    """Erro de regra de negocio da nota fiscal."""


class NotasFiscaisService:
    STATUS_PENDENTE = "Pendente"
    STATUS_APROVADA = "Aprovada"
    STATUS_REJEITADA = "Rejeitada"
    STATUS_CORRECAO = "Correcao Solicitada"

    def __init__(self, repository=None):
        self.repository = repository or NotasFiscaisRepository()
        self._agente_logado = None

    def listar_processos(self, infrator_id):
        return self.repository.listar_processos(infrator_id)

    def listar_itens_processo(self, processo):
        return self.repository.listar_itens_processo(processo)

    def salvar(self, numero, chave, data, processo, itens, arquivo=None, usuario_id=None):
        numero = (numero or "").strip()
        chave = (chave or "").strip()
        processo = (processo or "").strip()
        if not numero or not chave or not processo:
            raise RegraNotaError("Preencha todos os campos obrigatorios.")
        if not itens:
            raise RegraNotaError("Adicione pelo menos um item a nota fiscal.")
        try:
            data_db = datetime.strptime(data.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except (AttributeError, ValueError) as exc:
            raise RegraNotaError("Data invalida. Use o formato dd/mm/aaaa.") from exc
        dados = {
            "numero": numero,
            "chave": chave,
            "data": data_db,
            "processo": processo,
            "valor_total": sum(item["subtotal"] for item in itens),
            "arquivo": arquivo,
            "usuario": str(usuario_id) if usuario_id is not None else None,
        }
        self.repository.criar_nota(dados, itens)
        return dados["valor_total"]

    def listar_por_tccm(self, tccm_id):
        tccm_id = (tccm_id or "").strip()
        if not tccm_id:
            raise RegraNotaError("Selecione um TCCM para consultar as notas fiscais.")
        return self.repository.listar_por_tccm(tccm_id)

    def listar_pendencias_alerta(self, tccm_id=None):
        return self.repository.listar_pendencias_alerta(tccm_id)

    def listar_processos_com_correcao(self, tccm_id=None):
        return self.repository.listar_processos_com_correcao(tccm_id)

    def listar_monitoramento(self, processo=None):
        return self.listar_por_tccm(processo)

    def atualizar_status(self, nota, novo_status, tccm_id, motivo=None):
        tccm_id = (tccm_id or "").strip()
        if not tccm_id:
            raise RegraNotaError("Selecione um TCCM para alterar a nota fiscal.")
        transicoes = {
            self.STATUS_APROVADA,
            self.STATUS_REJEITADA,
            self.STATUS_CORRECAO,
        }
        if novo_status not in transicoes:
            raise RegraNotaError("Transicao de status da nota fiscal invalida.")
        if nota.get("processo") != tccm_id:
            raise RegraNotaError("A nota fiscal nao pertence ao TCCM selecionado.")
        if novo_status in {self.STATUS_REJEITADA, self.STATUS_CORRECAO}:
            motivo = (motivo or "").strip()
            if not motivo:
                raise RegraNotaError("Informe o motivo da operacao.")
        nota_atual = self.repository.buscar_por_id_e_tccm(nota["nota_fiscal"], tccm_id)
        if nota_atual is None:
            raise RegraNotaError("Nota fiscal nao encontrada neste TCCM.")
        if nota_atual.status_nota != self.STATUS_PENDENTE:
            raise RegraNotaError("Somente notas pendentes podem ser alteradas.")
        agente_id = self.repository.buscar_agente_id(self._agente_logado)
        if agente_id is None:
            raise RegraNotaError("Agente responsavel nao encontrado.")
        self.repository.atualizar_status(
            nota["nota_fiscal"], nota_atual.agente_matricula, tccm_id, novo_status,
            agente_id, motivo, self._agente_logado,
        )

    def aprovar_nota(self, nota, tccm_id):
        self.atualizar_status(nota, self.STATUS_APROVADA, tccm_id)

    def aprovar(self, nota, tccm_id):
        self.aprovar_nota(nota, tccm_id)

    def rejeitar_nota(self, nota, tccm_id, motivo):
        motivo = (motivo or "").strip()
        if not motivo:
            raise RegraNotaError("Informe o motivo da rejeicao.")
        self.atualizar_status(nota, self.STATUS_REJEITADA, tccm_id, motivo)

    def rejeitar(self, nota, tccm_id, motivo):
        self.rejeitar_nota(nota, tccm_id, motivo)

    def solicitar_correcao(self, nota, tccm_id, motivo):
        motivo = (motivo or "").strip()
        if not motivo:
            raise RegraNotaError("Informe o motivo da correcao.")
        self.atualizar_status(nota, self.STATUS_CORRECAO, tccm_id, motivo)

    def reenviar_nota(self, nota_fiscal, processo, infrator_id, dados, itens):
        processo = (processo or "").strip()
        if not processo or not infrator_id:
            raise RegraNotaError("TCCM e infrator sao obrigatorios.")
        if not dados.get("numero") or not dados.get("chave") or not dados.get("data"):
            raise RegraNotaError("Preencha os dados obrigatorios da nota fiscal.")
        if not itens:
            raise RegraNotaError("Adicione pelo menos um item a nota fiscal.")

        atual = self.repository.buscar_detalhes(nota_fiscal, infrator_id)
        if not atual or atual.get("processo") != processo:
            raise RegraNotaError("A nota fiscal nao pertence ao TCCM informado.")
        if atual.get("status") != "Correcao Solicitada":
            raise RegraNotaError("Somente notas com correcao solicitada podem ser reenviadas.")

        for item in itens:
            if item.get("item_id") is None or item.get("quantidade", 0) <= 0 or item.get("preco_unitario", 0) <= 0:
                raise RegraNotaError("A nota fiscal possui item ou quantidade invalida.")
        dados = dict(dados)
        dados["valor_total"] = sum(item["subtotal"] for item in itens)
        self.repository.reenviar_nota(
            nota_fiscal, processo, infrator_id, dados, itens, usuario=str(infrator_id)
        )
        return dados["valor_total"]

    def listar_historico(self, nota_fiscal, processo=None):
        return self.repository.listar_historico(nota_fiscal, processo)

    def definir_agente_logado(self, nome):
        self._agente_logado = nome

    def buscar_detalhes(self, nota_fiscal, infrator_id):
        return self.repository.buscar_detalhes(nota_fiscal, infrator_id)


def preparar_item_nota(display, quantidade, preco_unitario, itens_catalogo):
    display = (display or "").strip()
    quantidade = (quantidade or "").strip()
    preco_unitario = (preco_unitario or "").strip()

    if not display or any(texto in display for texto in ("Nenhum item", "Selecione", "Erro")):
        raise RegraNotaError("Selecione um item do TCCM.")
    if not quantidade or not preco_unitario:
        raise RegraNotaError("Preencha quantidade e preco unitario.")

    try:
        quantidade_int = int(quantidade)
        if quantidade_int <= 0:
            raise ValueError
    except ValueError as exc:
        raise RegraNotaError("Quantidade invalida.") from exc

    try:
        preco = float(preco_unitario.replace(".", "").replace(",", "."))
        if preco <= 0:
            raise ValueError
    except ValueError as exc:
        raise RegraNotaError("Preco unitario invalido.") from exc

    item_info = next(
        (
            item for item in itens_catalogo
            if f"{item['nome']} ({item['descricao']})" == display
        ),
        None,
    )
    if item_info is None:
        raise RegraNotaError("Item nao encontrado no TCCM.")

    return {
        "item_id": item_info["id"],
        "nome": item_info["nome"],
        "descricao": item_info["descricao"],
        "quantidade": quantidade_int,
        "preco_unitario": preco,
        "subtotal": quantidade_int * preco,
    }
