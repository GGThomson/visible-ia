from datetime import UTC, datetime

import httpx
import pytest

from visible_ia.heartbeat import HeartbeatError, run_heartbeat

URL = "https://fake.supabase.co"
KEY = "service-SECRET-KEY"
NOW = datetime(2026, 9, 27, 12, 0, tzinfo=UTC)


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_makes_the_three_rest_calls_with_service_role():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.headers["apikey"] == KEY
        assert request.headers["authorization"] == f"Bearer {KEY}"
        if request.method == "GET":
            return httpx.Response(200, json=[])
        if request.method == "POST":
            return httpx.Response(201)
        return httpx.Response(200, json=[{"id": 1}, {"id": 2}])

    result = run_heartbeat(URL, KEY, "dev", client=make_client(handler), now=NOW)

    assert [c.method for c in calls] == ["GET", "POST", "DELETE"]
    assert calls[0].url.path == "/rest/v1/markets"
    assert calls[1].url.path == "/rest/v1/heartbeats"
    assert b'"project":"dev"' in calls[1].content.replace(b" ", b"")
    assert calls[2].url.params["created_at"] == "lt.2026-08-28T12:00:00+00:00"
    assert result.old_deleted == 2


def test_http_error_raises_without_leaking_the_key():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Invalid API key"})

    with pytest.raises(HeartbeatError) as exc:
        run_heartbeat(URL, KEY, "prod", client=make_client(handler), now=NOW)
    assert "leer markets: HTTP 401" in str(exc.value)
    assert KEY not in str(exc.value)


def test_network_error_becomes_heartbeat_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    with pytest.raises(HeartbeatError, match="error de red: ConnectError"):
        run_heartbeat(URL, KEY, "dev", client=make_client(handler), now=NOW)


def test_failure_on_insert_stops_before_delete():
    methods = []

    def handler(request: httpx.Request) -> httpx.Response:
        methods.append(request.method)
        if request.method == "GET":
            return httpx.Response(200, json=[])
        return httpx.Response(500, text="db down")

    with pytest.raises(HeartbeatError, match="insertar heartbeat: HTTP 500"):
        run_heartbeat(URL, KEY, "dev", client=make_client(handler), now=NOW)
    assert methods == ["GET", "POST"]
