import sqlite3, json

DB = r"C:\Users\60291566\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

sid = 'ses_078f7a9b0ffeGO6PNVPNqvZKEm'
print(f"SESSION: {sid}")

cur.execute("SELECT title FROM session WHERE id = ?", (sid,))
row = cur.fetchone()
if row:
    print(f"Title: {row[0]}")

cur.execute("""
    SELECT m.id,
           json_extract(m.data, '$.role') as role,
           m.agent_id,
           m.time_created
    FROM message m
    WHERE m.session_id = ?
    ORDER BY m.time_created, m.id
""", (sid,))
messages = cur.fetchall()

for msg_id, role, agent_id, time_created in messages:
    print(f"\n--- [{role}] agent={agent_id or 'main'} t={time_created} ---")
    cur.execute("""
        SELECT json_extract(p.data, '$.type') as ptype,
               json_extract(p.data, '$.tool') as tool,
               substr(p.data, 1, 1500) as preview
        FROM part p
        WHERE p.message_id = ?
        ORDER BY p.time_created
    """, (msg_id,))
    for ptype, tool, preview in cur.fetchall():
        if ptype == 'text':
            try:
                data = json.loads(preview)
                text = data.get('text', '')[:800]
            except:
                text = preview[:800]
            print(f"  TEXT: {text}")
        elif ptype == 'tool':
            try:
                data = json.loads(preview)
                inp = data.get('state', {}).get('input', {})
                if isinstance(inp, dict):
                    fp = inp.get('file_path', '')
                    pattern = inp.get('pattern', '')
                    content_preview = inp.get('content', '')[:200] if inp.get('content') else ''
                    print(f"  TOOL {tool}: file={fp} pattern={pattern} content={content_preview}")
            except:
                print(f"  TOOL {tool}: {preview[:300]}")

conn.close()
