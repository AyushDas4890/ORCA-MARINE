# Deep Current — ORCA Marine Framer reimagining

## Context
The live ORCA Marine site (`frontend/`) is a React + Framer Motion app. This spec covers a separate creative reimagining of the same site, built in a new Framer (design tool) project, not a change to the React codebase. Same content and purpose, new visual language.

## Visual system: Deep Current
- Base: near-black ocean gradients (`#01050c` → `#062a3d`), never pure black.
- Accent: single bioluminescent cyan (`#00e5ff`) glow, used sparingly and consistently.
- Panels: glassmorphic (translucent, blurred, thin cyan hairline border).
- Layout: asymmetric, overlapping — not centered/symmetric.
- Motion: pulsing glow, parallax depth, staggered scroll reveals across all sections.

## Hero
- Opens on bold typographic statement over a dark still frame — video not yet playing.
- On scroll past the first fold, the existing hero video (`frontend/public/assets/video/hero-video.mp4`, the 3D chrome-ring video) plays full-bleed.
- Video asset is uploaded to Framer as-is — same file, no re-encode, no crop/trim.

## Agents section (8 agents)
- "Depth stack" layout: each agent is a horizontal bar; each successive bar is offset further right and lower, forming a descending dive-profile shape.
- Bar color encodes data status: cyan = live source, muted green = mock/gated — matches the real per-agent status already documented in `app/agents/data_discovery_agent.py` / README (Weather, Geospatial live; Ocean Analytics, MPA proximity mock).
- Bars reveal one at a time on scroll.

## Remaining sections
Mission, Demo ("Ask ORCA"), Platform, Team keep their existing content/copy from the current site. Only presentation changes to match the Deep Current visual system (glass panels, cyan glow, asymmetric grid).

## Execution
Built directly in a new Framer project (ID `DtGqGJfMUV6lkFW3Z8qc`) via the Framer agent CLI — canvas layout, styles, and the video asset upload. Not a code change to `frontend/`.
