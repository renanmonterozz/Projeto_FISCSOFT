from __future__ import annotations

from datetime import datetime

from screens.repository.notas_fiscais_repository import NotasFiscaisRepository


class RegraNotaError(ValueError):
    """Erro de regra de negocio da nota fiscal."""


class NotasFiscaisService:
    def __init__(self, repository=None):
        self.repository = repository or NotasFiscaisRepository()

    def listar_processos(self, infrator_id):
        return self.repository.listar_processos(infrator_id)

    def listar_itens_processo(self, processo):
        return self.repository.listar_itens_processo(processo)

    def salvar(self, numero, chave, data, processo, itens, arquivo=None):
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
        }
        self.repository.criar_nota(dados, itens)
        return dados["valor_total"]

    def listar_monitoramento(self, processo=None):
        return self.repository.listar_monitoramento(processo)

    def atualizar_status(self, nota, novo_status):
        self.repository.atualizar_status(
            nota["nota_fiscal"], nota["matricula"], nota.get("processo"), novo_status
        )

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
