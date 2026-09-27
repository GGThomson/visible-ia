import json

import httpx

from visible_ia.prospectos import issue_text, sync_issue, unseen_clinics

REPO = "GGThomson/visible-ia"


class FakeGitHub:
    """Minimal GitHub issues API in memory."""

    def __init__(self, issues=None):
        self.issues = issues or []
        self.calls = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.calls.append((request.method, request.url.path))
        if request.method == "GET":
            return httpx.Response(200, json=[i for i in self.issues if i["state"] == "open"])
        payload = json.loads(request.content)
        if request.method == "POST":
            issue = {"number": len(self.issues) + 1, "state": "open", **payload}
            self.issues.append(issue)
            return httpx.Response(201, json=issue)
        number = int(request.url.path.rsplit("/", 1)[1])
        issue = next(i for i in self.issues if i["number"] == number)
        issue.update(payload)
        return httpx.Response(200, json=issue)

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler))


def test_issue_has_count_and_clinics_but_no_contact_data():
    title, body = issue_text(["Clínica Uno", "Clínica Dos"])
    assert title == "Prospectos nuevos (2)"
    assert "- Clínica Uno" in body and "- Clínica Dos" in body
    assert "@" not in body and "+51" not in body


def test_new_requests_open_an_issue_then_update_it():
    gh = FakeGitHub([{"number": 1, "state": "open", "title": "Heartbeat falló (dev)"}])
    assert sync_issue(["Clínica Uno"], repo=REPO, token="t", client=gh.client()) == "creado"
    assert gh.issues[-1]["title"] == "Prospectos nuevos (1)"
    assert (
        sync_issue(["Clínica Uno", "Dos"], repo=REPO, token="t", client=gh.client())
        == "actualizado"
    )
    assert gh.issues[-1]["title"] == "Prospectos nuevos (2)"
    assert gh.issues[0]["title"] == "Heartbeat falló (dev)"  # other issues untouched


def test_no_requests_closes_the_issue_or_does_nothing():
    gh = FakeGitHub([{"number": 7, "state": "open", "title": "Prospectos nuevos (3)"}])
    assert sync_issue([], repo=REPO, token="t", client=gh.client()) == "cerrado"
    assert gh.issues[0]["state"] == "closed"
    assert sync_issue([], repo=REPO, token="t", client=gh.client()) == "nada"


def test_pull_requests_are_not_taken_for_the_issue():
    gh = FakeGitHub(
        [{"number": 3, "state": "open", "title": "Prospectos nuevos: PR", "pull_request": {}}]
    )
    assert sync_issue(["X"], repo=REPO, token="t", client=gh.client()) == "creado"


def test_unseen_clinics_reads_with_the_service_role():
    seen = {}

    def handler(request):
        seen["auth"] = request.headers["Authorization"]
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json=[{"clinic_name": "Clínica Uno"}])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    assert unseen_clinics("https://x.supabase.co", "srk", client=client) == ["Clínica Uno"]
    assert seen["auth"] == "Bearer srk"
    assert seen["params"]["seen"] == "eq.false" and seen["params"]["do_not_contact"] == "eq.false"
