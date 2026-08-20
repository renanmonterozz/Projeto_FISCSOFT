from __future__ import annotations

from repositories.login_repository import LoginRepository
from utils import verify_password


class RegraLoginError(ValueError):
    """Erro de regra de negocio do login."""


class LoginService:
    def __init__(self, repository=None):
        self.repository = repository or LoginRepository()

    def autenticar_usuario(self, login, senha):
        registro = self.repository.buscar_agente_por_login(login)
        if registro is None:
            return None

        if not verify_password(senha, registro["senha"]):
            raise RegraLoginError("Usuario ou senha incorretos!")

        if registro["status"] != "ativo":
            raise RegraLoginError("Usuario inativo! Contate o administrador.")

        return {
            "nome": registro["nome"],
            "perfil": registro["perfil"],
        }

    def autenticar_infrator_por_cpf(self, cpf, senha):
        registro = self.repository.buscar_infrator_por_cpf(cpf)
        if registro is None:
            return None

        if not verify_password(senha, registro["senha"]):
            raise RegraLoginError("CPF ou senha incorretos!")

        return {
            "id": registro["id"],
            "nome": registro["nome"],
        }

    def autenticar_credencial_unificada(self, credencial, senha):
        registro_agente = self.repository.buscar_agente_por_login(credencial)
        if registro_agente:
            if not verify_password(senha, registro_agente["senha"]):
                raise RegraLoginError("Usuario ou senha incorretos!")
            if registro_agente["status"] != "ativo":
                raise RegraLoginError("Usuario inativo! Contate o administrador.")
            return {
                "tipo": "agente",
                "nome": registro_agente["nome"],
                "perfil": registro_agente["perfil"],
            }

        registro_inf = self.repository.buscar_infrator_por_cpf(credencial)
        if registro_inf:
            if not verify_password(senha, registro_inf["senha"]):
                raise RegraLoginError("Usuario ou senha incorretos!")
            return {
                "tipo": "infrator",
                "id": registro_inf["id"],
                "nome": registro_inf["nome"],
            }

        return None


def validar_credenciais(usuario, senha):
    usuario = (usuario or "").strip()
    senha = (senha or "").strip()

    if not usuario:
        raise RegraLoginError("Informe o usuario.")
    if not senha:
        raise RegraLoginError("Informe a senha.")

    return usuario, senha
