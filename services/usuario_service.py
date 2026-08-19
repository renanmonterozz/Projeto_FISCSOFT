from __future__ import annotations

from repositories.usuarios_repository import UsuariosRepository
from utils import hash_password, registrar_log


class RegraUsuarioError(ValueError):
    """Erro de regra de negocio do cadastro de usuario."""


class UsuarioService:
    def __init__(self, repository=None):
        self.repository = repository or UsuariosRepository()

    def salvar(self, dados, em_edicao=False, usuario_logado=None):
        dados = dict(dados)
        senha = dados.pop("senha")
        dados.pop("confirmar")
        if senha:
            dados["senha_hash"] = hash_password(senha)

        if em_edicao:
            self.repository.atualizar(
                dados["matricula"],
                dados,
                usuario_logado,
            )
            mensagem = f"Usuario '{dados['nome']}' atualizado com sucesso!"
            acao = "edicao"
        else:
            self.repository.criar(dados, usuario_logado)
            mensagem = f"Usuario '{dados['nome']}' cadastrado com sucesso!"
            acao = "cadastro"

        registrar_log(usuario_logado or "Sistema", acao, "agente ibama", mensagem)
        return mensagem

    def listar(self):
        return self.repository.listar()

    def pesquisar(self, busca="", filtro_email="", filtro_perfil=""):
        return filtrar_usuarios(self.listar(), busca, filtro_email, filtro_perfil)

    def excluir(self, usuario, usuario_logado=None):
        self.repository.excluir(usuario["matricula"])
        mensagem = f"Usuario '{usuario['nome']}' (matricula: {usuario['matricula']}) excluido"
        registrar_log(usuario_logado or "Sistema", "exclusao", "agente ibama", mensagem)
        return mensagem


def validar_dados_usuario(
    nome,
    cpf,
    email,
    telefone,
    matricula,
    login,
    senha,
    confirmar,
    perfil,
    em_edicao=False,
):
    dados = {
        "nome": (nome or "").strip(),
        "cpf": (cpf or "").strip(),
        "email": (email or "").strip(),
        "telefone": (telefone or "").strip(),
        "matricula": (matricula or "").strip(),
        "login": (login or "").strip(),
        "senha": senha or "",
        "confirmar": confirmar or "",
        "perfil": (perfil or "").strip(),
    }

    if not all((dados["nome"], dados["cpf"], dados["email"], dados["matricula"], dados["login"], dados["perfil"])):
        raise RegraUsuarioError("Preencha todos os campos obrigatorios!")

    if not em_edicao and (not dados["senha"] or not dados["confirmar"]):
        raise RegraUsuarioError("Preencha todos os campos obrigatorios!")
    if dados["senha"] or dados["confirmar"]:
        if dados["senha"] != dados["confirmar"]:
            raise RegraUsuarioError("As senhas nao conferem!")

    try:
        dados["matricula"] = int(dados["matricula"])
    except ValueError as exc:
        raise RegraUsuarioError("Matricula deve ser um numero!") from exc

    return dados


def filtrar_usuarios(usuarios, busca="", filtro_email="", filtro_perfil=""):
    busca = (busca or "").strip().lower()
    filtro_email = (filtro_email or "").strip().lower()
    filtro_perfil = (filtro_perfil or "").strip().lower()
    return [
        usuario for usuario in usuarios
        if (
            not busca
            or busca in usuario["nome"].lower()
            or busca in usuario["login"].lower()
            or busca in str(usuario["matricula"])
        )
        and (not filtro_email or filtro_email in usuario["email"].lower())
        and (
            not filtro_perfil
            or filtro_perfil in usuario["perfil"].lower()
            or filtro_perfil in usuario["status"].lower()
        )
    ]
