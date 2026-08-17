import sqlite3, json

DB = r"C:\Users\60291566\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

for sid in ['ses_0b68ffcfbffegH1mXzAAHyNT2Z', 'ses_0b6cc60f0ffeaEgLz5p2wMsamf']:
    print(f"\n{'='*80}")
    print(f"SESSION: {sid}")
    print(f"{'='*80}")

    # Title
    cur.execute("SELECT title FROM session WHERE id = ?", (sid,))
    row = cur.fetchone()
    if row:
        print(f"Title: {row[0]}")

    # All messages with parts
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
                # Extract text
                try:
                    data = json.loads(preview)
                    text = data.get('text', '')[:500]
                except:
                    text = preview[:500]
                print(f"  TEXT: {text}")
            elif ptype == 'tool':
                try:
                    data = json.loads(preview)
                    inp = data.get('state', {}).get('input', {})
                    if isinstance(inp, dict):
                        # Show file_path or other key info
                        fp = inp.get('file_path', '')
                        old = inp.get('old_string', '')[:200]
                        new = inp.get('new_string', '')[:200]
                        content = inp.get('content', '')[:200]
                        print(f"  TOOL {tool}: file={fp}")
                        if old:
                            print(f"    OLD: {old}")
                        if new:
                            print(f"    NEW: {new}")
                        if content:
                            print(f"    CONTENT: {content}")
                except:
                    print(f"  TOOL {tool}: {preview[:300]}")

conn.close()
