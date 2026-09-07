"""WeatherAgent — Step 5: delegates all fetching to DataDiscoveryAgent.

No httpx, no JSON files touched here anymore — that plumbing moved to
DataDiscoveryAgent (app/agents/data_discovery_agent.py). This agent's job
is just: match a location, ask the data layer for weather, turn the raw
payload into a grounded, safety-assessed answer.
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.locations import LOCATIONS, resolve_location_key
from app.schemas import AgentResponse, Evidence, Query


class WeatherAgent(BaseAgent):
    name = "weather_agent"

    def __init__(self, data_discovery: DataDiscoveryAgent | None = None) -> None:
        self._dd = data_discovery or DataDiscoveryAgent()

    def handle(self, query: Query) -> AgentResponse:
        matched_key = resolve_location_key(query.text)

        if matched_key is None:
            return AgentResponse(
                agent=self.name,
                answer=(
                    "I don't have weather/marine data for that location yet. "
                    "Known locations right now: " + ", ".join(LOCATIONS.keys())
                ),
                evidence=[],
                grounded=False,
            )

        loc = LOCATIONS[matched_key]
        result = self._dd.get_weather(matched_key, loc["lat"], loc["lon"])

        if not result.available:
            return AgentResponse(
                agent=self.name,
                answer=f"Weather data unavailable for {loc['display_name']}: {result.note}",
                evidence=[],
                grounded=False,
            )

        p = result.payload
        safe = p["wave_height_m"] < 2.0 and p["wind_kmph"] < 35
        safety = "safe to venture out" if safe else "NOT safe to venture out — high wave/wind conditions"
        is_fallback = result.note is not None and "fallback" in result.note.lower()
        prefix = "[FALLBACK DATA] " if is_fallback else ""
        answer = (
            f"{prefix}{loc['display_name']}: temp {p['temp_c']}°C, wind {p['wind_kmph']} km/h, "
            f"wave height {p['wave_height_m']} m. Assessment: {safety}."
        )
        evidence = [Evidence(source=result.source, timestamp=result.timestamp, note=result.note)]
        return AgentResponse(agent=self.name, answer=answer, evidence=evidence, grounded=True)
