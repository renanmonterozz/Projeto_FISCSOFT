from __future__ import annotations

from sqlalchemy import delete, select

from database.models import AgenteIbama
from database.orm import session_scope


class UsuariosRepository:
    def criar(self, dados, usuario_logado=None):
        with session_scope() as session:
            usuario = AgenteIbama(
                matricula=dados["matricula"],
                nome_agente=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                telefone=dados["telefone"] or None,
                login=dados["login"],
                senha=dados["senha_hash"],
                perfil=dados["perfil"],
                status="ativo",
                cadastrado_por=usuario_logado or "",
            )
            session.add(usuario)

    def atualizar(self, matricula, dados, usuario_logado=None):
        with session_scope() as session:
            usuario = session.get(AgenteIbama, matricula)
            if usuario is None:
                raise LookupError("Usuario nao encontrado.")
            usuario.nome_agente = dados["nome"]
            usuario.cpf = dados["cpf"]
            usuario.email = dados["email"]
            usuario.telefone = dados["telefone"] or None
            usuario.login = dados["login"]
            usuario.perfil = dados["perfil"]
            usuario.atualizado_por = usuario_logado or ""
            if dados.get("senha_hash"):
                usuario.senha = dados["senha_hash"]

    def listar(self):
        with session_scope() as session:
            usuarios = session.scalars(select(AgenteIbama).order_by(AgenteIbama.nome_agente)).all()
        return [
            {
                "matricula": usuario.matricula,
                "nome": usuario.nome_agente,
                "cpf": usuario.cpf,
                "email": usuario.email,
                "telefone": usuario.telefone,
                "login": usuario.login,
                "perfil": usuario.perfil.capitalize() if usuario.perfil else "Agente",
                "status": "Ativo" if usuario.status == "ativo" else "Inativo",
            }
            for usuario in usuarios
        ]

    def excluir(self, matricula):
        with session_scope() as session:
            session.execute(delete(AgenteIbama).where(AgenteIbama.matricula == matricula))
        return True
