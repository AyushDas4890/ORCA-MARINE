"""OceanAnalyticsAgent — Step 5: delegates fetching to DataDiscoveryAgent.

PFZ/chlorophyll/SST data is MOCK ONLY (see DataDiscoveryAgent docstring —
no public INCOIS REST API exists). grounded=True is still returned since
the mock IS labelled, evidenced data; the answer always says MOCK so
nobody mistakes this for a live feed.
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.locations import LOCATIONS, resolve_location_key
from app.schemas import AgentResponse, Evidence, Query


class OceanAnalyticsAgent(BaseAgent):
    name = "ocean_analytics_agent"

    def __init__(self, data_discovery: DataDiscoveryAgent | None = None) -> None:
        self._dd = data_discovery or DataDiscoveryAgent()

    def handle(self, query: Query) -> AgentResponse:
        matched_key = resolve_location_key(query.text)

        if matched_key is None:
            return AgentResponse(
                agent=self.name,
                answer=(
                    "No PFZ/ocean-analytics data for that location yet. "
                    "Known locations: " + ", ".join(LOCATIONS.keys())
                ),
                evidence=[],
                grounded=False,
            )

        result = self._dd.get_ocean_analytics(matched_key)
        if not result.available:
            return AgentResponse(
                agent=self.name,
                answer=f"Ocean-analytics data unavailable: {result.note}",
                evidence=[],
                grounded=False,
            )

        p = result.payload
        outlook = "favourable fishing conditions" if p["favourable"] else "poor fishing conditions"
        answer = (
            f"{p['display_name']}: nearest Potential Fishing Zone ~{p['nearest_pfz_km']} km "
            f"{p['pfz_bearing']}. Chlorophyll {p['chlorophyll_mg_m3']} mg/m³, "
            f"SST {p['sst_c']}°C. Outlook: {outlook}. [MOCK DATA — {result.note}]"
        )
        evidence = [Evidence(source=result.source, timestamp=result.timestamp, note=result.note)]
        return AgentResponse(agent=self.name, answer=answer, evidence=evidence, grounded=True)
