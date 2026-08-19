from __future__ import annotations


class RegraLoginError(ValueError):
    """Erro de regra de negocio do login."""


def validar_credenciais(usuario, senha):
    usuario = (usuario or "").strip()
    senha = (senha or "").strip()

    if not usuario:
        raise RegraLoginError("Informe o usuario.")
    if not senha:
        raise RegraLoginError("Informe a senha.")

    return usuario, senha
