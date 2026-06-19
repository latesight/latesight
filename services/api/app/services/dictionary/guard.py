import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.core.cache import get_cache
from app.core.config import get_settings
from app.schemas.auth import UserProfile
from app.services.auth.service import get_user_for_access_token
from app.services.dictionary.cache import get_cached_dictionary_entry

RATE_LIMIT_KEY_PREFIX = "dict:v1:ratelimit:search"
DEEPSEEK_BUDGET_KEY_PREFIX = "dict:v1:budget:deepseek"
SEARCH_LOCK_KEY_PREFIX = "dict:v1:lock:search"


@dataclass(frozen=True)
class DictionaryRequestContext:
    identity_key: str
    ip_address: str
    user: UserProfile | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None


def _normalize_token(authorization: str | None) -> str:
    if not authorization:
        return ""

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return ""
    return token.strip()


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        first_hop = forwarded_for.split(",")[0].strip()
        if first_hop:
            return first_hop[:64]

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip[:64]

    client_host = request.client.host if request.client else ""
    return (client_host or "unknown")[:64]


async def build_dictionary_request_context(request: Request) -> DictionaryRequestContext:
    ip_address = _get_client_ip(request)
    token = _normalize_token(request.headers.get("authorization"))
    user = await get_user_for_access_token(token)

    if user is not None:
        return DictionaryRequestContext(
            identity_key=f"user:{user.id}",
            ip_address=ip_address,
            user=user,
        )

    return DictionaryRequestContext(identity_key=f"ip:{ip_address}", ip_address=ip_address)


def _rate_limit_key(context: DictionaryRequestContext, current_time: datetime) -> str:
    bucket = current_time.strftime("%Y%m%d%H%M")
    return f"{RATE_LIMIT_KEY_PREFIX}:{context.identity_key}:{bucket}"


def _deepseek_budget_key(context: DictionaryRequestContext, current_time: datetime) -> str:
    bucket = current_time.strftime("%Y%m%d")
    return f"{DEEPSEEK_BUDGET_KEY_PREFIX}:{context.identity_key}:{bucket}"


def _search_lock_key(word: str) -> str:
    normalized = word.strip().lower()
    return f"{SEARCH_LOCK_KEY_PREFIX}:{normalized}"


async def enforce_dictionary_search_rate_limit(context: DictionaryRequestContext) -> None:
    settings = get_settings()
    limit = (
        settings.dictionary_rate_limit_authenticated_per_minute
        if context.is_authenticated
        else settings.dictionary_rate_limit_anonymous_per_minute
    )
    if limit <= 0:
        return

    now = datetime.now(UTC)
    key = _rate_limit_key(context, now)

    try:
        cache = get_cache()
        current_count = await cache.incr(key)
        if current_count == 1:
            await cache.expire(key, 65)
        if current_count <= limit:
            return

        ttl = await cache.ttl(key)
    except RedisError:
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many dictionary searches. Please try again shortly.",
        headers={"Retry-After": str(max(ttl, 1))},
    )


async def try_consume_deepseek_budget(context: DictionaryRequestContext) -> bool:
    settings = get_settings()
    limit = (
        settings.dictionary_deepseek_budget_authenticated_per_day
        if context.is_authenticated
        else settings.dictionary_deepseek_budget_anonymous_per_day
    )
    if limit <= 0:
        return False

    now = datetime.now(UTC)
    key = _deepseek_budget_key(context, now)

    try:
        cache = get_cache()
        current_count = await cache.incr(key)
        if current_count == 1:
            await cache.expire(key, 60 * 60 * 25)
        return current_count <= limit
    except RedisError:
        return True


async def try_acquire_dictionary_search_lock(word: str) -> bool:
    settings = get_settings()
    lock_ttl_seconds = max(settings.dictionary_search_lock_seconds, 1)

    try:
        cache = get_cache()
        acquired = await cache.set(_search_lock_key(word), "1", ex=lock_ttl_seconds, nx=True)
    except RedisError:
        return True

    return bool(acquired)


async def release_dictionary_search_lock(word: str) -> None:
    try:
        cache = get_cache()
        await cache.delete(_search_lock_key(word))
    except RedisError:
        return


async def wait_for_dictionary_cache_fill(word: str) -> bool:
    settings = get_settings()
    timeout_ms = max(settings.dictionary_search_lock_wait_ms, 0)
    if timeout_ms <= 0:
        return False

    deadline = asyncio.get_running_loop().time() + (timeout_ms / 1000)
    while asyncio.get_running_loop().time() < deadline:
        if await get_cached_dictionary_entry(word) is not None:
            return True
        await asyncio.sleep(0.05)

    return False
