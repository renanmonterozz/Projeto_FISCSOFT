import mysql.connector
from mysql.connector import Error

from config.database import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class Database:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        self.conexao = None

    def conectar(self):
        try:
            self.conexao = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
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
