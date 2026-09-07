"""ReportingAgent — viz/reporting specialist.

Produces a self-contained HTML report (Leaflet map + evidence table) for
a grounded OrchestratorResponse. Deliberately NOT a Python geo library
(no folium/geopandas dependency added) — Leaflet is loaded from CDN
inside a plain HTML file, kept dependency-free per "no new deps without
asking first". The map always shows the 3 known MPA reference circles
(static geofencing context) plus a marker at the query's resolved
location, with the full answer text in the popup.

Not intent-routed like the other specialists: Controller calls this
AFTER getting a grounded answer, to attach a visual report — it doesn't
compete for the weather/ocean/geospatial intent slots.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.locations import LOCATIONS
from app.schemas import OrchestratorResponse

MPA_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mock_mpa.json"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "reports"

_LEAFLET_CSS = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
_LEAFLET_JS = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"

_INDIA_DEFAULT_CENTER = (15.0, 80.0)  # fallback when no location resolved


class ReportingAgent:
    def __init__(self, output_dir: Path = DEFAULT_OUTPUT_DIR, mpa_data_path: Path = MPA_DATA_PATH) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        with open(mpa_data_path, encoding="utf-8") as f:
            self._mpa_data = json.load(f)

    def render(self, response: OrchestratorResponse, location_key: str | None) -> Path | None:
        if not response.grounded:
            return None  # nothing evidenced to visualize — don't fake a report

        center = LOCATIONS[location_key] if location_key in LOCATIONS else None
        lat, lon = (center["lat"], center["lon"]) if center else _INDIA_DEFAULT_CENTER
        display_name = center["display_name"] if center else "Unresolved location"

        marker_popup = (
            f"<b>{html.escape(display_name)}</b><br>"
            f"Intent: {html.escape(response.intent)}<br>"
            f"{html.escape(response.answer)}"
        )

        mpa_circles_js = "\n".join(
            f'L.circle([{a["lat"]}, {a["lon"]}], {{radius: {a["radius_km"] * 1000}, '
            f'color: "#c0392b", fillOpacity: 0.08}}).addTo(map)'
            f'.bindPopup("{html.escape(a["name"])} (MPA, radius {a["radius_km"]} km)");'
            for a in self._mpa_data["areas"]
        )

        evidence_rows = "\n".join(
            f"<tr><td>{html.escape(e.source)}</td><td>{html.escape(e.timestamp)}</td>"
            f"<td>{html.escape(e.note or '')}</td></tr>"
            for e in response.evidence
        )

        page = f"""<!doctype html>
<html><head>
<meta charset="utf-8">
<title>ORCA Marine — report</title>
<link rel="stylesheet" href="{_LEAFLET_CSS}">
<script src="{_LEAFLET_JS}"></script>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; }}
  #map {{ height: 60vh; width: 100%; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em; }}
  td, th {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 14px; }}
  h2 {{ margin: 1em; }}
</style>
</head>
<body>
<div id="map"></div>
<h2>Evidence</h2>
<table>
  <tr><th>Source</th><th>Timestamp</th><th>Note</th></tr>
  {evidence_rows}
</table>
<script>
  var map = L.map('map').setView([{lat}, {lon}], 7);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);
  L.marker([{lat}, {lon}]).addTo(map).bindPopup("{marker_popup}").openPopup();
  {mpa_circles_js}
</script>
</body></html>"""

        safe_name = re.sub(r"[^a-z0-9]+", "-", response.query.lower())[:40].strip("-") or "query"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = self._output_dir / f"{timestamp}-{safe_name}.html"
        out_path.write_text(page, encoding="utf-8")
        return out_path
