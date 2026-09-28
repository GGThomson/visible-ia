"""Open, update or close a notice issue identified by its title prefix (GitHub REST API).

Used by the daily and monthly jobs to talk to the Director without e-mail: one open issue
per notice, updated in place instead of piling up.
"""

import httpx

API = "https://api.github.com"


def upsert_issue(
    prefix: str,
    title: str | None,
    body: str | None,
    *,
    repo: str,
    token: str,
    close: bool = False,
    client: httpx.Client | None = None,
) -> str:
    """Create or update the open issue whose title starts with `prefix`; with close=True,
    close it (after updating the body if one is given). Returns what it did."""
    own = client is None
    client = client or httpx.Client(timeout=20)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        found = client.get(
            f"{API}/repos/{repo}/issues",
            params={"state": "open", "per_page": "100"},
            headers=headers,
        )
        found.raise_for_status()
        issue = next(
            (i for i in found.json() if i["title"].startswith(prefix) and "pull_request" not in i),
            None,
        )
        payload = {k: v for k, v in (("title", title), ("body", body)) if v is not None}
        if close:
            if issue is None:
                return "nada"
            client.patch(
                f"{API}/repos/{repo}/issues/{issue['number']}",
                json={**payload, "state": "closed"},
                headers=headers,
            ).raise_for_status()
            return "cerrado"
        if issue is None:
            client.post(
                f"{API}/repos/{repo}/issues", json=payload, headers=headers
            ).raise_for_status()
            return "creado"
        client.patch(
            f"{API}/repos/{repo}/issues/{issue['number']}", json=payload, headers=headers
        ).raise_for_status()
        return "actualizado"
    finally:
        if own:
            client.close()
