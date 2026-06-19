import asyncio
from types import SimpleNamespace

from app.services.dictionary import service
from app.services.dictionary.guard import DictionaryRequestContext
from app.schemas.dictionary import DefinitionItem, DictionarySearchResponse, MeaningItem


def test_suggest_words_prefers_prefix_matches() -> None:
    result = asyncio.run(service.suggest_words("res"))

    assert result.query == "res"
    assert "resilience" in result.suggestions
    assert result.suggestions[0].startswith("res")


def _build_provider_entry() -> DictionarySearchResponse:
    return DictionarySearchResponse(
        word="resilience",
        phonetic="/rɪˈzɪliəns/",
        audio_url="https://audio.example/resilience.mp3",
        meanings=[
            MeaningItem(
                part_of_speech="noun",
                definitions=[
                    DefinitionItem(
                        en="The ability to recover quickly from difficulty or change.",
                        zh="",
                        example="Children often show resilience after setbacks.",
                        example_zh="",
                    )
                ],
            )
        ],
        origin="",
        synonyms=["adaptability"],
        antonyms=["fragility"],
        learning_tip="Focus on bouncing back.",
    )


def test_search_dictionary_returns_persisted_enriched_result(monkeypatch) -> None:
    provider_entry = _build_provider_entry()
    record = SimpleNamespace(
        provider_response=provider_entry.model_dump(mode="json"),
        deepseek_response={"meanings": [{"definitions": [{"zh": "韧性", "example_zh": "孩子们很有韧性。"}]}]},
    )

    class FakeEnricher:
        def apply_saved_payload(self, entry, payload):
            localized = entry.model_copy(deep=True)
            localized.meanings[0].definitions[0].zh = payload["meanings"][0]["definitions"][0]["zh"]
            localized.meanings[0].definitions[0].example_zh = payload["meanings"][0]["definitions"][0]["example_zh"]
            return localized

    async def noop(*args, **kwargs):
        return None

    async def unexpected_provider(*args, **kwargs):
        raise AssertionError("Provider should not be called when both payloads are persisted")

    monkeypatch.setattr(service, "get_dictionary_cache_by_word", lambda db, word: record)
    monkeypatch.setattr(service, "DeepSeekDictionaryEnricher", FakeEnricher)
    monkeypatch.setattr(service, "set_cached_dictionary_entry", noop)
    monkeypatch.setattr(service, "record_dictionary_search", noop)
    monkeypatch.setattr(service, "enforce_dictionary_search_rate_limit", noop)
    monkeypatch.setattr(service, "try_acquire_dictionary_search_lock", noop)
    monkeypatch.setattr(service, "_search_with_provider", unexpected_provider)

    result = asyncio.run(
        service.search_dictionary(
            "resilience",
            DictionaryRequestContext(identity_key="ip:127.0.0.1", ip_address="127.0.0.1"),
            db=object(),
        )
    )

    assert result.meanings[0].definitions[0].zh == "韧性"


def test_search_dictionary_enriches_existing_provider_payload(monkeypatch) -> None:
    provider_entry = _build_provider_entry()
    record = SimpleNamespace(
        provider_response=provider_entry.model_dump(mode="json"),
        deepseek_response={},
    )
    saved_payloads: list[dict] = []

    class FakeEnricher:
        enabled = True

        async def enrich_with_payload(self, entry):
            localized = entry.model_copy(deep=True)
            localized.learning_tip = "先记住它表示恢复能力。"
            return localized, {"learning_tip_zh": "先记住它表示恢复能力。"}

    async def noop(*args, **kwargs):
        return None

    async def yes(*args, **kwargs):
        return True

    monkeypatch.setattr(service, "get_dictionary_cache_by_word", lambda db, word: record)
    monkeypatch.setattr(service, "save_deepseek_dictionary_response", lambda db, word, payload: saved_payloads.append(payload))
    monkeypatch.setattr(service, "DeepSeekDictionaryEnricher", FakeEnricher)
    monkeypatch.setattr(service, "set_cached_dictionary_entry", noop)
    monkeypatch.setattr(service, "record_dictionary_search", noop)
    monkeypatch.setattr(service, "enforce_dictionary_search_rate_limit", noop)
    monkeypatch.setattr(service, "try_acquire_dictionary_search_lock", yes)
    monkeypatch.setattr(service, "release_dictionary_search_lock", noop)
    monkeypatch.setattr(service, "try_consume_deepseek_budget", yes)

    result = asyncio.run(
        service.search_dictionary(
            "resilience",
            DictionaryRequestContext(identity_key="ip:127.0.0.1", ip_address="127.0.0.1"),
            db=object(),
        )
    )

    assert result.learning_tip == "先记住它表示恢复能力。"
    assert saved_payloads == [{"learning_tip_zh": "先记住它表示恢复能力。"}]


def test_search_dictionary_persists_provider_then_deepseek(monkeypatch) -> None:
    provider_entry = _build_provider_entry()
    provider_saves: list[str] = []
    deepseek_saves: list[dict] = []

    class FakeEnricher:
        enabled = True

        async def enrich_with_payload(self, entry):
            localized = entry.model_copy(deep=True)
            localized.synonyms = ["韧性"]
            return localized, {"synonyms_zh": ["韧性"]}

    async def noop(*args, **kwargs):
        return None

    async def yes(*args, **kwargs):
        return True

    async def provider(*args, **kwargs):
        return provider_entry

    monkeypatch.setattr(service, "get_dictionary_cache_by_word", lambda db, word: None)
    monkeypatch.setattr(service, "_search_with_provider", provider)
    monkeypatch.setattr(
        service,
        "save_provider_dictionary_response",
        lambda db, word, provider, response: provider_saves.append(word),
    )
    monkeypatch.setattr(service, "save_deepseek_dictionary_response", lambda db, word, payload: deepseek_saves.append(payload))
    monkeypatch.setattr(service, "DeepSeekDictionaryEnricher", FakeEnricher)
    monkeypatch.setattr(service, "set_cached_dictionary_entry", noop)
    monkeypatch.setattr(service, "record_dictionary_search", noop)
    monkeypatch.setattr(service, "enforce_dictionary_search_rate_limit", noop)
    monkeypatch.setattr(service, "try_acquire_dictionary_search_lock", yes)
    monkeypatch.setattr(service, "release_dictionary_search_lock", noop)
    monkeypatch.setattr(service, "try_consume_deepseek_budget", yes)

    result = asyncio.run(
        service.search_dictionary(
            "resilience",
            DictionaryRequestContext(identity_key="ip:127.0.0.1", ip_address="127.0.0.1"),
            db=object(),
        )
    )

    assert provider_saves == ["resilience"]
    assert deepseek_saves == [{"synonyms_zh": ["韧性"]}]
    assert result.synonyms == ["韧性"]
