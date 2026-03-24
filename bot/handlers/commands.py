import httpx

from config import Settings


settings = Settings()


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.lms_api_key}"}


async def _get_items() -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{settings.lms_api_base_url}/items/",
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


async def _get_pass_rates(lab: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{settings.lms_api_base_url}/analytics/pass-rates",
            params={"lab": lab},
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


def _extract_labs(items: list[dict]) -> list[dict]:
    labs = [item for item in items if item.get("type") == "lab"]
    labs.sort(key=lambda x: x.get("id", 0))
    return labs


def _normalize_lab_arg(raw: str) -> str:
    raw = raw.strip().lower()

    if raw.startswith("lab-"):
        return raw

    if raw.startswith("lab "):
        num = raw.split()[-1]
        return f"lab-{int(num):02d}"

    if raw.isdigit():
        return f"lab-{int(raw):02d}"

    return raw


def _format_help() -> str:
    return (
        "Available commands:\n"
        "/start - show welcome message\n"
        "/help - show available commands\n"
        "/health - check backend status and item count\n"
        "/labs - list available labs\n"
        "/scores <lab> - show pass-rate data for a lab\n"
        "Examples:\n"
        "/scores lab-04\n"
        "/scores 4"
    )


def _format_labs(items: list[dict]) -> str:
    labs = _extract_labs(items)
    if not labs:
        return "No labs found."

    lines = ["Labs:"]
    for idx, lab in enumerate(labs, start=1):
        title = lab.get("title", "Untitled lab")
        lines.append(f"{idx}. {title}")
    return "\n".join(lines)


def _format_scores(lab: str, data: list[dict]) -> str:
    lines = [f"Scores for {lab}:"]

    if not data:
        lines.append("No data found.")
        return "\n".join(lines)

    total = 0.0
    count = 0

    for row in data:
        task = row.get("task", "Unknown task")
        avg_score = float(row.get("avg_score", 0.0))
        attempts = int(row.get("attempts", 0))
        lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")
        total += avg_score
        count += 1

    if count > 0:
        lines.append(f"Summary: {total / count:.1f}%")

    return "\n".join(lines)


async def handle_command(text: str) -> str:
    text = (text or "").strip()

    if text == "/start":
        return (
            "Welcome to LMS Bot!\n"
            "Use /help to see available commands.\n"
            "You can also try /labs and /scores lab-04."
        )

    if text == "/help":
        return _format_help()

    if text == "/health":
        try:
            items = await _get_items()
            return f"Backend is running OK. Items loaded: {len(items)}"
        except Exception as e:
            return f"Health check failed: {e}"

    if text == "/labs":
        try:
            items = await _get_items()
            return _format_labs(items)
        except Exception as e:
            return f"Failed to fetch labs: {e}"

    if text.startswith("/scores"):
        parts = text.split(maxsplit=1)

        if len(parts) < 2:
            return "Usage: /scores <lab>\nExample: /scores lab-04"

        lab = _normalize_lab_arg(parts[1])

        try:
            data = await _get_pass_rates(lab)
            return _format_scores(lab, data)
        except Exception as e:
            return f"Failed to fetch scores for {lab}: {e}"

    return "Unknown command. Use /help."
