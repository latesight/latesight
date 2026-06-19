from __future__ import annotations

from collections import OrderedDict

import httpx

from app.schemas.dictionary import DefinitionItem, DictionarySearchResponse, MeaningItem


class DictionaryProviderError(Exception):
    """Base error for dictionary provider failures."""


class DictionaryWordNotFoundError(DictionaryProviderError):
    """Raised when a word does not exist in the provider."""


FALLBACK_ENTRIES = {
    "resilience": {
        "phonetic": "/rɪˈzɪliəns/",
        "meanings": [
            {
                "part_of_speech": "noun",
                "definitions": [
                    {
                        "en": "The ability to recover quickly from difficulty or change.",
                        "example": "Children often show remarkable resilience after setbacks.",
                    }
                ],
            }
        ],
        "learning_tip": "Focus on the idea of bouncing back after pressure, stress, or change.",
    },
    "serendipity": {
        "phonetic": "/ˌserənˈdɪpəti/",
        "meanings": [
            {
                "part_of_speech": "noun",
                "definitions": [
                    {
                        "en": "The occurrence of finding something good by chance.",
                        "example": "Meeting her future business partner was pure serendipity.",
                    }
                ],
            }
        ],
        "learning_tip": "Use it for happy accidents or unexpectedly valuable discoveries.",
    },
}


class FreeDictionaryProvider:
    base_url = "https://api.dictionaryapi.dev/api/v2/entries/en"

    async def search(self, word: str) -> DictionarySearchResponse:
        normalized = word.strip().lower()
        if not normalized:
            raise DictionaryWordNotFoundError("Word is required.")

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(f"{self.base_url}/{normalized}")
        except httpx.HTTPError as exc:
            fallback = self._build_fallback(normalized)
            if fallback is not None:
                return fallback
            raise DictionaryProviderError("Dictionary provider request failed.") from exc

        if response.status_code == 404:
            fallback = self._build_fallback(normalized)
            if fallback is not None:
                return fallback
            raise DictionaryWordNotFoundError(f'"{normalized}" was not found.')

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            fallback = self._build_fallback(normalized)
            if fallback is not None:
                return fallback
            raise DictionaryProviderError("Dictionary provider request failed.") from exc

        payload = response.json()
        if not isinstance(payload, list) or not payload:
            fallback = self._build_fallback(normalized)
            if fallback is not None:
                return fallback
            raise DictionaryProviderError("Dictionary provider returned an invalid payload.")

        return self._normalize_entry(normalized, payload)

    def _normalize_entry(self, default_word: str, payload: list[dict]) -> DictionarySearchResponse:
        first_entry = payload[0]
        word = first_entry.get("word") or default_word
        phonetic = self._select_phonetic(payload)
        audio_url = self._select_audio(payload)
        origin = self._select_origin(payload)

        meanings: list[MeaningItem] = []
        synonyms = OrderedDict()
        antonyms = OrderedDict()

        for entry in payload:
            for meaning in entry.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech") or "unknown"
                definitions: list[DefinitionItem] = []

                for definition in meaning.get("definitions", []):
                    definition_text = (definition.get("definition") or "").strip()
                    if not definition_text:
                        continue

                    example = (definition.get("example") or "").strip()
                    definitions.append(DefinitionItem(en=definition_text, zh="", example=example, example_zh=""))

                    for synonym in definition.get("synonyms", []):
                        if synonym:
                            synonyms[synonym] = None
                    for antonym in definition.get("antonyms", []):
                        if antonym:
                            antonyms[antonym] = None

                for synonym in meaning.get("synonyms", []):
                    if synonym:
                        synonyms[synonym] = None
                for antonym in meaning.get("antonyms", []):
                    if antonym:
                        antonyms[antonym] = None

                if definitions:
                    meanings.append(MeaningItem(part_of_speech=part_of_speech, definitions=definitions))

        if not meanings:
            fallback = self._build_fallback(default_word)
            if fallback is not None:
                return fallback
            raise DictionaryProviderError("Dictionary provider returned no definitions.")

        return DictionarySearchResponse(
            word=word,
            phonetic=phonetic,
            audio_url=audio_url,
            meanings=meanings,
            origin=origin,
            synonyms=list(synonyms.keys())[:12],
            antonyms=list(antonyms.keys())[:12],
            learning_tip=self._build_learning_tip(word, meanings),
        )

    def _select_phonetic(self, payload: list[dict]) -> str:
        for entry in payload:
            phonetic = (entry.get("phonetic") or "").strip()
            if phonetic:
                return phonetic
            for item in entry.get("phonetics", []):
                text = (item.get("text") or "").strip()
                if text:
                    return text
        return ""

    def _select_audio(self, payload: list[dict]) -> str:
        for entry in payload:
            for item in entry.get("phonetics", []):
                audio = (item.get("audio") or "").strip()
                if audio:
                    return audio
        return ""

    def _select_origin(self, payload: list[dict]) -> str:
        for entry in payload:
            origin = (entry.get("origin") or "").strip()
            if origin:
                return origin
        return ""

    def _build_learning_tip(self, word: str, meanings: list[MeaningItem]) -> str:
        first_meaning = meanings[0]
        first_definition = first_meaning.definitions[0].en
        return f'Start with the {first_meaning.part_of_speech} sense of "{word}": {first_definition}'

    def _build_fallback(self, word: str) -> DictionarySearchResponse | None:
        entry = FALLBACK_ENTRIES.get(word)
        if entry is None:
            return None

        meanings = [
            MeaningItem(
                part_of_speech=meaning["part_of_speech"],
                definitions=[
                    DefinitionItem(
                        en=definition["en"],
                        zh="",
                        example=definition.get("example", ""),
                        example_zh="",
                    )
                    for definition in meaning["definitions"]
                ],
            )
            for meaning in entry["meanings"]
        ]

        return DictionarySearchResponse(
            word=word,
            phonetic=entry.get("phonetic", ""),
            audio_url="",
            meanings=meanings,
            origin="",
            synonyms=[],
            antonyms=[],
            learning_tip=entry.get("learning_tip", ""),
        )
