import sqlite3, json, os

DB = r"C:\Users\60291566\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Get full first user message from ses_078f7a9b0ffeGO6PNVPNqvZKEm
sid = 'ses_078f7a9b0ffeGO6PNVPNqvZKEm'
cur.execute("""
    SELECT p.data
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE m.session_id = ?
      AND json_extract(m.data, '$.role') = 'user'
      AND json_extract(p.data, '$.type') = 'text'
    ORDER BY m.time_created
    LIMIT 1
""", (sid,))
row = cur.fetchone()
if row and row[0]:
    data = json.loads(row[0])
    text = data.get('text', '')
    print(text[:5000])

# Also check git status
print("\n\n=== VERIFYING FILE STATE ===")
screens_dir = r"C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT\screens"
if os.path.exists(screens_dir):
    for f in sorted(os.listdir(screens_dir)):
        fpath = os.path.join(screens_dir, f)
        size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
        print(f"  {f} ({size} bytes)")

main_path = r"C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT\main.py"
if os.path.exists(main_path):
    size = os.path.getsize(main_path)
    print(f"  main.py ({size} bytes)")

conn_path = r"C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT\conexaodb.py"
if os.path.exists(conn_path):
    size = os.path.getsize(conn_path)
    print(f"  conexaodb.py ({size} bytes)")

db_path = r"C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT\database"
if os.path.exists(db_path):
    for f in sorted(os.listdir(db_path)):
        fpath = os.path.join(db_path, f)
        size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
        print(f"  database/{f} ({size} bytes)")

cfg_path = r"C:\Users\60291566\Documents\GitHub\Projeto_FISCSOFT\config"
if os.path.exists(cfg_path):
    for f in sorted(os.listdir(cfg_path)):
        fpath = os.path.join(cfg_path, f)
        size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
        print(f"  config/{f} ({size} bytes)")

conn.close()
