"""Core data contracts for the ORCA Marine agent pipeline.

Every agent speaks these schemas. The hard rule enforced elsewhere
(Controller): no AgentResponse reaches the user without at least one
Evidence entry. This file just defines the shapes.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Query(BaseModel):
    text: str
    language: str | None = None
    session_id: str | None = None


class Evidence(BaseModel):
    source: str  # e.g. "mock_weather.json", "INCOIS PFZ advisory"
    timestamp: str  # ISO8601 of the underlying data, not of the answer
    note: str | None = None


class AgentResponse(BaseModel):
    agent: str
    answer: str
    evidence: list[Evidence] = Field(default_factory=list)
    grounded: bool = True


class DataFetchResult(BaseModel):
    """Uniform shape every DataDiscoveryAgent.get_*() call returns.

    `available=False` means: don't fabricate an answer from this — the
    caller must handle that explicitly (refuse or note the gap), never
    silently substitute a guess.
    """
    dataset: str
    payload: dict | None
    source: str
    timestamp: str
    available: bool
    note: str | None = None


class OrchestratorResponse(BaseModel):
    query: str
    intent: str
    intent_source: str  # "llm" or "rule_based"
    answer: str
    evidence: list[Evidence] = Field(default_factory=list)
    grounded: bool
    context_used: bool = False  # True if a prior turn's location/intent filled a gap this turn
    report_path: str | None = None  # HTML map+evidence report path, if one was generated
