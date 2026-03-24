import httpx

from config import Settings


settings = Settings()


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.lms_api_key}"}


async def get_items() -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{settings.lms_api_base_url}/items/", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def get_pass_rates(lab: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{settings.lms_api_base_url}/analytics/pass-rates",
            params={"lab": lab},
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_scores_histogram(lab: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{settings.lms_api_base_url}/analytics/scores",
            params={"lab": lab},
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_groups(lab: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{settings.lms_api_base_url}/analytics/groups",
            params={"lab": lab},
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_timeline(lab: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{settings.lms_api_base_url}/analytics/timeline",
            params={"lab": lab},
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_completion_rate(lab: str) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{settings.lms_api_base_url}/analytics/completion-rate",
            params={"lab": lab},
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_learners() -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{settings.lms_api_base_url}/learners/", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def get_lab_names() -> list[str]:
    items = await get_items()
    labs = [item.get("title", "") for item in items if item.get("type") == "lab"]
    return labs


async def count_students() -> int:
    learners = await get_learners()
    return len(learners)


async def get_lowest_pass_rate_lab() -> dict:
    items = await get_items()
    labs = [item for item in items if item.get("type") == "lab"]

    best = None
    for idx, lab in enumerate(labs, start=1):
        lab_code = f"lab-{idx:02d}"
        try:
            rows = await get_pass_rates(lab_code)
        except Exception:
            continue
        if not rows:
            continue
        avg = sum(float(r.get("avg_score", 0.0)) for r in rows) / len(rows)
        candidate = {"lab": lab.get("title", lab_code), "avg_score": avg}
        if best is None or avg < best["avg_score"]:
            best = candidate

    return best or {"lab": "Unknown", "avg_score": 0.0}
