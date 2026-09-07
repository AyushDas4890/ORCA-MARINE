"""Base contract every specialist agent implements.

Keeping this tiny on purpose: Step 1 only needs to prove the loop works,
not a full plugin framework. Extend when the 2nd agent (ocean-analytics)
is added.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import AgentResponse, Query


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def handle(self, query: Query) -> AgentResponse:
        """Return a grounded AgentResponse, or one with grounded=False
        and an explanatory answer if the agent cannot ground the query
        in its data. Never fabricate evidence."""
        raise NotImplementedError
