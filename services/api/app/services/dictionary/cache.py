from typing import Optional

from redis.exceptions import RedisError

from app.schemas.dictionary import DictionarySearchResponse
from app.core.cache import get_cache

DICTIONARY_CACHE_TTL_SECONDS = 60 * 60 * 24
POPULAR_SEARCHES_KEY = "dict:popular_searches"


def _cache_key(word: str) -> str:
    return f"dict:v2:word:{word.strip().lower()}"


async def get_cached_dictionary_entry(word: str) -> Optional[DictionarySearchResponse]:
    try:
        cache = get_cache()
        payload = await cache.get(_cache_key(word))
    except RedisError:
        return None

    if not payload:
        return None

    try:
        return DictionarySearchResponse.model_validate_json(payload)
    except Exception:
        return None


async def set_cached_dictionary_entry(word: str, entry: DictionarySearchResponse) -> None:
    try:
        cache = get_cache()
        await cache.set(_cache_key(word), entry.model_dump_json(), ex=DICTIONARY_CACHE_TTL_SECONDS)
    except RedisError:
        return


async def record_dictionary_search(word: str) -> None:
    normalized = word.strip().lower()
    if not normalized:
        return

    try:
        cache = get_cache()
        await cache.zincrby(POPULAR_SEARCHES_KEY, 1, normalized)
    except RedisError:
        return


async def get_popular_dictionary_searches(limit: int = 10) -> list[str]:
    try:
        cache = get_cache()
        results = await cache.zrevrange(POPULAR_SEARCHES_KEY, 0, max(limit - 1, 0))
    except RedisError:
        return []

    if isinstance(results, list):
        return [item for item in results if isinstance(item, str)]
    return []
