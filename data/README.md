# Pasta de Dados - FISCSOFT

Este diretório contém o banco de dados SQLite da aplicação.

## Inicialização

O arquivo `fiscsoft.db` é criado automaticamente na primeira execução da aplicação. Se precisar reinicializar o banco com dados de teste:

```bash
python database/seed_db.py
```

## Estrutura

- `fiscsoft.db` — Banco de dados SQLite (gerado dinamicamente, não versionado)

## Backup

Para fazer backup do banco antes de fazer alterações:

```bash
cp fiscsoft.db fiscsoft.db.backup
```
