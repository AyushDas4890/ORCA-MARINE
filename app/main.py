"""FastAPI entrypoint. Thin — all logic lives in Controller/agents."""
from __future__ import annotations

from fastapi import FastAPI

from app.controller import Controller
from app.schemas import OrchestratorResponse, Query

app = FastAPI(title="ORCA Marine (SIH26176) — Step 1")
_controller = Controller()


@app.post("/query", response_model=OrchestratorResponse)
def query(q: Query) -> OrchestratorResponse:
    return _controller.handle(q)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
