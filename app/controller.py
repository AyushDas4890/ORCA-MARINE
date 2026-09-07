"""Controller (orchestrator) — Step 7: viz/reporting attached.

One DataDiscoveryAgent instance is shared across all specialist agents
(Step 5). One SessionStore instance tracks multi-turn context (Step 6).
One ReportingAgent (Step 7) now renders an HTML map+evidence report for
every GROUNDED response — never for a refusal, nothing to visualize
there. report_path on the response points at the generated file, or
stays None if rendering was skipped.

Routing is still a dict-lookup by intent label; LLM path classifies
directly among the known labels (single-turn only, no history — session
fallback only fires when the CURRENT turn's classification is
"unknown", never overriding an explicit different topic).

Hard rule unchanged: never grounded=True without an agent producing
grounded=True + non-empty evidence.
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.agents.geospatial_agent import GeospatialAgent
from app.agents.ocean_agent import OceanAnalyticsAgent
from app.agents.reporting_agent import ReportingAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.weather_agent import WeatherAgent
from app.llm import LLMClient, LLMUnavailable
from app.locations import resolve_location_key
from app.schemas import OrchestratorResponse, Query
from app.session_store import SessionStore

_KEYWORDS_BY_INTENT: dict[str, tuple[str, ...]] = {
    "weather": ("weather", "safe", "venture", "wave", "wind", "sea condition", "tide", "storm", "cyclone", "rain"),
    "ocean": ("pfz", "fishing zone", "chlorophyll", "fish productivity", "sst", "sea surface temperature", "where to fish"),
    "geospatial": ("boundary", "eez", "international water", "geofenc", "protected area", "marine park", "restricted zone", "cross border", "maritime border"),
    "risk": ("risk", "hazard", "safety score", "hazard level", "should i go", "is it risky", "go fishing today"),
}


class Controller:
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        data_discovery: DataDiscoveryAgent | None = None,
        session_store: SessionStore | None = None,
        reporting_agent: ReportingAgent | None = None,
    ) -> None:
        dd = data_discovery or DataDiscoveryAgent()
        self._agents: dict[str, BaseAgent] = {
            "weather": WeatherAgent(dd),
            "ocean": OceanAnalyticsAgent(dd),
            "geospatial": GeospatialAgent(dd),
            "risk": RiskAssessmentAgent(dd),
        }
        self._llm = llm_client or LLMClient()
        self._sessions = session_store or SessionStore()
        self._reporting = reporting_agent or ReportingAgent()

    def _detect_intent(self, text: str) -> tuple[str, str]:
        try:
            return self._llm.classify_intent(text), "llm"
        except LLMUnavailable:
            return self._detect_intent_rule_based(text), "rule_based"

    def _detect_intent_rule_based(self, text: str) -> str:
        text_lower = text.lower()
        for intent, keywords in _KEYWORDS_BY_INTENT.items():
            if any(kw in text_lower for kw in keywords):
                return intent
        return "unknown"

    def handle(self, query: Query) -> OrchestratorResponse:
        intent, intent_source = self._detect_intent(query.text)
        session_state = self._sessions.get(query.session_id) if query.session_id else None

        context_used = False
        if intent == "unknown" and session_state and session_state.last_intent not in (None, "unknown"):
            intent = session_state.last_intent
            context_used = True

        agent = self._agents.get(intent)
        if agent is None:
            if session_state is not None:
                self._sessions.update(query.session_id, location=None, intent="unknown")
            return OrchestratorResponse(
                query=query.text,
                intent="unknown",
                intent_source=intent_source,
                answer=(
                    "I can't confidently ground an answer to this yet — only "
                    "weather/marine-safety, ocean-analytics/PFZ, geospatial/geofencing, "
                    "and risk/hazard queries are wired up so far."
                ),
                evidence=[],
                grounded=False,
            )

        effective_text = query.text
        location_key = resolve_location_key(query.text)
        if location_key is None and session_state and session_state.last_location:
            location_key = session_state.last_location
            effective_text = f"{query.text} {location_key}"
            context_used = True

        result = agent.handle(Query(text=effective_text, language=query.language, session_id=query.session_id))

        if session_state is not None:
            self._sessions.update(query.session_id, location=location_key, intent=intent)

        grounded = result.grounded and bool(result.evidence)
        orchestrator_response = OrchestratorResponse(
            query=query.text,
            intent=intent,
            intent_source=intent_source,
            answer=result.answer,
            evidence=result.evidence,
            grounded=grounded,
            context_used=context_used,
        )
        if grounded:
            report_path = self._reporting.render(orchestrator_response, location_key)
            if report_path is not None:
                orchestrator_response.report_path = str(report_path)
        return orchestrator_response
