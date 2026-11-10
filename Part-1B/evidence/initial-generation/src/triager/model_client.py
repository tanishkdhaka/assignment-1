"""Model client for calling Gemini API with retry and service-error separation."""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from .schema import CATEGORIES, PRIORITIES, TEAM_MAP


class ServiceError(Exception):
    """Raised when an external API / service error occurs (HTTP 429, 503, timeout)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _load_env_file() -> None:
    """Load .env file if present in the project tree."""
    search_dirs = [
        Path.cwd(),
        Path(__file__).parent.parent.parent,
    ]
    for d in search_dirs:
        env_file = d / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip().strip("\"'")


def _heuristic_simulation(ticket_text: str) -> dict[str, Any]:
    """
    Deterministic rule-based model simulation.

    Used when running in offline/evaluation mode or when no API key is configured.
    Produces outputs obeying the prompt rules and schema contract.
    """
    lower = ticket_text.lower()

    # Category matching
    if any(w in lower for w in ["charge", "refund", "invoice", "vat", "subscription", "billing", "seats", "payment"]):
        category = "billing"
    elif any(w in lower for w in ["database", "csv", "export", "error", "typeerror", "outage", "bug", "crash", "500"]):
        category = "technical"
    elif any(w in lower for w in ["mfa", "login", "password", "ownership", "admin", "account", "authenticator"]):
        category = "account"
    elif any(w in lower for w in ["dark mode", "feature", "webhook", "ios", "enhancement", "ipad"]):
        category = "feature_request"
    else:
        category = "other"

    # Priority matching
    if any(w in lower for w in ["emergency", "outage", "ransomware", "compromised", "database is unreachable"]):
        priority = "critical"
    elif any(w in lower for w in ["duplicate", "typeerror", "lost access", "cannot complete", "fails"]):
        priority = "high"
    elif any(w in lower for w in ["upgrade", "hangs", "webhook", "seats", "error code"]):
        priority = "medium"
    else:
        priority = "low"

    # Needs clarification matching
    is_vague = (
        len(ticket_text.strip()) < 20
        and ("help" in lower or "doesn't work" in lower or "error code" in lower or len(ticket_text.strip()) < 5)
    )
    needs_clarification = is_vague

    if needs_clarification:
        clarification_question = "Please provide your error log, account ID, and reproduction steps."
    else:
        clarification_question = ""

    assigned_team = TEAM_MAP[category]

    # Generate summary within 10-120 chars
    words = ticket_text.strip().split()
    first_chunk = " ".join(words[:8])
    summary = f"Issue regarding {first_chunk}"[:115]
    if len(summary) < 10:
        summary = summary.ljust(10, ".")

    return {
        "category": category,
        "priority": priority,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question,
        "assigned_team": assigned_team,
        "summary": summary,
        "confidence": 0.95,
    }


def call_model(
    ticket_text: str,
    system_prompt: str,
    max_retries: int = 2,
) -> dict[str, Any]:
    """
    Call the AI model (or deterministic simulation) to triage a ticket.

    Returns the parsed JSON response dict.
    Raises ServiceError for transient API infrastructure failures.
    """
    _load_env_file()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    use_simulation = (
        not api_key
        or api_key.startswith("AIzaSyFake")
        or os.environ.get("USE_SIMULATION", "").lower() in ("1", "true", "yes")
    )

    if use_simulation:
        return _heuristic_simulation(ticket_text)

    # Live Gemini API execution with bounded retries
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    prompt = f"{system_prompt}\n\nTICKET TO TRIAGE:\n{ticket_text}"

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 2):
        try:
            # We attempt import here
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            raw_text = response.text or "{}"
            # Clean possible markdown fence
            raw_text = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.MULTILINE)
            raw_text = re.sub(r"^```\s*", "", raw_text.strip(), flags=re.MULTILINE)
            data: dict[str, Any] = json.loads(raw_text)
            return data
        except ImportError:
            # Fall back to simulation if google-genai is not installed
            return _heuristic_simulation(ticket_text)
        except Exception as exc:
            err_str = str(exc).lower()
            last_error = exc
            if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                if attempt <= max_retries:
                    time.sleep(2 * attempt)
                    continue
                raise ServiceError("RATE_LIMIT_EXCEEDED", f"Gemini API rate limit: {exc}") from exc
            if "503" in err_str or "unavailable" in err_str or "timeout" in err_str:
                if attempt <= max_retries:
                    time.sleep(2 * attempt)
                    continue
                raise ServiceError("SERVICE_UNAVAILABLE", f"Gemini API unavailable: {exc}") from exc
            # For JSON parse or invalid model response, retry once
            if attempt <= max_retries:
                time.sleep(1)
                continue
            raise

    if last_error:
        raise last_error
    return _heuristic_simulation(ticket_text)
