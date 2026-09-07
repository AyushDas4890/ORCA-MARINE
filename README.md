# ORCA Marine — SIH26176

Agentic AI platform for marine ecosystem reasoning (ISRO problem statement).

## Build status

**Step 1 (done):** agentic loop proven end-to-end with mocked data + rule-based intent routing.

**Step 2 (done):** 
- WeatherAgent now calls **Open-Meteo** (open-meteo.com — free, no API key, confirmed reachable) for live weather + marine (wave height) data. Falls back to local mock data if the live call fails, and says so explicitly in both the answer and the evidence (never silent).
- Intent detection now tries **OpenAI** first (`OPENAI_API_KEY` env var), falls back to keyword rules if no key / call fails / rate limited. Which path was used is reported in every response as `intent_source` ("llm" or "rule_based") — auditable, not hidden.

## Run

```
pip install -r requirements.txt
pytest -v
uvicorn app.main:app --reload
```

To enable the OpenAI path:
```
export OPENAI_API_KEY=sk-...
```
Without it, the system runs fully on free/no-key paths (Open-Meteo + keyword rules) — this is the current default and costs nothing.

## Hard rule (non-negotiable, from risk analysis)
Every agent response MUST carry evidence (source + timestamp). Controller
refuses to answer if no agent can ground the query. Safety-critical domain
(fishermen may act on this) — no ungrounded output, ever.

**Step 3 (done):** OceanAnalyticsAgent (PFZ/chlorophyll/SST) added.
Checked INCOIS first — no public REST API, only per-district PDF bulletins (api.incois.gov.in doesn't resolve, portal PFZ page 404s on direct fetch). Running on mock data, clearly labelled `[MOCK DATA]` in every answer — scraping INCOIS bulletins is real work, tracked as a follow-up, not faked.

**Step 4 (done):** GeospatialAgent (maritime boundary + MPA geofencing) added.
- Maritime boundary: **real, live** data from Marine Regions (marineregions.org/rest — free, no key, confirmed working) — returns the EEZ a point falls in.
- MPA geofencing: Protected Planet/WDPA has the real shapefiles but its API needs a registration-gated token (api.protectedplanet.net returned 401 with no key) — same blocker class as MOSDAC/IMD. Running on a small curated point+radius mock of 3 major Indian MPAs (Gulf of Mannar, Gulf of Kutch, Malvan) instead, clearly labelled `[MPA check uses MOCK...]` in every answer. Real WDPA shapefile + polygon intersection (geopandas/shapely) is the upgrade path once a token is obtained.
- Refactored: location coordinates now live in `app/locations.py`, shared by all 3 agents (was duplicated in weather_agent before). Each location has both a town centroid and an offshore point — the EEZ lookup needs the offshore point (verified: town centroids often resolve as land, not water, in the gazetteer).

**Step 5 (done):** DataDiscoveryAgent added — formalizes what WeatherAgent/OceanAnalyticsAgent/GeospatialAgent each used to do ad-hoc (live API call, catch specific failure modes, fall back to mock, stamp source+timestamp). All fetching now lives in ONE place: `app/agents/data_discovery_agent.py`. The 3 specialist agents no longer touch httpx or the data/ JSON files directly — they take a `DataDiscoveryAgent` dependency and just turn its raw payloads into answers. Controller builds one shared instance and injects it into all three (was: each agent loading its own mock JSON separately).

Per-dataset live/mock status, now documented in one place (DataDiscoveryAgent's docstring):
| dataset | status |
|---|---|
| weather | LIVE (Open-Meteo) -> falls back to mock |
| ocean_analytics (PFZ) | MOCK ONLY (no public INCOIS API) |
| eez (maritime boundary) | LIVE (Marine Regions) -> NO fallback (never guess a boundary) |
| mpa_proximity | MOCK ONLY (WDPA API needs a registration-gated token) |

Testing got easier as a side effect: fallback/unavailable scenarios are now tested by injecting a `DataDiscoveryAgent` with one method monkeypatched, instead of reaching into each agent's private implementation.

**Step 6 (done):** memory/session agent — multi-turn context.
- `app/session_store.py`: in-memory (dict-backed, no new dependency) `SessionStore` tracks last resolved location + intent per `session_id`.
- Controller now resolves a follow-up like *"what about the wind speed?"* after a Chennai weather query by filling in the missing location from session memory — and *"Kochi"* alone after a PFZ query resolves the missing intent the same way. Every response now carries `context_used: bool` so this is auditable, not hidden.
- Explicit new-topic queries are never silently overridden by session memory — context fallback only fires when the current turn's own classification is `unknown`.
- **Known limitation, documented not hidden:** the LLM intent classifier only sees the current message, not conversation history — so it can also say `unknown` on a bare follow-up. Feeding real history to the LLM classifier is a future upgrade.
- Consolidated `resolve_location_key()` into `app/locations.py` (single source of truth — was duplicated inline in all 3 agents).
- **Regression caught before shipping:** a geospatial test broke after the location-key consolidation because it monkeypatched a module-level `LOCATIONS` reference that other modules had already bound separately; fixed with `monkeypatch.setitem` on the shared dict instead of replacing it wholesale. Full suite re-run confirmed green before calling this done — this is why regressions get run after every change here, not just once at the end.

**Step 7 (done):** ReportingAgent — viz/reporting.
- `app/agents/reporting_agent.py` renders a self-contained HTML report (Leaflet map + evidence table) for every **grounded** response — never for a refusal, since there's nothing evidenced to visualize there.
- No new Python dependency: Leaflet loads from CDN inside a plain HTML file (cdnjs) rather than adding folium/geopandas. Map centers on the query's resolved location, shows a marker with the full answer as a popup, and always overlays the 3 known MPA reference circles for geofencing context.
- `OrchestratorResponse.report_path` points at the generated file (`reports/<timestamp>-<query-slug>.html`), `None` when nothing was grounded to report.
- Verified against a real query, not just the test suite — actually opened the generated file path and confirmed content, not just asserted the return value.

**Step 8 (done):** RiskAssessmentAgent — pure synthesis, no new data source.
- Combines weather (wave height + wind), MPA proximity, and ocean-analytics (informational only, not scored) into one deterministic 0-6 hazard score -> LOW/MODERATE/HIGH band. Every threshold is named in the docstring, not tuned/ML — the "why" behind any score is always answerable.
- Refuses rather than guesses: if weather data is unavailable (live call failed and no mock for the location), it says so instead of producing a hazard level from partial data.
- Wired into Controller as a 4th routed intent ("risk"): keywords chosen to avoid colliding with the existing "weather" intent (which already owns "safe"/"venture" — dropped an overlapping "safe to fish" keyword candidate for exactly this reason).
- 6 new tests (dependency-injection style, consistent with the rest of the suite) — full suite is 28/28 passing, not just the new ones.
- All 8 agents from the original roster now exist: Controller, Weather, Ocean Analytics, Geospatial, Data Discovery, Memory/Session, Reporting, Risk Assessment.

## Next
Backend roster complete. Open items: real WDPA/INCOIS integration if API access is obtained later; FastAPI/Streamlit demo layer; SIH team roster (still solo as of now — 6-member/1-woman/SPOC rule not yet satisfied, see project docs).

## Frontend

**Hero section (done):** `frontend/index.html` — built from the actual Claude Design export (`ORCA Marine Hero.html`, a self-unpacking 29MB bundle), not reconstructed from spec. Extracted the bundle's manifest (assets) and template (markup) directly: video, 7 Inter woff2 subsets, and the real layout/copy/animation-timing all came out of the export itself. The bundle's own `x-dc`/`sc-camel-*` component runtime was replaced with plain HTML + ~30 lines vanilla JS for the mobile menu — same behavior, no framework dependency. Applied the `apple-design` skill on top: pointerdown-triggered press feedback (not gated on click), `prefers-reduced-motion` fallback (cross-fade instead of the rise/slide keyframes), Escape-to-close on the mobile overlay.

**Bug found + fixed:** the exported hero video was 4K (3828x2164) at H.264 level 5.1, 17.5 Mbps — decodes unreliably as a looping background on real hardware, rendered blank instead of erroring. Re-encoded to 1920x1086, High profile / level 4.1, 4.2MB (was 21MB), audio stripped, faststart. Added a poster frame + on-page error banner so a future decode failure is visible instead of a silent blank page.

**Known leftover:** `frontend/assets/runtime.js` (68KB, the Design tool's own unused component runtime) — device sandbox won't allow deleting it without an explicit permission grant. Harmless, nothing references it.

**Mission / Agents / Platform / Team sections (done):** all four nav targets now exist and are real content, not filler:
- Mission — the problem statement + the hard grounding rule, pulled from actual project reasoning.
- Agents — all 8 agents from the roster, each with its real live/mock status (matches the DataDiscoveryAgent docstring table above), including Risk Assessment marked honestly as *In Progress*, not built.
- Platform — actual stack facts (FastAPI/Pydantic, Open-Meteo + Marine Regions as live sources, INCOIS/WDPA as gated -> mock, OpenAI-with-fallback intent layer).
- Team — SIH 2026 rules stated (6 members, 1+ woman, SPOC-cleared), 6 empty seat placeholders. Roster intentionally left blank rather than invented — not finalized yet.

Single-file `frontend/index.html`, same design system throughout (Inter, `#5E0ED7` accent, uppercase tracked labels, clamp()-based responsive type).
