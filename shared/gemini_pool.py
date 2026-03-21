"""
shared/gemini_pool.py

Rotating Gemini API key pool using the google.genai SDK.
- Reads GEMINI_API_KEY_1, GEMINI_API_KEY_2, ... (or GEMINI_API_KEY as fallback)
- On 429 / rate-limit, rotates to the next key with exponential back-off
- Thread-safe index rotation via threading.Lock
"""

import os
import threading
import time

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

try:
    from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
except ImportError:
    ResourceExhausted = None
    ServiceUnavailable = None


def _is_retryable(exc: Exception) -> bool:
    if ResourceExhausted and isinstance(exc, ResourceExhausted):
        return True
    if ServiceUnavailable and isinstance(exc, ServiceUnavailable):
        return True
    if isinstance(exc, ClientError) and getattr(exc, "code", None) == 429:
        return True
    if isinstance(exc, ServerError) and getattr(exc, "code", None) == 503:
        return True
    return False

_lock = threading.Lock()
_index = 0
_KEYS: list[str] = []


def _load_keys() -> list[str]:
    keys = []
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    if not keys:
        single = os.getenv("GEMINI_API_KEY")
        if single:
            keys.append(single)
    if not keys:
        raise RuntimeError(
            "No Gemini API keys found. Set GEMINI_API_KEY or GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..."
        )
    return keys


def _get_keys() -> list[str]:
    global _KEYS
    if not _KEYS:
        _KEYS = _load_keys()
    return _KEYS


def _next_key() -> str:
    global _index
    keys = _get_keys()
    with _lock:
        key = keys[_index % len(keys)]
        _index = (_index + 1) % len(keys)
    return key


def generate_with_retry(
    prompt: str,
    model_name: str = "gemini-2.5-flash-lite",
    temperature: float = 0.2,
    response_mime_type: str = "application/json",
) -> str:
    """
    Generate content with automatic key rotation on rate-limit (429).
    Tries every key in the pool before raising.
    """
    keys = _get_keys()
    last_exc = None
    max_attempts = max(len(keys) * 3, 5)  # retry each key up to 3x for 503s

    for attempt in range(max_attempts):
        try:
            client = genai.Client(api_key=_next_key())
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type=response_mime_type,
                ),
            )
            return response.text
        except Exception as e:
            if _is_retryable(e):
                last_exc = e
                time.sleep(min(2 ** attempt, 15))
            else:
                raise

    raise RuntimeError(
        f"All {len(keys)} Gemini API key(s) exhausted or unavailable. Last error: {last_exc}"
    )
