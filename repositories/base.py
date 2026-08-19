from __future__ import annotations

from database.orm import session_scope


class BaseRepository:
    session_scope = staticmethod(session_scope)
