"""In-memory multi-turn session memory.

Deliberately dict-backed, in-process — no new dependency. A Redis/DB
store is the obvious upgrade once this needs to survive a process
restart or run across multiple workers; not needed at this stage.

What it remembers per session_id: the last resolved location and intent,
so a follow-up like "what about tomorrow?" or "is it safe there?" can be
answered without repeating the location/topic every turn.

Known limitation (documented, not hidden): the LLM intent classifier
(app/llm.py) only ever sees the current message, not conversation
history — so on an ambiguous follow-up it may also say "unknown", same
as the rule-based path. Context fallback here only kicks in when the
CURRENT turn's classification is unknown; it never overrides an explicit
different topic. Feeding real conversation history to the LLM classifier
is a future upgrade, not implemented yet.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionState:
    last_location: str | None = None
    last_intent: str | None = None
    turn_count: int = 0


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        return self._sessions.setdefault(session_id, SessionState())

    def update(self, session_id: str, *, location: str | None, intent: str) -> None:
        state = self.get(session_id)
        if location is not None:
            state.last_location = location
        state.last_intent = intent
        state.turn_count += 1
