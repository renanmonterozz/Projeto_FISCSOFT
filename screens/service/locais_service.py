from __future__ import annotations

from screens.repository.locais_repository import LocaisRepository
from utils import registrar_log


class RegraLocalError(ValueError):
    """Erro de regra de negocio do cadastro de local."""


class LocalService:
    def __init__(self, repository=None):
        self.repository = repository or LocaisRepository()

    def listar(self):
        return self.repository.listar()

    def pesquisar(self, termo=""):
        return filtrar_locais(self.listar(), termo)

    def salvar(self, dados, local_id=None, usuario_logado=None):
        dados = {
            "cep": (dados.get("cep") or "").strip(),
            "endereco": (dados.get("endereco") or "").strip(),
            "instituicao": (dados.get("instituicao") or "").strip(),
            "responsavel": (dados.get("responsavel") or "").strip(),
            "telefone": (dados.get("telefone") or "").strip(),
        }
        if not all((dados["cep"], dados["endereco"], dados["instituicao"], dados["responsavel"])):
            raise RegraLocalError("Preencha CEP, Endereco, Instituicao e Responsavel.")

        if local_id:
            self.repository.atualizar(local_id, dados)
            mensagem = "Local atualizado com sucesso!"
            acao = "edicao"
        else:
            self.repository.criar(dados)
            mensagem = "Local cadastrado com sucesso!"
            acao = "cadastro"
        registrar_log(usuario_logado or "Sistema", acao, "locais", mensagem)
        return mensagem

    def excluir(self, local, usuario_logado=None):
        self.repository.excluir(local["id"])
        mensagem = f"Local '{local['instituicao']}' (ID: {local['id']}) excluido"
        registrar_log(usuario_logado or "Sistema", "exclusao", "locais", mensagem)
        return mensagem


def filtrar_locais(locais, termo=""):
    termo = (termo or "").strip().lower()
    if not termo:
        return list(locais)
    return [
        local for local in locais
        if termo in local["instituicao"].lower()
        or termo in local["endereco"].lower()
        or termo in local["cep"].lower()
        or termo in local["responsavel"].lower()
    ]