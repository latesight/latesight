from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.dictionary import (
    DefinitionItem,
    DictionarySearchResponse,
    DictionarySuggestionResponse,
    MeaningItem,
)
from app.core.config import get_settings
from app.repositories.dictionary import (
    get_dictionary_cache_by_word,
    save_deepseek_dictionary_response,
    save_provider_dictionary_response,
)
from app.services.dictionary.cache import (
    get_cached_dictionary_entry,
    get_popular_dictionary_searches,
    record_dictionary_search,
    set_cached_dictionary_entry,
)
from app.services.dictionary.deepseek import DeepSeekDictionaryEnricher, DictionaryEnrichmentError
from app.services.dictionary.guard import (
    DictionaryRequestContext,
    enforce_dictionary_search_rate_limit,
    release_dictionary_search_lock,
    try_acquire_dictionary_search_lock,
    try_consume_deepseek_budget,
    wait_for_dictionary_cache_fill,
)
from app.services.dictionary.providers.free_dictionary import (
    DictionaryProviderError,
    DictionaryWordNotFoundError,
    FreeDictionaryProvider,
)

SUGGESTION_SEED_WORDS = [
    "adapt",
    "analysis",
    "articulate",
    "clarity",
    "context",
    "curiosity",
    "discipline",
    "empathy",
    "focus",
    "harmony",
    "insight",
    "iterate",
    "language",
    "momentum",
    "pattern",
    "precision",
    "resilience",
    "serendipity",
    "signal",
    "structure",
    "syntax",
    "utility",
    "vocabulary",
]


async def _search_with_provider(word: str) -> DictionarySearchResponse:
    provider = FreeDictionaryProvider()
    try:
        return await provider.search(word)
    except DictionaryWordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DictionaryProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Dictionary provider is temporarily unavailable.",
        ) from exc


def _get_provider_name() -> str:
    return get_settings().dictionary_provider.strip() or "free_dictionary"


def _load_provider_entry(payload: dict | None) -> DictionarySearchResponse | None:
    if not isinstance(payload, dict) or not payload:
        return None

    try:
        return DictionarySearchResponse.model_validate(payload)
    except Exception:
        return None


def _load_enriched_entry(
    provider_entry: DictionarySearchResponse | None,
    deepseek_payload: dict | None,
) -> DictionarySearchResponse | None:
    if provider_entry is None or not isinstance(deepseek_payload, dict) or not deepseek_payload:
        return None

    try:
        return DeepSeekDictionaryEnricher().apply_saved_payload(provider_entry, deepseek_payload)
    except Exception:
        return None


async def _wait_for_cached_response(word: str) -> DictionarySearchResponse | None:
    if await wait_for_dictionary_cache_fill(word):
        return await get_cached_dictionary_entry(word)
    return None


async def _try_enrich_and_persist(
    db: Session,
    *,
    word: str,
    provider_entry: DictionarySearchResponse,
    context: DictionaryRequestContext,
) -> DictionarySearchResponse:
    enricher = DeepSeekDictionaryEnricher()
    if not enricher.enabled:
        return provider_entry

    if not await try_consume_deepseek_budget(context):
        return provider_entry

    try:
        enriched_entry, deepseek_payload = await enricher.enrich_with_payload(provider_entry)
    except DictionaryEnrichmentError:
        return provider_entry

    if deepseek_payload:
        save_deepseek_dictionary_response(db, word=word, payload=deepseek_payload)
    return enriched_entry


async def search_dictionary(
    word: str,
    context: DictionaryRequestContext,
    db: Session,
) -> DictionarySearchResponse:
    normalized = word.strip().lower()
    await enforce_dictionary_search_rate_limit(context)

    persisted = get_dictionary_cache_by_word(db, normalized)
    provider_entry = _load_provider_entry(persisted.provider_response if persisted else None)
    enriched_entry = _load_enriched_entry(
        provider_entry,
        persisted.deepseek_response if persisted else None,
    )

    if enriched_entry is not None:
        await set_cached_dictionary_entry(normalized, enriched_entry)
        await record_dictionary_search(normalized)
        return enriched_entry

    has_search_lock = await try_acquire_dictionary_search_lock(normalized)
    if not has_search_lock:
        cached = await _wait_for_cached_response(normalized)
        if cached is not None:
            await record_dictionary_search(normalized)
            return cached
        has_search_lock = await try_acquire_dictionary_search_lock(normalized)

    try:
        result = provider_entry

        if result is None:
            result = await _search_with_provider(normalized)
            save_provider_dictionary_response(
                db,
                word=normalized,
                provider=_get_provider_name(),
                response=result,
            )

        if has_search_lock and enriched_entry is None:
            result = await _try_enrich_and_persist(
                db,
                word=normalized,
                provider_entry=result,
                context=context,
            )

        await set_cached_dictionary_entry(normalized, result)
        await record_dictionary_search(normalized)
        return result
    finally:
        if has_search_lock:
            await release_dictionary_search_lock(normalized)


async def suggest_words(query: str) -> DictionarySuggestionResponse:
    base = query.strip().lower()
    if not base:
        return DictionarySuggestionResponse(query=query, suggestions=[])

    suggestions: list[str] = []
    seen = set()

    for candidate in await get_popular_dictionary_searches(limit=8):
        if candidate.startswith(base) and candidate not in seen:
            suggestions.append(candidate)
            seen.add(candidate)

    for candidate in SUGGESTION_SEED_WORDS:
        if candidate.startswith(base) and candidate not in seen:
            suggestions.append(candidate)
            seen.add(candidate)

    for candidate in [base, f"{base}ing", f"{base}ed", f"{base}ly"]:
        if candidate not in seen:
            suggestions.append(candidate)
            seen.add(candidate)

    return DictionarySuggestionResponse(query=query, suggestions=suggestions[:8])


def build_placeholder_response(word: str) -> DictionarySearchResponse:
    return DictionarySearchResponse(
        word=word,
        phonetic="",
        audio_url="",
        meanings=[
            MeaningItem(
                part_of_speech="noun",
                definitions=[DefinitionItem(en=f"Placeholder definition for {word}.")],
            )
        ],
        origin="",
        synonyms=[],
        antonyms=[],
        learning_tip="",
    )
