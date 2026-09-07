"""GeospatialAgent — Step 5: delegates fetching to DataDiscoveryAgent.

EEZ (maritime boundary) is LIVE with NO fallback (never guess a boundary).
MPA geofencing is MOCK ONLY (WDPA token gate). Both facts live in
DataDiscoveryAgent now, not here — this agent just composes the two into
one answer.
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.locations import LOCATIONS, resolve_location_key
from app.schemas import AgentResponse, Evidence, Query


class GeospatialAgent(BaseAgent):
    name = "geospatial_agent"

    def __init__(self, data_discovery: DataDiscoveryAgent | None = None) -> None:
        self._dd = data_discovery or DataDiscoveryAgent()

    def handle(self, query: Query) -> AgentResponse:
        matched_key = resolve_location_key(query.text)

        if matched_key is None:
            return AgentResponse(
                agent=self.name,
                answer="No coordinates for that location yet. Known locations: " + ", ".join(LOCATIONS.keys()),
                evidence=[],
                grounded=False,
            )

        loc = LOCATIONS[matched_key]
        evidence: list[Evidence] = []
        answer_parts: list[str] = []

        eez_result = self._dd.get_eez(loc["offshore_lat"], loc["offshore_lon"])
        if eez_result.available:
            answer_parts.append(f"Maritime boundary: within {eez_result.payload['eez_name']}.")
            evidence.append(Evidence(source=eez_result.source, timestamp=eez_result.timestamp, note=eez_result.note))
        else:
            answer_parts.append(f"Maritime boundary: lookup unavailable ({eez_result.note}).")

        mpa_result = self._dd.get_mpa_proximity(loc["lat"], loc["lon"])
        p = mpa_result.payload
        if p["inside"]:
            answer_parts.append(f"GEOFENCE ALERT: inside {p['nearest_mpa']} (Marine Protected Area) — restricted zone.")
        else:
            answer_parts.append(f"Nearest MPA: {p['nearest_mpa']}, ~{p['distance_km']:.0f} km away — outside restricted boundary.")
        answer_parts.append("[MPA check uses MOCK boundary data — see DataDiscoveryAgent docstring]")
        evidence.append(Evidence(source=mpa_result.source, timestamp=mpa_result.timestamp, note=mpa_result.note))

        if not evidence:
            return AgentResponse(agent=self.name, answer=" ".join(answer_parts), evidence=[], grounded=False)

        return AgentResponse(
            agent=self.name,
            answer=f"{loc['display_name']}: " + " ".join(answer_parts),
            evidence=evidence,
            grounded=True,
        )
