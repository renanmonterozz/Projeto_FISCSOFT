from __future__ import annotations

from screens.repository.destinacao_repository import DestinacaoRepository
from utils import registrar_log


class RegraDestinacaoError(ValueError):
    """Erro de regra de negocio da destinacao."""


class DestinacaoService:
    def __init__(self, repository=None):
        self.repository = repository or DestinacaoRepository()

    def listar_locais(self):
        return self.repository.listar_locais()

    def listar_itens(self, processo=None):
        return self.repository.listar_itens(processo)

    def salvar_local(self, cep, endereco, instituicao, responsavel, telefone, usuario_logado=None):
        dados = {
            "cep": (cep or "").strip(),
            "endereco": (endereco or "").strip(),
            "instituicao": (instituicao or "").strip(),
            "responsavel": (responsavel or "").strip(),
            "telefone": (telefone or "").strip(),
        }
        validar_local(
            dados["cep"],
            dados["endereco"],
            dados["instituicao"],
            dados["responsavel"],
        )
        self.repository.criar_local(dados)
        mensagem = f"Local '{dados['instituicao']}' cadastrado via Relatorio de Entrega"
        registrar_log(usuario_logado or "Sistema", "cadastro", "locais", mensagem)
        return mensagem


def item_display(item):
    nome = item.get("nome") or item.get("item") or ""
    descricao = item.get("descricao")
    if descricao and descricao != nome:
        return f"{nome} ({descricao})"
    return nome


def quantidade_disponivel(item_catalogo, itens_adicionados, item_id):
    item = next((item for item in item_catalogo if item.get("id") == item_id), None)
    if item is None:
        return None

    quantidade_maxima = item.get("quantidade") or 0
    if quantidade_maxima <= 0:
        return None

    quantidade_usada = sum(
        item.get("quantidade", 0)
        for item in itens_adicionados
        if item.get("item_id") == item_id
    )
    return max(0, quantidade_maxima - quantidade_usada)


def preparar_item(display, quantidade, item_catalogo, itens_adicionados):
    display = (display or "").strip()
    quantidade = (quantidade or "").strip()

    if not display or "Nenhum item" in display:
        raise RegraDestinacaoError("Selecione um item do catalogo.")
    if not quantidade:
        raise RegraDestinacaoError("Preencha a quantidade.")

    try:
        quantidade_int = int(quantidade)
    except ValueError as exc:
        raise RegraDestinacaoError(
            "Quantidade deve ser um numero inteiro positivo."
        ) from exc

    if quantidade_int <= 0:
        raise RegraDestinacaoError("Quantidade deve ser um numero inteiro positivo.")

    item = next((item for item in item_catalogo if item_display(item) == display), None)
    if item is None:
        raise RegraDestinacaoError("Item nao encontrado no catalogo.")

    disponivel = quantidade_disponivel(item_catalogo, itens_adicionados, item["id"])
    if disponivel is not None and quantidade_int > disponivel:
        raise RegraDestinacaoError(
            f"Quantidade maxima permitida para '{item['nome']}' e {disponivel}."
        )

    return {
        "item_id": item["id"],
        "item": item["nome"],
        "descricao": item.get("descricao"),
        "quantidade": quantidade_int,
    }


def validar_local(cep, endereco, instituicao, responsavel):
    if not all((cep, endereco, instituicao, responsavel)):
        raise RegraDestinacaoError(
            "Preencha CEP, Endereco, Instituicao e Responsavel."
        )


def gerar_texto_relatorio(processo, documento_sei, responsavel, observacoes, itens):
    texto = "RELATORIO DE ENTREGA DE MATERIAIS\n"
    texto += "=" * 40 + "\n\n"
    texto += f"Processo: {processo or 'N/A'}\n"
    texto += f"Documento SEI: {documento_sei or 'N/A'}\n"
    texto += f"Responsavel: {responsavel or 'N/A'}\n"
    if observacoes:
        texto += f"Observacoes: {observacoes}\n"
    texto += "\nITENS:\n"
    texto += "-" * 40 + "\n"
    for item in itens:
        texto += f"  {item['item']}: {item['quantidade']}\n"
    texto += "-" * 40 + "\n"
    texto += f"Total de Itens: {sum(item['quantidade'] for item in itens)}\n"
    return texto
