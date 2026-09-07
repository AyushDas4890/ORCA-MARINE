"""DataDiscoveryAgent — the single place all live/mock fetching happens.

Formalizes what WeatherAgent, OceanAnalyticsAgent, and GeospatialAgent
each used to do ad-hoc: try a live API, catch specific network/HTTP
failure modes, fall back to mock data when one exists, and stamp the
result with source+timestamp for grounding. That logic lived 3x with
small inconsistencies — now it lives once, and specialist agents depend
on this instead of touching httpx or the data/ JSON files directly.

Not a BaseAgent: this doesn't answer a user Query, it's called BY the
specialist agents. The problem statement calls for a "data discovery"
agent that autonomously retrieves from heterogeneous sources — this is
that piece, with a fetch_*() interface instead of handle(Query) since
its job is structurally different (internal data layer, not an intent
handler).

Per-dataset live/mock status (see README for the full record):
- weather      : LIVE (Open-Meteo, free/no-key) -> falls back to mock_weather.json
- ocean        : MOCK ONLY (no public INCOIS PFZ API exists)
- eez          : LIVE (Marine Regions, free/no-key) -> NO fallback (never
                 guess a maritime boundary; caller must handle unavailable)
- mpa_proximity: MOCK ONLY (WDPA/Protected Planet API needs a
                 registration-gated token; 401 without one)
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.schemas import DataFetchResult

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
EEZ_URL = "https://www.marineregions.org/rest/getGazetteerRecordsByLatLong.json"

# Expected/handleable failure modes for a live call. Anything else (a
# programming bug, an unexpected exception type) is NOT caught here and
# propagates — per "handle errors explicitly, no silent catches".
_LIVE_FAILURE_MODES = (httpx.HTTPError, httpx.TimeoutException, KeyError, StopIteration)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class DataDiscoveryAgent:
    def __init__(self, timeout_s: float = 6.0) -> None:
        self._timeout_s = timeout_s
        with open(_DATA_DIR / "mock_weather.json", encoding="utf-8") as f:
            self._mock_weather = json.load(f)
        with open(_DATA_DIR / "mock_ocean.json", encoding="utf-8") as f:
            self._mock_ocean = json.load(f)
        with open(_DATA_DIR / "mock_mpa.json", encoding="utf-8") as f:
            self._mock_mpa = json.load(f)

    def get_weather(self, location_key: str, lat: float, lon: float) -> DataFetchResult:
        try:
            with httpx.Client(timeout=self._timeout_s) as client:
                w = client.get(WEATHER_URL, params={"latitude": lat, "longitude": lon, "current": "wind_speed_10m,temperature_2m"})
                w.raise_for_status()
                m = client.get(MARINE_URL, params={"latitude": lat, "longitude": lon, "current": "wave_height"})
                m.raise_for_status()
            wj, mj = w.json()["current"], m.json()["current"]
            return DataFetchResult(
                dataset="weather",
                payload={
                    "temp_c": wj["temperature_2m"],
                    "wind_kmph": wj["wind_speed_10m"],
                    "wave_height_m": mj["wave_height"],
                },
                source="Open-Meteo forecast+marine API (open-meteo.com, free/public)",
                timestamp=wj["time"],
                available=True,
            )
        except _LIVE_FAILURE_MODES as exc:
            loc = self._mock_weather["locations"].get(location_key)
            if loc is None:
                return DataFetchResult(
                    dataset="weather", payload=None, source="none", timestamp="",
                    available=False, note=f"live call failed ({exc}) and no mock for this location",
                )
            return DataFetchResult(
                dataset="weather",
                payload={"temp_c": loc["temp_c"], "wind_kmph": loc["wind_kmph"], "wave_height_m": loc["wave_height_m"]},
                source=f"{self._mock_weather['source']} [FALLBACK, live call failed: {exc}]",
                timestamp=self._mock_weather["generated_at"],
                available=True,
                note=f"fallback used — live call failed: {exc}",
            )

    def get_ocean_analytics(self, location_key: str) -> DataFetchResult:
        loc = self._mock_ocean["locations"].get(location_key)
        if loc is None:
            return DataFetchResult(
                dataset="ocean_analytics", payload=None, source="none", timestamp="",
                available=False, note="no data for this location",
            )
        return DataFetchResult(
            dataset="ocean_analytics",
            payload=loc,
            source=self._mock_ocean["source"],
            timestamp=self._mock_ocean["generated_at"],
            available=True,
            note="MOCK — no live INCOIS PFZ API exists (per-district PDF bulletins only)",
        )

    def get_eez(self, offshore_lat: float, offshore_lon: float) -> DataFetchResult:
        try:
            with httpx.Client(timeout=self._timeout_s) as client:
                resp = client.get(f"{EEZ_URL}/{offshore_lat}/{offshore_lon}/")
                resp.raise_for_status()
            records = resp.json()
            eez = next(r for r in records if r["placeType"] == "EEZ")
            return DataFetchResult(
                dataset="eez",
                payload={"eez_name": eez["preferredGazetteerName"]},
                source="Marine Regions REST API (marineregions.org, free/public gazetteer)",
                timestamp=datetime.now(timezone.utc).isoformat(),
                available=True,
                note=f"lookup for offshore point lat={offshore_lat}, lon={offshore_lon}",
            )
        except _LIVE_FAILURE_MODES as exc:
            # Deliberately NO mock fallback: guessing a maritime boundary is
            # exactly the kind of fabrication the grounding rule forbids.
            return DataFetchResult(
                dataset="eez", payload=None, source="none", timestamp="",
                available=False, note=f"live call failed: {exc} — not guessing a maritime boundary",
            )

    def get_mpa_proximity(self, lat: float, lon: float) -> DataFetchResult:
        best = min(self._mock_mpa["areas"], key=lambda a: _haversine_km(lat, lon, a["lat"], a["lon"]))
        distance_km = _haversine_km(lat, lon, best["lat"], best["lon"])
        return DataFetchResult(
            dataset="mpa_proximity",
            payload={
                "nearest_mpa": best["name"],
                "distance_km": distance_km,
                "radius_km": best["radius_km"],
                "inside": distance_km < best["radius_km"],
            },
            source=self._mock_mpa["source"],
            timestamp=self._mock_mpa["generated_at"],
            available=True,
            note="MOCK — WDPA/Protected Planet API needs a registration-gated token (401 without one)",
        )
