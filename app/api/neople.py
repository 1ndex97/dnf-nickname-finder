from __future__ import annotations

import logging
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://api.neople.co.kr/df"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class NeopleApiError(RuntimeError):
    pass


@dataclass(slots=True)
class RateLimiter:
    calls_per_second: float
    _last_call: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def wait(self) -> None:
        if self.calls_per_second <= 0:
            return
        interval = 1.0 / self.calls_per_second
        with self._lock:
            elapsed = time.monotonic() - self._last_call
            if elapsed < interval:
                time.sleep(interval - elapsed)
            self._last_call = time.monotonic()


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 5.0
    jitter_seconds: float = 0.15

    def delay_for_attempt(self, attempt: int) -> float:
        exponential = self.base_delay_seconds * (2 ** max(attempt - 1, 0))
        return min(
            exponential + random.uniform(0, self.jitter_seconds), self.max_delay_seconds
        )


class NeopleClient:
    def __init__(
        self,
        api_key: str,
        timeout: float = 10.0,
        rate_limit_per_second: float = 3.0,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(rate_limit_per_second)
        self.retry_policy = retry_policy or RetryPolicy()

    def search_character(
        self, server_id: str, character_name: str
    ) -> list[dict[str, Any]]:
        if not self.api_key:
            raise NeopleApiError("Neople API key is not configured.")

        url = f"{BASE_URL}/servers/{server_id}/characters"
        params = {
            "characterName": character_name,
            "apikey": self.api_key,
            "wordType": "match",
        }
        last_error: Exception | None = None

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            self.rate_limiter.wait()
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                if response.status_code in RETRYABLE_STATUS_CODES:
                    raise NeopleApiError(
                        f"Retryable Neople status {response.status_code}"
                    )
                response.raise_for_status()
                payload = response.json()
                rows = payload.get("rows", [])
                LOGGER.debug(
                    "Neople search succeeded",
                    extra={
                        "server": server_id,
                        "nickname": character_name,
                        "rows": len(rows),
                    },
                )
                return list(rows)
            except (requests.RequestException, NeopleApiError) as exc:
                last_error = exc
                if attempt >= self.retry_policy.max_attempts:
                    break
                delay = self.retry_policy.delay_for_attempt(attempt)
                LOGGER.warning(
                    "Neople search failed; retrying",
                    extra={
                        "server": server_id,
                        "nickname": character_name,
                        "attempt": attempt,
                        "delay": delay,
                    },
                    exc_info=exc,
                )
                time.sleep(delay)
            except ValueError as exc:
                raise NeopleApiError("Invalid JSON response from Neople API") from exc

        LOGGER.error(
            "Neople search failed after retries",
            extra={"server": server_id, "nickname": character_name},
            exc_info=last_error,
        )
        raise NeopleApiError(
            str(last_error) if last_error else "Unknown Neople API error"
        )
