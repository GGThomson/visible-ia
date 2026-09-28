import json

import httpx
import pytest

from visible_ia.clientes import AuthAdmin, ClientError, normalize_email


@pytest.mark.parametrize(
    "raw, expected",
    [(" Ana@Clinica.PE ", "ana@clinica.pe"), ("dr.x+panel@gmail.com", "dr.x+panel@gmail.com")],
)
def test_normalize_email(raw, expected):
    assert normalize_email(raw) == expected


@pytest.mark.parametrize("raw", ["sin-arroba", "a@b", "a b@c.pe", ""])
def test_invalid_email(raw):
    with pytest.raises(ClientError):
        normalize_email(raw)


def _auth(responses, calls):
    def handler(request):
        calls.append((request.method, request.url.path, dict(request.url.params),
                      json.loads(request.content or b"{}")))  # fmt: skip
        return responses.pop(0)

    return AuthAdmin(
        "https://x.supabase.co", "srk", httpx.Client(transport=httpx.MockTransport(handler))
    )


def test_invite_posts_email_and_redirect():
    calls = []
    auth = _auth([httpx.Response(200, json={"id": "u-1"})], calls)
    assert auth.invite("a@b.pe", "https://site/panel/") == "u-1"
    method, path, _, body = calls[0]
    assert (method, path) == ("POST", "/auth/v1/invite")
    assert body == {"email": "a@b.pe", "redirect_to": "https://site/panel/"}


def test_sign_in_never_creates_a_user():
    calls = []
    auth = _auth([httpx.Response(200, json={})], calls)
    auth.send_sign_in("a@b.pe", "https://site/panel/")
    _, path, params, body = calls[0]
    assert path == "/auth/v1/otp" and body["create_user"] is False
    assert params["redirect_to"] == "https://site/panel/"


def test_generate_link_for_new_and_existing_users():
    calls = []
    auth = _auth(
        [
            httpx.Response(200, json={"id": "u-2", "action_link": "https://x/verify?t=1"}),
            httpx.Response(
                200, json={"user": {"id": "u-3"}, "properties": {"action_link": "https://x/v?t=2"}}
            ),
        ],
        calls,
    )
    assert auth.generate_link("a@b.pe", "r", new=True) == ("u-2", "https://x/verify?t=1")
    assert auth.generate_link("c@d.pe", "r", new=False) == ("u-3", "https://x/v?t=2")
    assert [c[3]["type"] for c in calls] == ["invite", "magiclink"]


def test_auth_errors_are_reported():
    auth = _auth([httpx.Response(422, text="email rate limit exceeded")], [])
    with pytest.raises(ClientError, match="422"):
        auth.invite("a@b.pe", "r")
