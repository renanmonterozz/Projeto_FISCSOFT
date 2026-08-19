from __future__ import annotations


class RegraNotaError(ValueError):
    """Erro de regra de negocio da nota fiscal."""


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
