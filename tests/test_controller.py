"""Step 5 verification.

DataDiscoveryAgent is now the single dependency-injection seam for
fetching. Fallback/unavailable scenarios are tested by injecting a real
DataDiscoveryAgent whose specific method is monkeypatched to return a
controlled DataFetchResult — no more reaching into agent internals.

No OPENAI_API_KEY is set in this environment on purpose, proving the
LLM->rule-based fallback works without a key or network call to OpenAI.
Live Open-Meteo / Marine Regions calls ARE real (network available here).
"""
from pathlib import Path

from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.controller import Controller
from app.llm import LLMClient, LLMUnavailable
from app.schemas import DataFetchResult, Query


# ---- intent routing + LLM fallback ----

def test_falls_back_to_rule_based_when_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    controller = Controller()
    response = controller.handle(Query(text="Is it safe to venture into the sea near Chennai tomorrow?"))

    assert response.intent_source == "rule_based"
    assert response.intent == "weather"
    assert response.grounded is True
    assert len(response.evidence) >= 1


def test_llm_client_raises_llm_unavailable_without_key():
    client = LLMClient(api_key=None)
    try:
        client.classify_intent("is it safe to sail")
        assert False, "expected LLMUnavailable"
    except LLMUnavailable:
        pass


def test_non_weather_intent_refuses_cleanly():
    controller = Controller()
    response = controller.handle(Query(text="Tell me a joke"))

    assert response.intent == "unknown"
    assert response.grounded is False


# ---- weather (live Open-Meteo + explicit fallback) ----

def test_weather_query_live_or_grounded_fallback():
    controller = Controller()
    response = controller.handle(Query(text="What's the sea condition near Kochi?"))

    assert response.grounded is True
    assert len(response.evidence) >= 1


def test_weather_unknown_location_refuses_rather_than_fabricates():
    controller = Controller()
    response = controller.handle(Query(text="What's the weather near Atlantis?"))

    assert response.grounded is False
    assert response.evidence == []


def test_weather_falls_back_to_mock_when_live_call_fails(monkeypatch):
    dd = DataDiscoveryAgent()
    monkeypatch.setattr(
        dd, "get_weather",
        lambda location_key, lat, lon: DataFetchResult(
            dataset="weather",
            payload={"temp_c": 30.5, "wind_kmph": 18, "wave_height_m": 1.2},
            source="mock_weather.json [FALLBACK, live call failed: simulated]",
            timestamp="2026-09-06T06:00:00Z",
            available=True,
            note="fallback used — live call failed: simulated network failure",
        ),
    )
    controller = Controller(data_discovery=dd)
    response = controller.handle(Query(text="weather near chennai"))

    assert response.grounded is True
    assert "FALLBACK" in response.answer
    assert "FALLBACK" in response.evidence[0].source


# ---- ocean analytics (mock-only, always labelled) ----

def test_ocean_analytics_query_is_grounded():
    controller = Controller()
    response = controller.handle(Query(text="Where is the nearest potential fishing zone near Chennai today?"))

    assert response.intent == "ocean"
    assert response.grounded is True
    assert "MOCK DATA" in response.answer
    assert response.evidence[0].source.startswith("mock_ocean.json")


def test_ocean_analytics_unknown_location_refuses():
    controller = Controller()
    response = controller.handle(Query(text="What's the chlorophyll level near Atlantis?"))

    assert response.grounded is False
    assert response.evidence == []


# ---- geospatial (live EEZ, no fallback + mock MPA) ----

def test_geospatial_query_reports_eez_and_mpa_status():
    controller = Controller()
    response = controller.handle(Query(text="Is there an international boundary or restricted zone near Chennai?"))

    assert response.intent == "geospatial"
    assert response.grounded is True
    assert "Maritime boundary" in response.answer
    assert "MPA check uses MOCK boundary data" in response.answer


def test_geospatial_flags_mpa_geofence_alert_when_inside_radius(monkeypatch):
    from app.agents import geospatial_agent as ga_module

    # LOCATIONS is one shared dict (app.locations.LOCATIONS) imported by
    # name into every agent module — mutate it in place with setitem so
    # resolve_location_key() and every "from app.locations import
    # LOCATIONS" binding see the same change. Replacing the dict wholesale
    # (monkeypatch.setattr to a new dict) does NOT work: other modules'
    # already-bound names would keep pointing at the old object.
    monkeypatch.setitem(ga_module.LOCATIONS, "testzone", {
        "display_name": "Test zone inside Gulf of Mannar",
        "lat": 9.17, "lon": 79.25,
        "offshore_lat": 9.17, "offshore_lon": 79.25,
    })
    agent = ga_module.GeospatialAgent()
    result = agent.handle(Query(text="geofence check near testzone"))

    assert "GEOFENCE ALERT" in result.answer
    assert "Gulf of Mannar" in result.answer


def test_geospatial_eez_lookup_failure_does_not_fabricate_a_boundary(monkeypatch):
    dd = DataDiscoveryAgent()
    monkeypatch.setattr(
        dd, "get_eez",
        lambda offshore_lat, offshore_lon: DataFetchResult(
            dataset="eez", payload=None, source="none", timestamp="",
            available=False, note="live call failed: simulated — not guessing a maritime boundary",
        ),
    )
    controller = Controller(data_discovery=dd)
    response = controller.handle(Query(text="what's the maritime boundary near chennai"))

    # EEZ unavailable but MPA mock still grounds the response overall —
    # the "unavailable" fact is stated, never papered over.
    assert "lookup unavailable" in response.answer
    assert "not guessing a maritime boundary" in response.answer


def test_geospatial_unknown_location_refuses():
    controller = Controller()
    response = controller.handle(Query(text="What's the maritime boundary near Atlantis?"))

    assert response.grounded is False
    assert response.evidence == []


# ---- DataDiscoveryAgent itself ----

def test_data_discovery_ocean_analytics_is_labelled_as_mock():
    dd = DataDiscoveryAgent()
    result = dd.get_ocean_analytics("chennai")

    assert result.available is True
    assert "MOCK" in result.note
    assert result.payload["display_name"] == "Chennai coast, Tamil Nadu"


def test_data_discovery_mpa_proximity_computes_nearest_area():
    dd = DataDiscoveryAgent()
    result = dd.get_mpa_proximity(9.17, 79.25)  # exactly Gulf of Mannar's coords

    assert result.payload["nearest_mpa"] == "Gulf of Mannar Marine National Park"
    assert result.payload["inside"] is True
    assert result.payload["distance_km"] < 1


# ---- multi-turn session memory ----

def test_session_remembers_location_for_followup_query():
    controller = Controller()
    first = controller.handle(Query(text="Is it safe to venture near Chennai tomorrow?", session_id="s1"))
    assert first.grounded is True
    assert first.context_used is False  # nothing borrowed on the first turn

    followup = controller.handle(Query(text="What about the wind speed?", session_id="s1"))
    assert followup.intent == "weather"
    assert followup.grounded is True
    assert followup.context_used is True
    assert "Chennai" in followup.answer


def test_session_remembers_intent_for_ambiguous_followup():
    controller = Controller()
    controller.handle(Query(text="Where is the nearest fishing zone near Kochi?", session_id="s2"))

    followup = controller.handle(Query(text="Kochi", session_id="s2"))
    # bare "Kochi" alone has no ocean/weather keyword -> intent must come
    # from session memory (last_intent="ocean"), location resolves directly
    # from this turn's own text (doesn't need the session fallback for that).
    assert followup.intent == "ocean"
    assert followup.context_used is True


def test_no_session_id_means_no_memory_across_calls():
    controller = Controller()
    controller.handle(Query(text="Is it safe near Chennai?", session_id=None))

    followup = controller.handle(Query(text="What about tomorrow?", session_id=None))
    assert followup.intent == "unknown"
    assert followup.grounded is False
    assert followup.context_used is False


def test_different_sessions_do_not_leak_context():
    controller = Controller()
    controller.handle(Query(text="Is it safe near Chennai?", session_id="alice"))

    bob_followup = controller.handle(Query(text="What about tomorrow?", session_id="bob"))
    assert bob_followup.intent == "unknown"
    assert bob_followup.context_used is False


def test_explicit_new_topic_overrides_session_context():
    controller = Controller()
    controller.handle(Query(text="Is it safe near Chennai?", session_id="s3"))

    # explicit ocean-intent query mentioning a DIFFERENT location — must not
    # be silently overridden by session's remembered weather/Chennai state
    new_topic = controller.handle(Query(text="What's the chlorophyll level near Kochi?", session_id="s3"))
    assert new_topic.intent == "ocean"
    assert "Kochi" in new_topic.answer
    assert new_topic.context_used is False


# ---- viz/reporting ----

def test_grounded_response_gets_a_report(tmp_path):
    from app.agents.reporting_agent import ReportingAgent

    controller = Controller(reporting_agent=ReportingAgent(output_dir=tmp_path))
    response = controller.handle(Query(text="Is it safe to venture near Chennai tomorrow?"))

    assert response.grounded is True
    assert response.report_path is not None
    report_file = Path(response.report_path)
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Chennai" in content
    assert "Gulf of Mannar Marine National Park" in content  # static MPA reference layer
    assert "leaflet" in content.lower()


def test_refused_response_gets_no_report(tmp_path):
    from app.agents.reporting_agent import ReportingAgent

    controller = Controller(reporting_agent=ReportingAgent(output_dir=tmp_path))
    response = controller.handle(Query(text="Tell me a joke"))

    assert response.grounded is False
    assert response.report_path is None
    assert list(tmp_path.iterdir()) == []


def test_report_evidence_table_lists_actual_sources(tmp_path):
    from app.agents.reporting_agent import ReportingAgent

    controller = Controller(reporting_agent=ReportingAgent(output_dir=tmp_path))
    response = controller.handle(Query(text="Where is the nearest fishing zone near Kochi?"))

    content = Path(response.report_path).read_text(encoding="utf-8")
    assert response.evidence[0].source in content
    assert response.evidence[0].timestamp in content


# ---- risk assessment (pure synthesis, no new data source) ----

def test_risk_query_routes_and_grounds():
    controller = Controller()
    response = controller.handle(Query(text="What's the risk level for going fishing near Chennai?"))

    assert response.intent == "risk"
    assert response.grounded is True
    assert "RISK LEVEL" in response.answer
    assert len(response.evidence) >= 2  # weather + mpa at minimum


def test_risk_unknown_location_refuses():
    controller = Controller()
    response = controller.handle(Query(text="What's the hazard level near Atlantis?"))

    assert response.grounded is False
    assert response.evidence == []


def test_risk_low_when_calm_and_outside_mpa(monkeypatch):
    from app.agents.risk_agent import RiskAssessmentAgent

    dd = DataDiscoveryAgent()
    monkeypatch.setattr(
        dd, "get_weather",
        lambda location_key, lat, lon: DataFetchResult(
            dataset="weather", payload={"temp_c": 30.0, "wind_kmph": 10, "wave_height_m": 0.5},
            source="mock", timestamp="2026-09-06T06:00:00Z", available=True,
        ),
    )
    agent = RiskAssessmentAgent(dd)
    result = agent.handle(Query(text="risk near chennai"))

    assert "RISK LEVEL LOW" in result.answer
    assert "score 0/6" in result.answer


def test_risk_high_when_rough_seas_and_high_wind(monkeypatch):
    from app.agents.risk_agent import RiskAssessmentAgent

    dd = DataDiscoveryAgent()
    monkeypatch.setattr(
        dd, "get_weather",
        lambda location_key, lat, lon: DataFetchResult(
            dataset="weather", payload={"temp_c": 28.0, "wind_kmph": 42, "wave_height_m": 2.8},
            source="mock", timestamp="2026-09-06T06:00:00Z", available=True,
        ),
    )
    agent = RiskAssessmentAgent(dd)
    result = agent.handle(Query(text="risk near kochi"))

    assert "RISK LEVEL HIGH" in result.answer
    assert "score 4/6" in result.answer


def test_risk_penalizes_being_inside_an_mpa(monkeypatch):
    from app.agents.risk_agent import RiskAssessmentAgent

    dd = DataDiscoveryAgent()
    monkeypatch.setattr(
        dd, "get_weather",
        lambda location_key, lat, lon: DataFetchResult(
            dataset="weather", payload={"temp_c": 30.0, "wind_kmph": 10, "wave_height_m": 0.5},
            source="mock", timestamp="2026-09-06T06:00:00Z", available=True,
        ),
    )
    monkeypatch.setattr(
        dd, "get_mpa_proximity",
        lambda lat, lon: DataFetchResult(
            dataset="mpa_proximity",
            payload={"nearest_mpa": "Gulf of Mannar Marine National Park", "distance_km": 0.1, "radius_km": 5, "inside": True},
            source="mock_mpa.json", timestamp="2026-09-06T06:00:00Z", available=True,
        ),
    )
    agent = RiskAssessmentAgent(dd)
    result = agent.handle(Query(text="risk near chennai"))

    assert "RISK LEVEL MODERATE" in result.answer  # score 2: MPA penalty only
    assert "restricted zone" in result.answer


def test_risk_refuses_rather_than_guessing_when_weather_unavailable(monkeypatch):
    from app.agents import risk_agent as ra_module

    monkeypatch.setitem(ra_module.LOCATIONS, "noweatherzone", {
        "display_name": "No-weather test zone",
        "lat": 1.0, "lon": 1.0, "offshore_lat": 1.0, "offshore_lon": 1.0,
    })
    dd = DataDiscoveryAgent()
    monkeypatch.setattr(
        dd, "get_weather",
        lambda location_key, lat, lon: DataFetchResult(
            dataset="weather", payload=None, source="none", timestamp="",
            available=False, note="live call failed and no mock for this location",
        ),
    )
    agent = ra_module.RiskAssessmentAgent(dd)
    result = agent.handle(Query(text="risk near noweatherzone"))

    assert result.grounded is False
    assert result.evidence == []
    assert "unavailable" in result.answer
