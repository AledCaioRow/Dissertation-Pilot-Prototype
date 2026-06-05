"""Thin wrapper over the Anthropic SDK.

Every call is temperature 0 and returns the raw request and response JSON so the
backend can store them verbatim. The same model is used for every condition.
"""

import os
import time

from anthropic import Anthropic

MODEL = os.getenv("STUDY_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("STUDY_MAX_TOKENS", "4096"))

_client = None


def client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Put it in backend/.env (see .env.example)."
            )
        _client = Anthropic(api_key=api_key)
    return _client


def complete(system: str, messages: list):
    """Run one model turn at temperature 0.

    ``messages`` is the full window so far (list of {role, content}).
    Returns a dict with: text, request_json, response_json, latency_ms,
    prompt_tokens, completion_tokens.
    """
    request_json = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0,
        "system": system,
        "messages": messages,
    }
    start = time.time()
    resp = client().messages.create(**request_json)
    latency_ms = int((time.time() - start) * 1000)

    text = "".join(block.text for block in resp.content if block.type == "text")
    response_json = resp.model_dump()
    usage = response_json.get("usage", {}) or {}
    return {
        "text": text,
        "request_json": request_json,
        "response_json": response_json,
        "latency_ms": latency_ms,
        "prompt_tokens": usage.get("input_tokens"),
        "completion_tokens": usage.get("output_tokens"),
    }
