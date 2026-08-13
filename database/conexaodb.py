import os
import re
import logging
import sqlite3

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from cache.gerenciador_cache import CacheManager

logger = logging.getLogger(__name__)

load_dotenv()


def _executar_multiplas(conn, sql_bloco):
    """Divide um bloco SQL em statements individuais e executa um por um."""
    stmts = [s.strip() for s in re.split(r";\s*(?=\S)", sql_bloco) if s.strip()]
    cursor = conn.cursor()
    for stmt in stmts:
        try:
            cursor.execute(stmt)
        except Error as e:
            msg = str(e).lower()
            if "duplicate" not in msg and "already exists" not in msg and "multiple primary key" not in msg:
                logger.warning("Statement falhou: %s -> %s", stmt[:80], e)
    cursor.close()


class Database:
    def __init__(self):
        self.conexao = None

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()
        return False

    def conectar(self) -> bool:
        try:
            config = {
                "host": os.getenv("DB_HOST", "").strip(),
                "port": int(os.getenv("DB_PORT", "3306").strip()),
                "database": os.getenv("DB_NAME", "").strip(),
                "user": os.getenv("DB_USER", "").strip(),
                "password": os.getenv("DB_PASSWORD", "").strip(),
                "charset": "utf8mb4",
                "collation": "utf8mb4_unicode_ci",
                "autocommit": False,
                "use_unicode": True,
            }

            ssl_ca = os.getenv("DB_SSL_CA")
            if ssl_ca:
                import certifi
                config["ssl_ca"] = certifi.where() if ssl_ca == "certifi" else ssl_ca.strip()
                config["ssl_verify_cert"] = True
            else:
                config["ssl_disabled"] = False

            logger.info("Conectando ao MySQL: %s@%s:%s/%s",
                        config["user"], config["host"], config["port"], config["database"])

            self.conexao = mysql.connector.connect(**config)
            cursor = self.conexao.cursor()
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            cursor.close()

            self._migrar()
            return True
        except Error as e:
            logger.warning("MySQL indisponivel: %s", e)
            return False

    def _migrar(self):
        migracoes = [
            ("ALTER TABLE itens ADD COLUMN processo VARCHAR(100)", "itens.processo"),
            ("ALTER TABLE tccm ADD COLUMN documento_sei TEXT", "tccm.documento_sei"),
            ("ALTER TABLE tccm ADD COLUMN data_inicio DATE", "tccm.data_inicio"),
            ("ALTER TABLE tccm ADD COLUMN semestres INTEGER NOT NULL DEFAULT 1", "tccm.semestres"),
            ("ALTER TABLE `nota fiscal` ADD COLUMN arquivo TEXT", "`nota fiscal`.arquivo"),
        ]
        cursor = self.conexao.cursor()
        for sql, nome in migracoes:
            try:
                cursor.execute(sql)
                self.conexao.commit()
                logger.debug("Migracao aplicada: %s", nome)
            except Error as e:
                if "duplicate column" in str(e).lower():
                    continue
                logger.debug("Migracao ignorada para %s: %s", nome, e)
        cursor.close()

        self._migrar_perfis()

    def _migrar_perfis(self):
        try:
            normalizacoes = [
                ("Administrador", ("admin", "administrador")),
                ("Agente", ("agente",)),
                ("Operador", ("operador", "usuario", "user")),
            ]
            cursor = self.conexao.cursor()
            for novo, antigos in normalizacoes:
                marca = ",".join(["%s"] * len(antigos))
                cursor.execute(
                    f'SELECT COUNT(*) FROM `agente ibama` WHERE LOWER(perfil) IN ({marca})',
                    antigos,
                )
                if cursor.fetchone()[0] > 0:
                    cursor.execute(
                        f'UPDATE `agente ibama` SET perfil = %s WHERE LOWER(perfil) IN ({marca})',
                        (novo, *antigos),
                    )
                    logger.debug("Migracao aplicada: perfis '%s' -> '%s'", "/".join(antigos), novo)
            self.conexao.commit()
        except Error:
            pass

    def desconectar(self):
        if self.conexao and self.conexao.is_connected():
            self.conexao.close()

    def executar(self, sql: str, params=None):
        cache = CacheManager.instancia()
        sql_upper = sql.strip().upper()

        if cache.ativo and sql_upper.startswith("SELECT"):
            try:
                cursor_cache = cache.executar_cache(sql, params)
                return cursor_cache
            except Exception as e:
                logger.debug("Fallback p/ MySQL (cache erro): %s", e)

        if not self.conexao or not self.conexao.is_connected():
            return None
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor

    def commitar(self):
        if self.conexao and self.conexao.is_connected():
            self.conexao.commit()
        cache = CacheManager.instancia()
        if cache.ativo:
            cache.commitar_cache()


def criar_schema():
    schema_sql = """
    CREATE TABLE IF NOT EXISTS `agente ibama` (
        matricula INTEGER NOT NULL,
        senha VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL,
        nome_agente VARCHAR(45) NOT NULL,
        cpf VARCHAR(45) NOT NULL,
        telefone VARCHAR(20),
        login VARCHAR(45) NOT NULL,
        perfil VARCHAR(50) NOT NULL DEFAULT 'agente',
        status VARCHAR(20) NOT NULL DEFAULT 'ativo',
        cadastrado_por VARCHAR(45),
        atualizado_por VARCHAR(45),
        UNIQUE (matricula),
        UNIQUE (email),
        UNIQUE (login),
        UNIQUE (cpf),
        PRIMARY KEY (matricula)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS infrator (
        cpf VARCHAR(11) NOT NULL,
        email VARCHAR(100) NOT NULL,
        senha VARCHAR(255) NOT NULL,
        id_infrator INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
        nome_infrator VARCHAR(45) NOT NULL,
        telefone_infrator VARCHAR(20),
        UNIQUE (cpf),
        UNIQUE (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS tccm (
        processo VARCHAR(100) NOT NULL,
        documento_sei VARCHAR(100),
        data_inicio DATE,
        semestres INTEGER NOT NULL DEFAULT 1,
        total_pago DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        total_validado DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        data_validade DATE,
        intervalo INTEGER NOT NULL DEFAULT 1,
        total_devido DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        status VARCHAR(30) NOT NULL DEFAULT 'pendente',
        `agente ibama_matricula` INTEGER NOT NULL,
        `infrator_id_infrator` INTEGER NOT NULL,
        PRIMARY KEY (processo, `agente ibama_matricula`, `infrator_id_infrator`),
        UNIQUE (processo),
        FOREIGN KEY (`agente ibama_matricula`) REFERENCES `agente ibama` (matricula),
        FOREIGN KEY (`infrator_id_infrator`) REFERENCES infrator (id_infrator)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS `nota fiscal` (
        nota_fiscal VARCHAR(50) NOT NULL,
        semestre INTEGER NOT NULL,
        data DATE NOT NULL,
        chave_de_acesso VARCHAR(44) NOT NULL,
        valor_total DECIMAL(8,2) NOT NULL,
        `agente ibama_matricula` INTEGER NOT NULL,
        status_nota VARCHAR(30) DEFAULT 'Pendente',
        processo VARCHAR(100),
        arquivo TEXT,
        PRIMARY KEY (nota_fiscal, `agente ibama_matricula`),
        UNIQUE (nota_fiscal),
        UNIQUE (chave_de_acesso),
        FOREIGN KEY (`agente ibama_matricula`) REFERENCES `agente ibama` (matricula),
        FOREIGN KEY (processo) REFERENCES tccm (processo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS produtos (
        lote VARCHAR(255) NOT NULL,
        status_entrega VARCHAR(30) NOT NULL DEFAULT 'pendente',
        quantidade INTEGER NOT NULL DEFAULT 0,
        preco_unitario DECIMAL(10,2) NOT NULL,
        data_validade DATE,
        `nota fiscal_nota_fiscal` VARCHAR(50) NOT NULL,
        `nota fiscal_agente ibama_matricula` INTEGER NOT NULL,
        itens_id INTEGER,
        nome_item VARCHAR(200),
        PRIMARY KEY (lote, `nota fiscal_nota_fiscal`, `nota fiscal_agente ibama_matricula`),
        UNIQUE (lote),
        FOREIGN KEY (`nota fiscal_nota_fiscal`, `nota fiscal_agente ibama_matricula`)
            REFERENCES `nota fiscal` (nota_fiscal, `agente ibama_matricula`),
        FOREIGN KEY (itens_id) REFERENCES itens (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS insumo (
        nome VARCHAR(255) NOT NULL,
        tipo VARCHAR(255) NOT NULL,
        descricao TEXT,
        justificativa TEXT,
        link TEXT,
        preco_orcado DECIMAL(8,2) NOT NULL,
        id_insumo INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
        `infrator_id_infrator` INTEGER NOT NULL,
        `produtos_lote` VARCHAR(255) NOT NULL,
        UNIQUE (id_insumo),
        FOREIGN KEY (`infrator_id_infrator`) REFERENCES infrator (id_infrator),
        FOREIGN KEY (`produtos_lote`) REFERENCES produtos (lote)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS insumo_has_TCCM (
        `insumo_id_insumo` INTEGER NOT NULL,
        `insumo_infrator_id_infrator` INTEGER NOT NULL,
        `insumo_produtos_lote` VARCHAR(255) NOT NULL,
        `TCCM_processo` VARCHAR(100) NOT NULL,
        `TCCM_agente ibama_matricula` INTEGER NOT NULL,
        `TCCM_infrator_id_infrator` INTEGER NOT NULL,
        PRIMARY KEY (`insumo_id_insumo`, `insumo_infrator_id_infrator`, `insumo_produtos_lote`,
                     `TCCM_processo`, `TCCM_agente ibama_matricula`, `TCCM_infrator_id_infrator`),
        FOREIGN KEY (`insumo_id_insumo`) REFERENCES insumo (id_insumo),
        FOREIGN KEY (`TCCM_processo`) REFERENCES tccm (processo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS itens (
        id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
        nome VARCHAR(200),
        descricao VARCHAR(200) NOT NULL,
        codigo_interno VARCHAR(50) NOT NULL,
        categoria VARCHAR(100),
        tipo VARCHAR(50),
        justificativa TEXT,
        unidade_medida VARCHAR(50),
        semestre VARCHAR(20),
        quantidade_prevista INTEGER DEFAULT 0,
        status VARCHAR(30) DEFAULT 'Ativo',
        notas_fiscais VARCHAR(100),
        processo VARCHAR(100),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (codigo_interno)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS locais (
        id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
        cep VARCHAR(10) NOT NULL,
        endereco VARCHAR(255) NOT NULL,
        instituicao VARCHAR(200) NOT NULL,
        responsavel VARCHAR(100) NOT NULL,
        telefone VARCHAR(20),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
        usuario VARCHAR(100) NOT NULL,
        acao VARCHAR(50) NOT NULL,
        tabela VARCHAR(50) NOT NULL,
        descricao TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """

    dados_sql = """
    INSERT IGNORE INTO `agente ibama` (matricula, login, senha, email, nome_agente, status, perfil, cpf, telefone)
    VALUES
        (0, 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin@ibama.gov.br', 'Carlos Silva', 'ativo', 'Administrador', '12345678901', NULL),
        (1, 'agente', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'agente@ibama.gov.br', 'Joao Agente', 'ativo', 'Agente', '12345678902', NULL),
        (2, 'usuario', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'usuario@ibama.gov.br', 'Maria Usuario', 'ativo', 'Usuario', '12345678903', NULL);

    INSERT IGNORE INTO infrator (cpf, email, senha, id_infrator, nome_infrator, telefone_infrator)
    VALUES
        ('12345678901', 'joao@email.com', '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 1, 'João Silva', '11987654321'),
        ('23456789012', 'maria@email.com', '6b08d780140e292a4af8ba3f2333fc1357091442d7e807c6cad92e8dcd0240b7', 2, 'Maria Oliveira', '11976543210'),
        ('34567890123', 'pedro@email.com', 'b578dc5fcbfabbc7e96400601d0858c951f04929faef033bbbc117ab935c6ae9', 3, 'Pedro Santos', '11965432109'),
        ('45678901234', 'ana@email.com', '2288821c6b799cf47a8c9aa231f361ffb906bbee0d5fb5e1767509e27442cc62', 4, 'Ana Costa', '11954321098');

    INSERT IGNORE INTO tccm (processo, documento_sei, data_inicio, semestres, total_pago, total_validado, data_validade, intervalo, total_devido, status, `agente ibama_matricula`, `infrator_id_infrator`)
    VALUES
        ('PROC-2026-001', 'SEI-001/2026', '2026-01-15', 4, 1500.00, 2000.00, '2026-12-31', 6, 5000.00, 'pendente', 0, 1),
        ('PROC-2026-002', 'SEI-002/2026', '2026-02-01', 4, 3000.00, 4000.00, '2026-12-31', 6, 8000.00, 'pendente', 0, 2),
        ('PROC-2026-003', 'SEI-003/2026', '2026-03-10', 2, 800.00, 1000.00, '2026-12-31', 6, 2500.00, 'pendente', 0, 3),
        ('PROC-2026-004', 'SEI-004/2026', '2026-01-20', 4, 2200.00, 3000.00, '2026-12-31', 6, 6500.00, 'pendente', 0, 4);

    INSERT IGNORE INTO itens (id, nome, descricao, codigo_interno, categoria, tipo, justificativa, unidade_medida, semestre, quantidade_prevista, status, notas_fiscais, criado_em)
    VALUES
        (1, 'Monitor Dell 24"', 'Monitor Dell 24"', 'IT-001', 'Eletrônicos', 'Equipamento', 'Monitor para estacao de trabalho', 'Unidade', NULL, 0, 'Ativo', 'NF-001234', '2026-06-26 23:05:18'),
        (2, 'Cadeira Ergonômica', 'Cadeira Ergonômica', 'IT-002', 'Mobiliário', 'Móvel', 'Cadeira para escritorio', 'Unidade', NULL, 0, 'Ativo', 'NF-001235', '2026-06-26 23:05:18'),
        (3, 'Notebook Lenovo', 'Notebook Lenovo', 'IT-003', 'Eletrônicos', 'Equipamento', 'Notebook para uso administrativo', 'Unidade', NULL, 0, 'Pendente', 'NF-001236', '2026-06-26 23:05:18'),
        (4, 'Mesa de Escritório', 'Mesa de Escritório', 'IT-004', 'Mobiliário', 'Móvel', 'Mesa para trabalho', 'Unidade', NULL, 0, 'Ativo', 'NF-001234', '2026-06-26 23:05:18'),
        (5, 'Impressora HP', 'Impressora HP', 'IT-005', 'Eletrônicos', 'Equipamento', 'Impressora multifuncional', 'Unidade', NULL, 0, 'Inativo', 'NF-001235', '2026-06-26 23:05:18'),
        (6, 'Teclado USB', 'Teclado USB', 'IT-006', 'Eletrônicos', 'Periférico', 'Teclado USB padrao', 'Unidade', NULL, 0, 'Ativo', 'NF-001236', '2026-06-26 23:05:18'),
        (7, 'Cadeira Executiva', 'Cadeira Executiva', 'IT-007', 'Mobiliário', 'Móvel', 'Cadeira executiva', 'Unidade', NULL, 0, 'Ativo', 'NF-001234', '2026-06-26 23:05:18'),
        (8, 'computador', 'dell', '', NULL, NULL, NULL, NULL, '3', 100, 'Ativo', NULL, '2026-06-27 00:11:24');

    INSERT IGNORE INTO locais (id, cep, endereco, instituicao, responsavel, telefone)
    VALUES
        (1, '70040-010', 'Esplanada dos Ministerios, Bloco D, Brasilia-DF', 'IBAMA - Sede', 'Joao Silva', '61-36747000'),
        (2, '01310-100', 'Av. Paulista, 1578, Bela Vista, Sao Paulo-SP', 'IBAMA - Regional SP', 'Maria Oliveira', '11-30155000'),
        (3, '20040-020', 'Av. Rio Branco, 156, Centro, Rio de Janeiro-RJ', 'IBAMA - Regional RJ', 'Pedro Santos', '21-32137000');
    """

    try:
        config = {
            "host": os.getenv("DB_HOST", "").strip(),
            "port": int(os.getenv("DB_PORT", "3306").strip()),
            "database": os.getenv("DB_NAME", "").strip(),
            "user": os.getenv("DB_USER", "").strip(),
            "password": os.getenv("DB_PASSWORD", "").strip(),
            "charset": "utf8mb4",
        }

        ssl_ca = os.getenv("DB_SSL_CA")
        if ssl_ca:
            import certifi
            config["ssl_ca"] = certifi.where() if ssl_ca == "certifi" else ssl_ca.strip()
            config["ssl_verify_cert"] = True
        else:
            config["ssl_disabled"] = False

        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.close()
        _executar_multiplas(conexao, schema_sql)
        _executar_multiplas(conexao, dados_sql)
        cursor = conexao.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        cursor.close()
        conexao.commit()
        conexao.close()
        logger.info("Schema MySQL criado com sucesso")
    except Error as e:
        logger.error("Erro ao criar schema MySQL: %s", e)
        raise


if __name__ == "__main__":
    criar_schema()
    print("Schema MySQL criado no servidor Aiven")
