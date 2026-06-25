import os

import mysql.connector
from mysql.connector import Error

from config.database import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from database.connection import Database

SCHEMA_SQL = os.path.join(os.path.dirname(__file__), "schema.sql")


def criar_banco_se_nao_existe():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao criar banco: {e}")
        return False


def executar_schema():
    db = Database()
    if not db.conectar():
        return False

    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        sql = f.read()

    comandos = [cmd.strip() for cmd in sql.split(";") if cmd.strip()]
    for comando in comandos:
        try:
            db.executar(comando)
        except Error:
            pass

    db.commitar()
    db.desconectar()
    return True


def inicializar():
    if not criar_banco_se_nao_existe():
        return False
    return executar_schema()
