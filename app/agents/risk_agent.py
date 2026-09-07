"""RiskAssessmentAgent — Step 8: pure synthesis, no new data source.

Combines what WeatherAgent, OceanAnalyticsAgent, and GeospatialAgent each
already fetch via DataDiscoveryAgent into one hazard/safety verdict.
Deliberately simple and explainable (not ML) — every point in the score
traces to a named threshold below, so the "why" is always answerable.

Scoring (0-6, higher = more hazardous):
- wave_height_m:  <1.0 -> 0   1.0-2.5 -> +1   >2.5 -> +2
- wind_kmph:       <20 -> 0    20-35  -> +1    >35 -> +2
- inside an MPA (geofenced/restricted zone) -> +2 (regulatory risk, not physical)

Bands: 0-1 LOW, 2-3 MODERATE, 4+ HIGH.

Ocean-analytics (PFZ/chlorophyll/SST) is reported alongside for context
but NOT scored — "unfavourable" fishing conditions are a productivity
signal, not a safety hazard, and folding them into a hazard score would
misrepresent what the number means.

If weather data is unavailable (live call failed AND no mock for the
location), this agent cannot ground a verdict and says so — it does not
guess a hazard level from partial or missing data.
"""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.locations import LOCATIONS, resolve_location_key
from app.schemas import AgentResponse, Evidence, Query

_WAVE_MODERATE_M = 1.0
_WAVE_HIGH_M = 2.5
_WIND_MODERATE_KMPH = 20.0
_WIND_HIGH_KMPH = 35.0
_MPA_PENALTY = 2

_LOW_MAX = 1
_MODERATE_MAX = 3


def _band(score: int) -> str:
    if score <= _LOW_MAX:
        return "LOW"
    if score <= _MODERATE_MAX:
        return "MODERATE"
    return "HIGH"


class RiskAssessmentAgent(BaseAgent):
    name = "risk_agent"

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

        weather = self._dd.get_weather(matched_key, loc["lat"], loc["lon"])
        if not weather.available:
            return AgentResponse(
                agent=self.name,
                answer=f"{loc['display_name']}: can't produce a risk verdict — weather data unavailable ({weather.note}). Not guessing a hazard level from missing data.",
                evidence=[],
                grounded=False,
            )
        evidence.append(Evidence(source=weather.source, timestamp=weather.timestamp, note=weather.note))

        wave_m = weather.payload["wave_height_m"]
        wind_kmph = weather.payload["wind_kmph"]

        score = 0
        reasons: list[str] = []
        if wave_m > _WAVE_HIGH_M:
            score += 2
            reasons.append(f"wave height {wave_m:.1f}m (>{_WAVE_HIGH_M}m)")
        elif wave_m >= _WAVE_MODERATE_M:
            score += 1
            reasons.append(f"wave height {wave_m:.1f}m ({_WAVE_MODERATE_M}-{_WAVE_HIGH_M}m)")

        if wind_kmph > _WIND_HIGH_KMPH:
            score += 2
            reasons.append(f"wind {wind_kmph:.0f} km/h (>{_WIND_HIGH_KMPH} km/h)")
        elif wind_kmph >= _WIND_MODERATE_KMPH:
            score += 1
            reasons.append(f"wind {wind_kmph:.0f} km/h ({_WIND_MODERATE_KMPH}-{_WIND_HIGH_KMPH} km/h)")

        mpa = self._dd.get_mpa_proximity(loc["lat"], loc["lon"])
        evidence.append(Evidence(source=mpa.source, timestamp=mpa.timestamp, note=mpa.note))
        if mpa.payload["inside"]:
            score += _MPA_PENALTY
            reasons.append(f"inside {mpa.payload['nearest_mpa']} restricted zone")

        band = _band(score)
        reason_text = "; ".join(reasons) if reasons else "no elevated factors detected"

        ocean = self._dd.get_ocean_analytics(matched_key)
        ocean_note = ""
        if ocean.available:
            evidence.append(Evidence(source=ocean.source, timestamp=ocean.timestamp, note=ocean.note))
            fav = "favourable" if ocean.payload["favourable"] else "unfavourable"
            ocean_note = f" Fishing conditions: {fav} (informational, not scored into this hazard level)."

        answer = (
            f"{loc['display_name']}: RISK LEVEL {band} (score {score}/6). "
            f"Basis: {reason_text}.{ocean_note} "
            "[Deterministic threshold-based score — see RiskAssessmentAgent docstring, not ML.]"
        )

        return AgentResponse(agent=self.name, answer=answer, evidence=evidence, grounded=True)
