"""Shared demo-location coordinates.

Single source of truth so WeatherAgent, OceanAnalyticsAgent, and
GeospatialAgent all key off the same 3 locations instead of drifting.

Two coordinate sets per location: `lat/lon` is the town/coastal centroid
(used for weather/ocean lookups); `offshore_lat/offshore_lon` is a point
a few km out to sea, used for the EEZ/maritime-boundary check — the town
centroid itself often resolves as land, not water, in the Marine Regions
gazetteer (verified: 13.0827/80.2707 returns no EEZ record; the offshore
points below were checked and do).

Replace with a real geocoding + coastline-offset lookup once query volume
needs more than these 3 demo points.
"""
from __future__ import annotations

LOCATIONS: dict[str, dict] = {
    "chennai": {
        "display_name": "Chennai coast, Tamil Nadu",
        "lat": 13.0827, "lon": 80.2707,
        "offshore_lat": 12.9, "offshore_lon": 80.6,
    },
    "kochi": {
        "display_name": "Kochi coast, Kerala",
        "lat": 9.9312, "lon": 76.2673,
        "offshore_lat": 9.85, "offshore_lon": 75.9,
    },
    "visakhapatnam": {
        "display_name": "Visakhapatnam coast, Andhra Pradesh",
        "lat": 17.6868, "lon": 83.2185,
        "offshore_lat": 17.6, "offshore_lon": 83.6,
    },
}


def resolve_location_key(text: str) -> str | None:
    """Find a known location mentioned in free text, or None.

    Single source of truth for this — was duplicated inline in every
    specialist agent; Controller also needs it now for session-context
    resolution (see app/session_store.py).
    """
    text_lower = text.lower()
    return next((key for key in LOCATIONS if key in text_lower), None)
