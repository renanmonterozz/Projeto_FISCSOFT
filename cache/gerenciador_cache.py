import os
import re
import sqlite3
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
CACHE_DB = os.path.join(CACHE_DIR, "session_cache.db")


class CacheManager:
    _instancia = None
    _cache_conn = None

    @classmethod
    def instancia(cls):
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    @property
    def ativo(self):
        return self._cache_conn is not None

    @property
    def conexao(self):
        return self._cache_conn

    def criar_cache(self, conexao_mysql):
        """Cria cache local SQLite copiando dados do MySQL."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)

            if os.path.exists(CACHE_DB):
                os.remove(CACHE_DB)

            self._cache_conn = sqlite3.connect(CACHE_DB)
            self._cache_conn.execute("PRAGMA journal_mode=WAL")
            self._cache_conn.row_factory = sqlite3.Row

            self._criar_schema_local()
            self._sincronizar_dados(conexao_mysql)

            logger.info("Cache local criado: %s", CACHE_DB)
            return True
        except Exception as e:
            logger.error("Erro ao criar cache: %s", e)
            self.limpar_cache()
            return False

    def limpar_cache(self):
        """Remove o arquivo de cache local."""
        try:
            if self._cache_conn:
                self._cache_conn.close()
                self._cache_conn = None
            if os.path.exists(CACHE_DB):
                os.remove(CACHE_DB)
                logger.info("Cache local removido: %s", CACHE_DB)
        except Exception as e:
            logger.error("Erro ao limpar cache: %s", e)
        finally:
            self._cache_conn = None

    def executar_cache(self, sql: str, params=None):
        """Executa uma query SELECT no cache local."""
        if not self._cache_conn:
            return None
        sql_sqlite = self._converter_sql(sql)
        cursor = self._cache_conn.cursor()
        cursor.execute(sql_sqlite, params or ())
        return cursor

    def _converter_sql(self, sql: str) -> str:
        """Converte sintaxe MySQL para SQLite (backticks -> aspas duplas)."""
        resultado = sql.replace("`", '"')
        resultado = re.sub(r'%s', '?', resultado)
        return resultado

    def _converter_valores(self, valores):
        """Converte tipos MySQL incompativeis com SQLite."""
        convertidos = []
        for v in valores:
            if isinstance(v, Decimal):
                convertidos.append(float(v))
            elif hasattr(v, 'isoformat'):
                convertidos.append(str(v))
            else:
                convertidos.append(v)
        return convertidos

    def inserir_cache(self, sql: str, params=None):
        """Insere dados no cache local."""
        if not self._cache_conn:
            return
        try:
            sql_sqlite = self._converter_sql(sql)
            valores = self._converter_valores(params) if params else ()
            cursor = self._cache_conn.cursor()
            cursor.execute(sql_sqlite, valores)
            self._cache_conn.commit()
        except sqlite3.Error as e:
            logger.debug("Erro ao inserir no cache: %s", e)

    def commitar_cache(self):
        if self._cache_conn:
            self._cache_conn.commit()

    def _criar_schema_local(self):
        """Cria tabelas no SQLite local (espelho do MySQL)."""
        schema = """
        CREATE TABLE IF NOT EXISTS "agente ibama" (
            matricula INTEGER PRIMARY KEY,
            senha TEXT NOT NULL,
            email TEXT NOT NULL,
            nome_agente TEXT NOT NULL,
            cpf TEXT NOT NULL,
            telefone TEXT,
            login TEXT NOT NULL,
            perfil TEXT NOT NULL DEFAULT 'agente',
            status TEXT NOT NULL DEFAULT 'ativo',
            cadastrado_por TEXT,
            atualizado_por TEXT
        );

        CREATE TABLE IF NOT EXISTS infrator (
            id_infrator INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT NOT NULL,
            email TEXT NOT NULL,
            senha TEXT NOT NULL,
            nome_infrator TEXT NOT NULL,
            telefone_infrator TEXT
        );

        CREATE TABLE IF NOT EXISTS tccm (
            processo TEXT PRIMARY KEY,
            documento_sei TEXT,
            data_inicio TEXT,
            semestres INTEGER NOT NULL DEFAULT 1,
            total_pago REAL NOT NULL DEFAULT 0.00,
            total_validado REAL NOT NULL DEFAULT 0.00,
            data_validade TEXT,
            intervalo INTEGER NOT NULL DEFAULT 1,
            total_devido REAL NOT NULL DEFAULT 0.00,
            status TEXT NOT NULL DEFAULT 'pendente',
            agente_ibama_matricula INTEGER NOT NULL,
            infrator_id_infrator INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "nota fiscal" (
            nota_fiscal TEXT PRIMARY KEY,
            semestre INTEGER NOT NULL,
            data TEXT NOT NULL,
            chave_de_acesso TEXT NOT NULL,
            valor_total REAL NOT NULL,
            agente_ibama_matricula INTEGER NOT NULL,
            status_nota TEXT DEFAULT 'Pendente',
            processo TEXT,
            arquivo TEXT
        );

        CREATE TABLE IF NOT EXISTS produtos (
            lote TEXT PRIMARY KEY,
            status_entrega TEXT NOT NULL DEFAULT 'pendente',
            quantidade INTEGER NOT NULL DEFAULT 0,
            preco_unitario REAL NOT NULL,
            data_validade TEXT,
            nota_fiscal_nota_fiscal TEXT NOT NULL,
            nota_fiscal_agente_ibama_matricula INTEGER NOT NULL,
            itens_id INTEGER,
            nome_item TEXT
        );

        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT NOT NULL,
            codigo_interno TEXT NOT NULL,
            categoria TEXT,
            tipo TEXT,
            justificativa TEXT,
            unidade_medida TEXT,
            semestre TEXT,
            quantidade_prevista INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Ativo',
            notas_fiscais TEXT,
            processo TEXT,
            criado_em TEXT
        );

        CREATE TABLE IF NOT EXISTS locais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cep TEXT NOT NULL,
            endereco TEXT NOT NULL,
            instituicao TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            telefone TEXT,
            criado_em TEXT
        );

        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            acao TEXT NOT NULL,
            tabela TEXT NOT NULL,
            descricao TEXT NOT NULL,
            criado_em TEXT
        );

        CREATE TABLE IF NOT EXISTS insumo (
            id_insumo INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT,
            justificativa TEXT,
            link TEXT,
            preco_orcado REAL NOT NULL,
            infrator_id_infrator INTEGER NOT NULL,
            produtos_lote TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS insumo_has_tccm (
            insumo_id_insumo INTEGER NOT NULL,
            insumo_infrator_id_infrator INTEGER NOT NULL,
            insumo_produtos_lote TEXT NOT NULL,
            tccm_processo TEXT NOT NULL,
            tccm_agente_ibama_matricula INTEGER NOT NULL,
            tccm_infrator_id_infrator INTEGER NOT NULL,
            PRIMARY KEY (insumo_id_insumo, insumo_infrator_id_infrator, insumo_produtos_lote,
                         tccm_processo, tccm_agente_ibama_matricula, tccm_infrator_id_infrator)
        );
        """
        self._cache_conn.executescript(schema)

    def _sincronizar_dados(self, conexao_mysql):
        """Copia dados do MySQL para o SQLite local."""
        cursor_mysql = conexao_mysql.cursor(dictionary=True)

        tabelas = [
            ("agente ibama", [
                "matricula", "senha", "email", "nome_agente", "cpf", "telefone",
                "login", "perfil", "status", "cadastrado_por", "atualizado_por"
            ]),
            ("infrator", [
                "id_infrator", "cpf", "email", "senha", "nome_infrator", "telefone_infrator"
            ]),
            ("tccm", [
                "processo", "documento_sei", "data_inicio", "semestres",
                "total_pago", "total_validado", "data_validade", "intervalo",
                "total_devido", "status", "agente ibama_matricula", "infrator_id_infrator"
            ]),
            ("nota fiscal", [
                "nota_fiscal", "semestre", "data", "chave_de_acesso",
                "valor_total", "agente ibama_matricula", "status_nota",
                "processo", "arquivo"
            ]),
            ("produtos", [
                "lote", "status_entrega", "quantidade", "preco_unitario",
                "data_validade", "nota fiscal_nota_fiscal",
                "nota fiscal_agente ibama_matricula", "itens_id", "nome_item"
            ]),
            ("itens", [
                "id", "nome", "descricao", "codigo_interno", "categoria",
                "tipo", "justificativa", "unidade_medida", "semestre",
                "quantidade_prevista", "status", "notas_fiscais", "processo", "criado_em"
            ]),
            ("locais", [
                "id", "cep", "endereco", "instituicao", "responsavel",
                "telefone", "criado_em"
            ]),
            ("logs", [
                "id", "usuario", "acao", "tabela", "descricao", "criado_em"
            ]),
            ("insumo", [
                "id_insumo", "nome", "tipo", "descricao", "justificativa",
                "link", "preco_orcado", "infrator_id_infrator", "produtos_lote"
            ]),
        ]

        for tabela, colunas in tabelas:
            try:
                cursor_mysql.execute(f"SELECT * FROM `{tabela}`")
                dados = cursor_mysql.fetchall()

                if not dados:
                    continue

                colunas_cache = colunas.copy()
                if tabela == "tccm":
                    colunas_cache = [
                        "processo", "documento_sei", "data_inicio", "semestres",
                        "total_pago", "total_validado", "data_validade", "intervalo",
                        "total_devido", "status", "agente_ibama_matricula", "infrator_id_infrator"
                    ]
                elif tabela == "nota fiscal":
                    colunas_cache = [
                        "nota_fiscal", "semestre", "data", "chave_de_acesso",
                        "valor_total", "agente_ibama_matricula", "status_nota",
                        "processo", "arquivo"
                    ]
                elif tabela == "produtos":
                    colunas_cache = [
                        "lote", "status_entrega", "quantidade", "preco_unitario",
                        "data_validade", "nota_fiscal_nota_fiscal",
                        "nota_fiscal_agente_ibama_matricula", "itens_id", "nome_item"
                    ]
                elif tabela == "insumo_has_tccm":
                    colunas_cache = [
                        "insumo_id_insumo", "insumo_infrator_id_infrator",
                        "insumo_produtos_lote", "tccm_processo",
                        "tccm_agente_ibama_matricula", "tccm_infrator_id_infrator"
                    ]

                placeholders = ", ".join(["?"] * len(colunas_cache))
                cols_str = ", ".join([f'"{c}"' for c in colunas_cache])
                sql_insert = f'INSERT OR REPLACE INTO "{tabela}" ({cols_str}) VALUES ({placeholders})'

                cursor_cache = self._cache_conn.cursor()
                for row in dados:
                    valores = []
                    for c in colunas:
                        v = row.get(c)
                        if isinstance(v, Decimal):
                            v = float(v)
                        elif hasattr(v, 'isoformat'):
                            v = str(v)
                        valores.append(v)
                    cursor_cache.execute(sql_insert, valores)
                self._cache_conn.commit()

                logger.info("Cache: %d registros copiados de '%s'", len(dados), tabela)
            except Exception as e:
                logger.warning("Erro ao sincronizar tabela '%s': %s", tabela, e)

        try:
            cursor_mysql.execute("SELECT * FROM insumo_has_TCCM")
            dados = cursor_mysql.fetchall()
            if dados:
                colunas_cache = [
                    "insumo_id_insumo", "insumo_infrator_id_infrator",
                    "insumo_produtos_lote", "TCCM_processo",
                    "TCCM_agente ibama_matricula", "TCCM_infrator_id_infrator"
                ]
                colunas_mysql = colunas_cache.copy()
                placeholders = ", ".join(["?"] * len(colunas_cache))
                cols_str = ", ".join([f'"{c}"' for c in colunas_cache])
                sql_insert = f'INSERT OR REPLACE INTO "insumo_has_tccm" ({cols_str}) VALUES ({placeholders})'

                cursor_cache = self._cache_conn.cursor()
                for row in dados:
                    valores = []
                    for c in colunas_mysql:
                        v = row.get(c)
                        if isinstance(v, Decimal):
                            v = float(v)
                        elif hasattr(v, 'isoformat'):
                            v = str(v)
                        valores.append(v)
                    cursor_cache.execute(sql_insert, valores)
                self._cache_conn.commit()
                logger.info("Cache: %d registros copiados de 'insumo_has_TCCM'", len(dados))
        except Exception as e:
            logger.warning("Erro ao sincronizar insumo_has_TCCM: %s", e)

        cursor_mysql.close()
