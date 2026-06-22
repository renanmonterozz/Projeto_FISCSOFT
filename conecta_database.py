import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host='localhost', user='root', password='', database='fiscsoft'): 
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexao = None

    def conectar(self):
        try:
            self.conexao = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conexao.is_connected():
                print("✅ Conexão Estabelecida: O motor do sistema de logística está online!")
                return True
        except Error as e:
            print(f"❌ Erro Crítico: A base de dados não foi encontrada ou a chave de acesso está incorreta.")
            print(f"Detalhes do erro para debug: {e}")
            return False

    def desconectar(self):
        """Encerra a conexão com o banco de forma segura."""
        if self.conexao and self.conexao.is_connected():
            self.conexao.close()