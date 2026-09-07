"""OpenAI-backed intent classification, with an explicit fallback.

Design: OpenAI is the primary path when OPENAI_API_KEY is set and the
call succeeds. LLMUnavailable is raised — never a silent None — for every
expected failure mode (no key, network error, rate limit, timeout,
malformed response). Callers (Controller) catch *only* LLMUnavailable and
fall back to rule-based logic; anything else propagates, per the
"handle errors explicitly, no silent catches" rule.
"""
from __future__ import annotations

import os

INTENT_LABELS = ("weather", "ocean", "geospatial", "unknown")

_SYSTEM_PROMPT = (
    "You classify a user's marine/fishing query into exactly one label: "
    "'weather' if it asks about weather, sea conditions, safety of venturing "
    "out, waves, wind, storms, or tides; "
    "'ocean' if it asks about fishing zones, PFZ, chlorophyll, sea surface "
    "temperature, or fish productivity/availability; "
    "'geospatial' if it asks about maritime boundaries, international waters, EEZ, marine protected areas, restricted zones, or geofencing; "
    "otherwise 'unknown'. Respond with ONLY the label, nothing else."
)


class LLMUnavailable(Exception):
    """Raised for any expected reason the LLM path can't be used right now."""


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._model = model

    def classify_intent(self, text: str) -> str:
        if not self._api_key:
            raise LLMUnavailable("OPENAI_API_KEY not set")

        try:
            from openai import OpenAI  # imported lazily so the package is
        except ImportError as exc:                                    # optional until this path is actually used
            raise LLMUnavailable(f"openai package not installed: {exc}") from exc

        try:
            client = OpenAI(api_key=self._api_key)
            resp = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0,
                max_tokens=5,
                timeout=6.0,
            )
        except Exception as exc:  # noqa: BLE001 — deliberately broad: any
            # OpenAI SDK failure (auth, rate limit, timeout, network) is an
            # expected "LLM path unavailable right now" case, not a bug.
            raise LLMUnavailable(f"OpenAI call failed: {exc}") from exc

        label = resp.choices[0].message.content.strip().lower()
        if label not in INTENT_LABELS:
            raise LLMUnavailable(f"unexpected label from model: {label!r}")
        return label
