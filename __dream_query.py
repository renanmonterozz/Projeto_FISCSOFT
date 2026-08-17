import sqlite3, json, sys

DB = r"C:\Users\60291566\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Get all sessions for this project (sorted newest first)
print("=== ALL SESSIONS FOR THIS PROJECT ===")
cur.execute("""
    SELECT id, title, time_created
    FROM session
    WHERE project_id = 'd9910546-4e1c-4541-8d4e-0104ca8e8193'
    ORDER BY time_created DESC
""")
for row in cur.fetchall():
    print(f"  {row[0]} | {row[1]} | {row[2]}")

# Get all non-checkpoint-writer, non-current sessions
recent_session_ids = []
cur.execute("""
    SELECT id, title, time_created
    FROM session
    WHERE project_id = 'd9910546-4e1c-4541-8d4e-0104ca8e8193'
      AND title NOT LIKE 'checkpoint-writer:%'
      AND id != 'ses_078f7a8dfffeJ4jCbMD2DkQTRo'
    ORDER BY time_created DESC
""")
for row in cur.fetchall():
    recent_session_ids.append(row[0])
    print(f"  Active session: {row[0]} | {row[1]}")

# For each active session, get user messages with keywords
keywords = ["sempre", "nunca", "lembre", "regra", "decidiu", "razao", "decisão",
            "repetir", "novamente", "toda vez", "workflow", "always", "never",
            "remember", "rule", "decision", "tradeoff", "reason",
            "erro", "bug", "fix", "problema", "solução"]

print("\n=== USER MESSAGES CONTAINING KEYWORDS ===")
for sid in recent_session_ids:
    cur.execute("""
        SELECT m.id, substr(json_extract(m.data, '$.role'), 1, 20) as role,
               substr(json_extract(p.data, '$.text'), 1, 500) as text
        FROM message m
        JOIN part p ON p.message_id = m.id
        WHERE m.session_id = ?
          AND json_extract(m.data, '$.role') = 'user'
          AND json_extract(p.data, '$.type') = 'text'
        ORDER BY m.time_created
    """, (sid,))
    for row in cur.fetchall():
        text = row[2] or ""
        text_lower = text.lower()
        for kw in keywords:
            if kw.lower() in text_lower:
                print(f"  [{sid}] {text[:200]}")
                break

print("\n=== ASSISTANT TOOL CALLS (for verifying architecture/decisions) ===")
for sid in recent_session_ids:
    cur.execute("""
        SELECT m.id,
               json_extract(p.data, '$.tool') as tool,
               substr(p.data, 1, 500) as preview
        FROM message m
        JOIN part p ON p.message_id = m.id
        WHERE m.session_id = ?
          AND json_extract(m.data, '$.role') = 'assistant'
          AND json_extract(p.data, '$.type') = 'tool'
        ORDER BY m.time_created
    """, (sid,))
    for row in cur.fetchall():
        tool = row[1] or ""
        preview = row[2] or ""
        if tool in ('write', 'edit', 'read'):
            print(f"  [{sid}] {tool}: {preview[:200]}")

conn.close()
