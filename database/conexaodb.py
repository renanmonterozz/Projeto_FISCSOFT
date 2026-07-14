import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.ssl_disabled = False
        self.conexao = None

    def conectar(self):
        try:
            print(f"Conectando ao banco de dados {self.database} em {self.host}, {self.user}, {self.password}, {self.ssl_disabled}...")
            self.conexao = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                ssl_disabled = self.ssl_disabled
            )
            if self.conexao.is_connected():
                return True
        except Error as e:
            print(f"Erro ao conectar ao banco: {e}")
            return False

    def desconectar(self):
        if self.conexao and self.conexao.is_connected():
            self.conexao.close()

    def executar(self, sql, params=None):
        if not self.conexao or not self.conexao.is_connected():
            return None
        cursor = self.conexao.cursor()
        cursor.execute(sql, params or ())
        return cursor

    def commitar(self):
        if self.conexao and self.conexao.is_connected():
            self.conexao.commit()
