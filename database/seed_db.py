#!/usr/bin/env python3
"""
Script para inicializar o banco de dados com dados de teste.
Execute uma única vez após clonar o repositório:
    python database/seed_db.py
"""

from conexaodb import criar_schema, DB_PATH
import os


def main():
    """Cria o banco de dados com schema e dados de teste."""
    if os.path.exists(DB_PATH):
        print(f"✓ Banco de dados já existe em: {DB_PATH}")
        print("  Se deseja reinicializar, delete o arquivo e execute novamente.")
        return

    print(f"Criando banco de dados em: {DB_PATH}")
    criar_schema()
    print("✓ Banco de dados criado com sucesso!")
    print("  Usuários de teste:")
    print("    - admin / senha: admin")
    print("    - agente / senha: agente")
    print("    - usuario / senha: usuario")
    print("  Infratores de teste:")
    print("    - CPF: 12345678901 / senha: senha1")
    print("    - CPF: 23456789012 / senha: senha2")
    print("    - CPF: 34567890123 / senha: senha3")
    print("    - CPF: 45678901234 / senha: senha4")


if __name__ == "__main__":
    main()
