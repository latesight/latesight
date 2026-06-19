from fastapi import HTTPException, status

from app.schemas.dictionary import (
    DefinitionItem,
    DictionarySearchResponse,
    DictionarySuggestionResponse,
    MeaningItem,
)
from app.services.dictionary.cache import (
    get_cached_dictionary_entry,
    get_popular_dictionary_searches,
    record_dictionary_search,
    set_cached_dictionary_entry,
)
from app.services.dictionary.deepseek import DeepSeekDictionaryEnricher, DictionaryEnrichmentError
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


async def search_dictionary(word: str) -> DictionarySearchResponse:
    normalized = word.strip().lower()
    cached = await get_cached_dictionary_entry(normalized)
    if cached is not None:
        await record_dictionary_search(normalized)
        return cached

    provider = FreeDictionaryProvider()
    try:
        result = await provider.search(normalized)
    except DictionaryWordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DictionaryProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Dictionary provider is temporarily unavailable.",
        ) from exc

    try:
        result = await DeepSeekDictionaryEnricher().enrich(result)
    except DictionaryEnrichmentError:
        pass

    await set_cached_dictionary_entry(normalized, result)
    await record_dictionary_search(normalized)
    return result


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
