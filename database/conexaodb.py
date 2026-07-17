import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fiscsoft.db")


class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.conexao = None

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()
        return False

    def conectar(self) -> bool:
        try:
            logger.info("Conectando ao banco SQLite: %s", self.db_path)
            self.conexao = sqlite3.connect(self.db_path)
            self.conexao.execute("PRAGMA foreign_keys = ON")
            self.conexao.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            logger.error("Erro ao conectar ao banco: %s", e)
            return False

    def desconectar(self):
        if self.conexao:
            self.conexao.close()

    def executar(self, sql: str, params=None):
        if not self.conexao:
            return None
        cursor = self.conexao.cursor()
        cursor.execute(sql, params or ())
        return cursor

    def commitar(self):
        if self.conexao:
            self.conexao.commit()


def criar_schema():
    schema_sql = """
    CREATE TABLE IF NOT EXISTS "agente ibama" (
        matricula INTEGER NOT NULL,
        senha VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL,
        nome_agente VARCHAR(45) NOT NULL,
        cpf VARCHAR(45) NOT NULL,
        telefone TEXT,
        login VARCHAR(45) NOT NULL,
        perfil TEXT NOT NULL DEFAULT 'agente',
        status TEXT NOT NULL DEFAULT 'ativo',
        cadastrado_por VARCHAR(45),
        atualizado_por VARCHAR(45),
        UNIQUE (matricula),
        UNIQUE (email),
        UNIQUE (login),
        UNIQUE (cpf),
        PRIMARY KEY (matricula)
    );

    CREATE TABLE IF NOT EXISTS infrator (
        cpf VARCHAR(11) NOT NULL,
        email VARCHAR(100) NOT NULL,
        senha VARCHAR(255) NOT NULL,
        id_infrator INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome_infrator VARCHAR(45) NOT NULL,
        telefone_infrator TEXT,
        UNIQUE (cpf),
        UNIQUE (email)
    );

    CREATE TABLE IF NOT EXISTS tccm (
        processo TEXT NOT NULL,
        total_pago DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        total_validado DECIMAL(12,2) NOT NULL,
        data_validade DATE,
        intervalo INTEGER NOT NULL,
        total_devido DECIMAL(12,2) NOT NULL,
        status TEXT NOT NULL DEFAULT 'pendente',
        "agente ibama_matricula" INTEGER NOT NULL,
        "infrator_id_infrator" INTEGER NOT NULL,
        PRIMARY KEY (processo, "agente ibama_matricula", "infrator_id_infrator"),
        UNIQUE (processo),
        FOREIGN KEY ("agente ibama_matricula") REFERENCES "agente ibama" (matricula),
        FOREIGN KEY ("infrator_id_infrator") REFERENCES infrator (id_infrator)
    );

    CREATE TABLE IF NOT EXISTS "nota fiscal" (
        nota_fiscal VARCHAR(50) NOT NULL,
        semestre INTEGER NOT NULL,
        data DATE NOT NULL,
        chave_de_acesso VARCHAR(44) NOT NULL,
        valor_total DECIMAL(8,2) NOT NULL,
        "agente ibama_matricula" INTEGER NOT NULL,
        status_nota VARCHAR(30) DEFAULT 'Pendente',
        processo TEXT,
        PRIMARY KEY (nota_fiscal, "agente ibama_matricula"),
        UNIQUE (nota_fiscal),
        UNIQUE (chave_de_acesso),
        FOREIGN KEY ("agente ibama_matricula") REFERENCES "agente ibama" (matricula),
        FOREIGN KEY (processo) REFERENCES tccm (processo)
    );

    CREATE TABLE IF NOT EXISTS produtos (
        lote VARCHAR(255) NOT NULL,
        status_entrega TEXT NOT NULL DEFAULT 'pendente',
        quantidade INTEGER NOT NULL DEFAULT 0,
        preco_unitario DECIMAL(10,2) NOT NULL,
        data_validade DATE,
        "nota fiscal_nota_fiscal" VARCHAR(50) NOT NULL,
        "nota fiscal_agente ibama_matricula" INTEGER NOT NULL,
        itens_id INTEGER,
        nome_item VARCHAR(200),
        PRIMARY KEY (lote, "nota fiscal_nota_fiscal", "nota fiscal_agente ibama_matricula"),
        UNIQUE (lote),
        FOREIGN KEY ("nota fiscal_nota_fiscal", "nota fiscal_agente ibama_matricula")
            REFERENCES "nota fiscal" (nota_fiscal, "agente ibama_matricula"),
        FOREIGN KEY (itens_id) REFERENCES itens (id)
    );

    CREATE TABLE IF NOT EXISTS insumo (
        nome VARCHAR(255) NOT NULL,
        tipo VARCHAR(255) NOT NULL,
        descricao TEXT,
        justificativa TEXT,
        link TEXT,
        preco_orcado DECIMAL(8,2) NOT NULL,
        id_insumo INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "infrator_id_infrator" INTEGER NOT NULL,
        "produtos_lote" VARCHAR(255) NOT NULL,
        UNIQUE (id_insumo),
        FOREIGN KEY ("infrator_id_infrator") REFERENCES infrator (id_infrator),
        FOREIGN KEY ("produtos_lote") REFERENCES produtos (lote)
    );

    CREATE TABLE IF NOT EXISTS insumo_has_TCCM (
        "insumo_id_insumo" INTEGER NOT NULL,
        "insumo_infrator_id_infrator" INTEGER NOT NULL,
        "insumo_produtos_lote" VARCHAR(255) NOT NULL,
        "TCCM_processo" TEXT NOT NULL,
        "TCCM_agente ibama_matricula" INTEGER NOT NULL,
        "TCCM_infrator_id_infrator" INTEGER NOT NULL,
        PRIMARY KEY ("insumo_id_insumo", "insumo_infrator_id_infrator", "insumo_produtos_lote",
                     "TCCM_processo", "TCCM_agente ibama_matricula", "TCCM_infrator_id_infrator"),
        FOREIGN KEY ("insumo_id_insumo", "insumo_infrator_id_infrator", "insumo_produtos_lote")
            REFERENCES insumo (id_insumo, "infrator_id_infrator", "produtos_lote"),
        FOREIGN KEY ("TCCM_processo", "TCCM_agente ibama_matricula", "TCCM_infrator_id_infrator")
            REFERENCES tccm (processo, "agente ibama_matricula", "infrator_id_infrator")
    );

    CREATE TABLE IF NOT EXISTS itens (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
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
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (codigo_interno)
    );

    CREATE TABLE IF NOT EXISTS locais (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        cep VARCHAR(10) NOT NULL,
        endereco VARCHAR(255) NOT NULL,
        instituicao VARCHAR(200) NOT NULL,
        responsavel VARCHAR(100) NOT NULL,
        telefone VARCHAR(20),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        usuario VARCHAR(100) NOT NULL,
        acao VARCHAR(50) NOT NULL,
        tabela VARCHAR(50) NOT NULL,
        descricao TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    dados_sql = """
    INSERT OR IGNORE INTO "agente ibama" (matricula, login, senha, email, nome_agente, status, perfil, cpf, telefone)
    VALUES
        (0, 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin@ibama.gov.br', 'Carlos Silva', 'ativo', 'Administrador', '12345678901', NULL),
        (1, 'agente', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'agente@ibama.gov.br', 'Joao Agente', 'ativo', 'Agente', '12345678902', NULL),
        (2, 'usuario', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'usuario@ibama.gov.br', 'Maria Usuario', 'ativo', 'Usuario', '12345678903', NULL);

    INSERT OR IGNORE INTO infrator (cpf, email, senha, id_infrator, nome_infrator, telefone_infrator)
    VALUES
        ('12345678901', 'joao@email.com', '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 1, 'João Silva', '11987654321'),
        ('23456789012', 'maria@email.com', '6b08d780140e292a4af8ba3f2333fc1357091442d7e807c6cad92e8dcd0240b7', 2, 'Maria Oliveira', '11976543210'),
        ('34567890123', 'pedro@email.com', 'b578dc5fcbfabbc7e96400601d0858c951f04929faef033bbbc117ab935c6ae9', 3, 'Pedro Santos', '11965432109'),
        ('45678901234', 'ana@email.com', '2288821c6b799cf47a8c9aa231f361ffb906bbee0d5fb5e1767509e27442cc62', 4, 'Ana Costa', '11954321098');

    INSERT OR IGNORE INTO tccm (processo, total_pago, total_validado, data_validade, intervalo, total_devido, status, "agente ibama_matricula", "infrator_id_infrator")
    VALUES
        ('PROC-2026-001', 1500.00, 2000.00, '2026-12-31', 6, 5000.00, 'pendente', 0, 1),
        ('PROC-2026-002', 3000.00, 4000.00, '2026-12-31', 6, 8000.00, 'pendente', 0, 2),
        ('PROC-2026-003', 800.00, 1000.00, '2026-12-31', 6, 2500.00, 'pendente', 0, 3),
        ('PROC-2026-004', 2200.00, 3000.00, '2026-12-31', 6, 6500.00, 'pendente', 0, 4);

    INSERT OR IGNORE INTO itens (id, nome, descricao, codigo_interno, categoria, tipo, justificativa, unidade_medida, semestre, quantidade_prevista, status, notas_fiscais, criado_em)
    VALUES
        (1, 'Monitor Dell 24"', 'Monitor Dell 24"', 'IT-001', 'Eletrônicos', 'Equipamento', 'Monitor para estacao de trabalho', 'Unidade', NULL, 0, 'Ativo', 'NF-001234', '2026-06-26 23:05:18'),
        (2, 'Cadeira Ergonômica', 'Cadeira Ergonômica', 'IT-002', 'Mobiliário', 'Móvel', 'Cadeira para escritorio', 'Unidade', NULL, 0, 'Ativo', 'NF-001235', '2026-06-26 23:05:18'),
        (3, 'Notebook Lenovo', 'Notebook Lenovo', 'IT-003', 'Eletrônicos', 'Equipamento', 'Notebook para uso administrativo', 'Unidade', NULL, 0, 'Pendente', 'NF-001236', '2026-06-26 23:05:18'),
        (4, 'Mesa de Escritório', 'Mesa de Escritório', 'IT-004', 'Mobiliário', 'Móvel', 'Mesa para trabalho', 'Unidade', NULL, 0, 'Ativo', 'NF-001234', '2026-06-26 23:05:18'),
        (5, 'Impressora HP', 'Impressora HP', 'IT-005', 'Eletrônicos', 'Equipamento', 'Impressora multifuncional', 'Unidade', NULL, 0, 'Inativo', 'NF-001235', '2026-06-26 23:05:18'),
        (6, 'Teclado USB', 'Teclado USB', 'IT-006', 'Eletrônicos', 'Periférico', 'Teclado USB padrao', 'Unidade', NULL, 0, 'Ativo', 'NF-001236', '2026-06-26 23:05:18'),
        (7, 'Cadeira Executiva', 'Cadeira Executiva', 'IT-007', 'Mobiliário', 'Móvel', 'Cadeira executiva', 'Unidade', NULL, 0, 'Ativo', 'NF-001234', '2026-06-26 23:05:18'),
        (8, 'computador', 'dell', '', NULL, NULL, NULL, NULL, '3', 100, 'Ativo', NULL, '2026-06-27 00:11:24');

    INSERT OR IGNORE INTO locais (id, cep, endereco, instituicao, responsavel, telefone)
    VALUES
        (1, '70040-010', 'Esplanada dos Ministerios, Bloco D, Brasilia-DF', 'IBAMA - Sede', 'Joao Silva', '61-36747000'),
        (2, '01310-100', 'Av. Paulista, 1578, Bela Vista, Sao Paulo-SP', 'IBAMA - Regional SP', 'Maria Oliveira', '11-30155000'),
        (3, '20040-020', 'Av. Rio Branco, 156, Centro, Rio de Janeiro-RJ', 'IBAMA - Regional RJ', 'Pedro Santos', '21-32137000');
    """

    conexao = sqlite3.connect(DB_PATH)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.executescript(schema_sql)
    conexao.executescript(dados_sql)
    conexao.commit()
    conexao.close()
    logger.info("Schema SQLite criado em: %s", DB_PATH)


if __name__ == "__main__":
    criar_schema()
    print(f"Banco de dados criado em: {DB_PATH}")
