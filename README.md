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

**Frontend <-> backend wired (done):** the site is no longer a static mockup next to a working API — they actually talk to each other.
- `app/main.py`: added CORS (wildcard — a hackathon demo with a file:// frontend and no user credentials, not a production default to carry forward) and a `/reports` static mount so the browser can open a generated report directly instead of needing filesystem access.
- `frontend/index.html`: new **Try It / Ask ORCA** section (`#demo`) — real text input, 4 sample queries, calls `POST /query` on `localhost:8000`, renders the grounded/not-grounded badge, intent, answer, full evidence list, and a link to the generated map report. Clear inline error if the backend isn't running (most likely failure mode for a judge trying this cold). The "Explore ORCA" CTAs (hero + mobile menu) now point here instead of to the static Platform section.
- Verified live, not just asserted: started uvicorn, hit `/query` and the CORS preflight over curl, confirmed the JSON response and report generation for real; extracted the page's own `<script>` block and ran it through `node --check` for a syntax sanity pass. Full test suite re-run after all of this: still 28/28.
- Added `pytest.ini` (`testpaths = tests`) — a stray scratch file outside `tests/` was being auto-collected by pytest's default discovery and threw 6 spurious failures; this scopes collection properly instead of relying on nothing else ending up named `test_*.py`.

## Run the full demo
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open `frontend/index.html` in a browser and use the **Ask ORCA** section — it talks to the backend at `localhost:8000`.

## Next
Real WDPA/INCOIS integration if API access is obtained later. SIH team roster — still solo as of now, 6-member/1-woman/SPOC rule not yet satisfied (see project docs).

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

## Frontend rewrite: React + Framer Motion + taste-skill-v1 (done)

The static `frontend/index.html` above is superseded. The live frontend is now a real React app (Vite + Tailwind CSS v4 + Framer Motion), built to remove CSS-approximated motion in favor of actual spring physics, and to apply the `taste-skill-v1` design skill on top.

**Explicit scope, agreed with the user before starting** (this was a dependency + architecture change, flagged and confirmed first):
- Full rewrite to React + Framer Motion approved.
- The hero's 3D chrome-ring video is preserved byte-for-byte — same re-encoded `hero-video.mp4`/`poster.jpg`, just served from `frontend/public/assets/video/` instead of `frontend/assets/video/`.
- taste-skill-v1 explicitly approved to override the original visual identity: purple `#5E0ED7` and Inter are gone. New palette is near-black ink (`#0a0a0c`, never pure `#000`) with a single desaturated accent (`#2f5fe0`, Electric Blue) on a white base; font is Outfit (Google Fonts), not Inter.

**Structure:**
- `frontend/` is now a normal Vite project: `package.json`, `vite.config.js` (`@vitejs/plugin-react` + `@tailwindcss/vite`), `index.html`, `src/index.css` (Tailwind v4 `@theme` tokens), `src/main.jsx`, `src/App.jsx`, `src/components/{Nav,Hero,Mission,Demo,Agents,Platform,Team}.jsx`.
- The old static site moved intact to `frontend/legacy-static/` (kept as a backup, not deleted).
- `Demo.jsx` is the same live "Ask ORCA" tool as before, now as a proper React component: `fetch('http://localhost:8000/query')`, sample-query buttons, evidence list, and a report link — functionally identical to the static version's JS, no backend changes needed.
- Agents section was redesigned from a plain grid into a divided list (taste-skill bans the generic "3 equal cards" layout) — same 8 agents, same accurate live/mock/mixed status per agent.
- Every section uses `whileInView` + `staggerChildren` reveals and spring transitions (`type: 'spring', stiffness: 100-140, damping: 16-20`) instead of linear CSS easing; hero uses `min-h-[100dvh]`, not `h-screen`, per taste-skill's mobile-viewport-jump rule.
- Dropped `oxlint` from `devDependencies` — it isn't needed (no lint step wired into `npm run build`) and its dependency tree of dozens of platform-specific optional binaries made `npm install` take 170s+ before timing out; removing it brought fresh installs down to 2-5s.

**Verification note (read before assuming it "just works"):** this was built and synced from a sandboxed device shell with no way to open a browser against a live dev server, so verification here was `npm run build` succeeding, `npm run preview` + `curl` HTTP-level checks (correct 200s and byte sizes for the HTML/JS/CSS/video), and grepping the built JS bundle for expected content strings — not a visual look at the rendered page. Run it yourself to confirm the design reads the way it's supposed to:
```
cd frontend
npm install
npm run dev
```

**Known leftovers on disk, not cleaned up (delete is blocked in this sandbox without an explicit permission grant):**
- `frontend/src/App.css`, `frontend/src/assets/{hero.png,react.svg,vite.svg}` — Vite's default scaffold files, unused (nothing imports them).
- `frontend/.oxlintrc.json` — irrelevant now that oxlint was dropped.
- `frontend/_react_src_tmp/` — scratch staging folder used to sync source files onto this machine; safe to delete.
- `frontend/node_modules/` at the project root (~109MB) — a partial install (45 packages) from an earlier attempt directly on this machine, before the build was moved to a faster location for speed. It's already gitignored either way; running `npm install` will just complete/replace it.

None of these are wired into the build or referenced anywhere, so they're inert — just clutter worth deleting by hand when convenient.
