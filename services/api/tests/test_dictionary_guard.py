import asyncio

from fastapi import HTTPException
from starlette.requests import Request

from app.services.dictionary import guard


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[str, int | str] = {}
        self.expirations: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        current = int(self.values.get(key, 0))
        current += 1
        self.values[key] = current
        return current

    async def expire(self, key: str, seconds: int) -> bool:
        self.expirations[key] = seconds
        return True

    async def ttl(self, key: str) -> int:
        return self.expirations.get(key, 0)

    async def set(self, key: str, value: str, ex: int | None = None, nx: bool = False) -> bool:
        if nx and key in self.values:
            return False
        self.values[key] = value
        if ex is not None:
            self.expirations[key] = ex
        return True

    async def delete(self, key: str) -> int:
        existed = key in self.values
        self.values.pop(key, None)
        self.expirations.pop(key, None)
        return int(existed)


def build_request(
    headers: dict[str, str] | None = None,
    client_host: str = "127.0.0.1",
) -> Request:
    header_items = []
    for key, value in (headers or {}).items():
        header_items.append((key.lower().encode("utf-8"), value.encode("utf-8")))

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/dictionary/search",
        "headers": header_items,
        "client": (client_host, 12345),
    }
    return Request(scope)


def test_build_dictionary_request_context_uses_authenticated_identity() -> None:
    request = build_request(headers={"authorization": "Bearer dev-token"})

    context = asyncio.run(guard.build_dictionary_request_context(request))

    assert context.identity_key == "user:1"
    assert context.is_authenticated is True


def test_build_dictionary_request_context_falls_back_to_ip() -> None:
    request = build_request(headers={"x-forwarded-for": "198.51.100.8, 10.0.0.1"})

    context = asyncio.run(guard.build_dictionary_request_context(request))

    assert context.identity_key == "ip:198.51.100.8"
    assert context.ip_address == "198.51.100.8"
    assert context.is_authenticated is False


def test_enforce_dictionary_search_rate_limit_blocks_after_threshold(monkeypatch) -> None:
    fake_cache = FakeCache()
    context = guard.DictionaryRequestContext(identity_key="ip:127.0.0.1", ip_address="127.0.0.1")

    class StubSettings:
        dictionary_rate_limit_authenticated_per_minute = 10
        dictionary_rate_limit_anonymous_per_minute = 2

    monkeypatch.setattr(guard, "get_cache", lambda: fake_cache)
    monkeypatch.setattr(guard, "get_settings", lambda: StubSettings())

    asyncio.run(guard.enforce_dictionary_search_rate_limit(context))
    asyncio.run(guard.enforce_dictionary_search_rate_limit(context))

    try:
        asyncio.run(guard.enforce_dictionary_search_rate_limit(context))
    except HTTPException as exc:
        assert exc.status_code == 429
        assert exc.headers == {"Retry-After": "65"}
    else:
        raise AssertionError("Expected the third request to be rate limited")


def test_try_consume_deepseek_budget_respects_daily_limit(monkeypatch) -> None:
    fake_cache = FakeCache()
    context = guard.DictionaryRequestContext(identity_key="user:1", ip_address="127.0.0.1")

    class StubSettings:
        dictionary_deepseek_budget_authenticated_per_day = 2
        dictionary_deepseek_budget_anonymous_per_day = 1

    monkeypatch.setattr(guard, "get_cache", lambda: fake_cache)
    monkeypatch.setattr(guard, "get_settings", lambda: StubSettings())

    assert asyncio.run(guard.try_consume_deepseek_budget(context)) is True
    assert asyncio.run(guard.try_consume_deepseek_budget(context)) is True
    assert asyncio.run(guard.try_consume_deepseek_budget(context)) is False


def test_search_lock_only_allows_one_owner(monkeypatch) -> None:
    fake_cache = FakeCache()

    class StubSettings:
        dictionary_search_lock_seconds = 15

    monkeypatch.setattr(guard, "get_cache", lambda: fake_cache)
    monkeypatch.setattr(guard, "get_settings", lambda: StubSettings())

    assert asyncio.run(guard.try_acquire_dictionary_search_lock("resilience")) is True
    assert asyncio.run(guard.try_acquire_dictionary_search_lock("resilience")) is False
