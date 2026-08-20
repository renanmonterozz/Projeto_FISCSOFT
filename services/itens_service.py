from __future__ import annotations

from repositories.itens_repository import ItensRepository
from config.permissoes import normalizar_perfil
from utils import registrar_log


class RegraItemError(ValueError):
    """Erro de regra de negocio do cadastro de item."""


class ItemService:
    def __init__(self, repository=None):
        self.repository = repository or ItensRepository()

    def salvar(self, dados, item_id=None, processo=None, usuario_logado=None):
        dados = dict(dados)
        dados["descricao"] = dados["descricao"] or dados["nome"]
        if item_id:
            self.repository.atualizar(item_id, dados, processo)
            mensagem = f"Item '{dados['nome']}' atualizado com sucesso!"
            acao = "edicao"
        else:
            self.repository.criar(dados, processo)
            mensagem = f"Item '{dados['nome']}' cadastrado com sucesso!"
            acao = "cadastro"

        registrar_log(usuario_logado or "Sistema", acao, "itens", mensagem)
        return mensagem

    def listar(self, processo=None, semestre_atual=False):
        itens = self.repository.listar(processo, semestre_atual)
        for item in itens:
            item["quantidade_restante"] = max(
                (item.get("quantidade_prevista") or 0) - (item.get("qtd_entregue") or 0),
                0,
            )
        return itens

    def listar_notas_do_item(self, item_id, processo):
        if not processo:
            raise RegraItemError("Selecione um TCCM para consultar as notas vinculadas.")
        if not item_id:
            raise RegraItemError("Selecione um item para consultar as notas vinculadas.")
        return self.repository.listar_notas_do_item(item_id, processo)

    def pesquisar(self, itens, busca=""):
        return filtrar_itens(itens, busca)

    def listar_para_exportacao(self, processo=None):
        return self.repository.listar_para_exportacao(processo)

    def desativar(self, item, usuario_logado=None, perfil=None, processo=None, motivo=None):
        if normalizar_perfil(perfil) != "admin":
            raise RegraItemError("A desativacao de itens exige permissao de administrador.")
        motivo = (motivo or "").strip()
        if not motivo:
            raise RegraItemError("Informe o motivo da desativacao do item.")
        self.repository.desativar(item["id"])
        usuario = usuario_logado or "Sistema"
        mensagem = (
            f"DESATIVACAO_ITEM item_id={item['id']} "
            f"tccm_id={processo or item.get('processo') or '--'} "
            f"motivo={motivo}"
        )
        registrar_log(usuario, "DESATIVACAO_ITEM", "itens", mensagem)
        return mensagem

    def listar_historico(self, processo=None):
        return self.repository.listar_historico(processo)

    def excluir(self, item, usuario_logado=None, perfil=None, processo=None, motivo=None):
        return self.desativar(item, usuario_logado, perfil, processo, motivo)


def validar_dados_item(nome, descricao, tipo, unidade, justificativa, quantidade):
    dados = {
        "nome": (nome or "").strip(),
        "descricao": (descricao or "").strip(),
        "tipo": (tipo or "").strip(),
        "unidade": (unidade or "").strip(),
        "justificativa": (justificativa or "").strip(),
        "quantidade": (quantidade or "").strip(),
    }

    if not dados["nome"] or not dados["justificativa"] or not dados["quantidade"]:
        raise RegraItemError(
            "Preencha nome, justificativa e quantidade prevista!"
        )

    try:
        dados["quantidade"] = int(dados["quantidade"])
    except ValueError as exc:
        raise RegraItemError(
            "Qtd. Prevista deve ser um numero inteiro!"
        ) from exc

    return dados


def filtrar_itens(itens, busca=""):
    busca = (busca or "").strip().lower()
    if not busca:
        return list(itens)
    return [
        item for item in itens
        if busca in item["nome"].lower()
        or busca in item["descricao"].lower()
        or busca in item["tipo"].lower()
        or busca in item.get("justificativa", "").lower()
        or busca in item.get("unidade_medida", "").lower()
    ]
