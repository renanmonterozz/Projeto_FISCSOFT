from __future__ import annotations

from screens.repository.infratores_repository import InfratoresRepository
from utils import hash_password, registrar_log


class RegraInfratorError(ValueError):
    """Erro de regra de negocio do cadastro de infrator."""


class InfratorService:
    def __init__(self, repository=None):
        self.repository = repository or InfratoresRepository()

    def salvar(self, dados, infrator_id=None, usuario_logado=None):
        dados = dict(dados)
        dados["senha_hash"] = hash_password(dados.pop("senha"))

        if infrator_id:
            self.repository.atualizar(infrator_id, dados)
            acao = "edicao"
            mensagem = f"Infrator '{dados['nome']}' atualizado com sucesso!"
        else:
            self.repository.criar(dados)
            acao = "cadastro"
            mensagem = f"Infrator '{dados['nome']}' cadastrado com sucesso!"

        registrar_log(
            usuario_logado or "Sistema",
            acao,
            "infrator",
            mensagem,
        )
        return mensagem


def validar_dados_infrator(nome, cpf, email, telefone, senha, confirmar):
    dados = {
        "nome": (nome or "").strip(),
        "cpf": (cpf or "").strip(),
        "email": (email or "").strip(),
        "telefone": (telefone or "").strip(),
        "senha": senha or "",
        "confirmar": confirmar or "",
    }

    if not all((dados["nome"], dados["cpf"], dados["email"], dados["senha"], dados["confirmar"])):
        raise RegraInfratorError("Preencha todos os campos obrigatorios!")
    if dados["senha"] != dados["confirmar"]:
        raise RegraInfratorError("As senhas nao conferem!")

    return dados


def filtrar_infratores(infratores, busca="", filtro_email="", filtro_telefone=""):
    busca = (busca or "").strip().lower()
    filtro_email = (filtro_email or "").strip().lower()
    filtro_telefone = (filtro_telefone or "").strip().lower()

    return [
        infrator for infrator in infratores
        if (
            not busca
            or busca in infrator["nome"].lower()
            or busca in infrator["cpf"]
            or busca in infrator["email"].lower()
        )
        and (not filtro_email or filtro_email in infrator["email"].lower())
        and (not filtro_telefone or filtro_telefone in infrator["telefone"])
    ]
