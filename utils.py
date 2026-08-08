import hashlib
import os
import logging

import bcrypt
from database.conexaodb import Database

logger = logging.getLogger(__name__)


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


CERTIFICADO_DIR = "D:\\"
CERTIFICADO_ARQUIVO = "certificado.pfx"
CERTIFICADO_SENHA = b"admin123"
SENHAS_TENTATIVA = [b"admin123", b"123456", b"senha", b""]


def _carregar_certificado(cert_path: str, senha: bytes):
    from cryptography.hazmat.primitives.serialization import pkcs12
    with open(cert_path, "rb") as f:
        pfx_data = f.read()
    return pkcs12.load_key_and_certificates(pfx_data, senha)


def _tentar_senhas(cert_path: str):
    from cryptography.hazmat.primitives.serialization import pkcs12
    with open(cert_path, "rb") as f:
        pfx_data = f.read()

    for senha in SENHAS_TENTATIVA:
        try:
            pk, cert, chain = pkcs12.load_key_and_certificates(pfx_data, senha)
            if cert is not None:
                return pk, cert, chain, senha
        except Exception:
            continue
    return None, None, None, None


def _extrair_cpf_cnpj(certificate) -> str | None:
    from cryptography.x509.oid import NameOID
    subject = certificate.subject

    for attr in subject:
        if attr.oid == NameOID.SERIAL_NUMBER:
            digits = "".join(c for c in attr.value if c.isdigit())
            if len(digits) == 11 or len(digits) == 14:
                return digits

    for attr in subject:
        if attr.oid == NameOID.COMMON_NAME:
            digits = "".join(c for c in attr.value if c.isdigit())
            if len(digits) == 11 or len(digits) == 14:
                return digits

    return None


def validar_certificado_usb() -> tuple[bool, str, str | None]:
    cert_path = os.path.join(CERTIFICADO_DIR, CERTIFICADO_ARQUIVO)

    if not os.path.exists(cert_path):
        return False, "Certificado nao encontrado", None

    try:
        private_key, certificate, chain, senha_usada = _tentar_senhas(cert_path)

        if certificate is None:
            return False, (
                "Arquivo invalido ou senha incorreta!\n"
                "Senhas testadas: admin123, 123456, senha, (vazia)"
            ), None

        identificador = _extrair_cpf_cnpj(certificate)
        logger.info("Certificado validado. Identificador: %s", identificador)
        return True, "Certificado valido", identificador

    except Exception as e:
        logger.error("Erro ao validar certificado: %s", e)
        return False, f"Erro ao ler certificado: {e}", None


def login_por_certificado() -> tuple[bool, str, dict | None]:
    valido, mensagem, identificador = validar_certificado_usb()
    if not valido:
        return False, mensagem, None
    if identificador is None:
        return False, "Nao foi possivel extrair CPF/CNPJ do certificado", None
    with Database() as db:
        if not db.conexao:
            return False, "Erro ao conectar ao banco de dados", None
        sql = """
            SELECT nome_agente, cpf, status, perfil, login
            FROM "agente ibama"
            WHERE cpf = ?
        """
        resultado = db.executar(sql, (identificador,))
        registro = resultado.fetchone() if resultado else None
    if registro is None:
        return False, f"CPF {identificador} nao encontrado no sistema", None
    nome, cpf, status, perfil, login = registro
    if status != "ativo":
        return False, "Usuario inativo! Contate o administrador.", None
    return True, "Login realizado com sucesso", {
        "nome": nome,
        "cpf": cpf,
        "perfil": perfil,
        "login": login,
    }
