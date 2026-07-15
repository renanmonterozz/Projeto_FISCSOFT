import hashlib
import bcrypt
from database.conexaodb import Database


def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha. Mantém compatibilidade com hashes SHA-256 antigos."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt ou SHA-256 (legado)."""
    if hashed.startswith("$2"):
        return bcrypt.checkpw(password.encode(), hashed.encode())
    return hashlib.sha256(password.encode()).hexdigest() == hashed


def registrar_log(usuario: str, acao: str, tabela: str, descricao: str):
    """Registra uma acao no log de auditoria."""
    with Database() as db:
        if db.conexao:
            sql = """INSERT INTO logs (usuario, acao, tabela, descricao)
                     VALUES (?, ?, ?, ?)"""
            db.executar(sql, (usuario, acao, tabela, descricao))
            db.commitar()
