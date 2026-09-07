"""FastAPI entrypoint. Thin — all logic lives in Controller/agents."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.controller import Controller
from app.schemas import OrchestratorResponse, Query

_REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ORCA Marine (SIH26176)")

# Demo-scope CORS: the frontend is a static file (file:// or any static
# host) with no fixed origin, and this is a hackathon demo, not a
# multi-tenant service handling user credentials — wildcard is the right
# tradeoff here, not a default to carry into a real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves ReportingAgent's generated HTML (map + evidence table) so the
# frontend can link straight to it instead of needing filesystem access.
app.mount("/reports", StaticFiles(directory=_REPORTS_DIR), name="reports")

_controller = Controller()


@app.post("/query", response_model=OrchestratorResponse)
def query(q: Query) -> OrchestratorResponse:
    return _controller.handle(q)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
