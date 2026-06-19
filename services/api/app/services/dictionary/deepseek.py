from __future__ import annotations

import json

import httpx

from app.core.config import get_settings
from app.schemas.dictionary import DictionarySearchResponse


class DictionaryEnrichmentError(Exception):
    """Raised when the Chinese enrichment request fails."""


class DeepSeekDictionaryEnricher:
    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.deepseek_api_key.strip()
        self._base_url = settings.deepseek_base_url.rstrip("/")
        self._model = settings.deepseek_model

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    async def enrich(self, entry: DictionarySearchResponse) -> DictionarySearchResponse:
        if not self.enabled:
            return entry

        payload = await self._request_translation_payload(entry)
        return self._apply_translation_payload(entry, payload)

    async def enrich_with_payload(self, entry: DictionarySearchResponse) -> tuple[DictionarySearchResponse, dict]:
        if not self.enabled:
            return entry, {}

        payload = await self._request_translation_payload(entry)
        return self._apply_translation_payload(entry, payload), payload

    def apply_saved_payload(self, entry: DictionarySearchResponse, payload: dict) -> DictionarySearchResponse:
        return self._apply_translation_payload(entry, payload)

    async def _request_translation_payload(self, entry: DictionarySearchResponse) -> dict:
        compact_entry = {
            "word": entry.word,
            "meanings": [
                {
                    "part_of_speech": meaning.part_of_speech,
                    "definitions": [
                        {
                            "en": definition.en,
                            "example": definition.example,
                        }
                        for definition in meaning.definitions
                    ],
                }
                for meaning in entry.meanings
            ],
            "learning_tip_en": entry.learning_tip,
            "synonyms_en": entry.synonyms[:8],
            "antonyms_en": entry.antonyms[:8],
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an English-Chinese dictionary localization assistant. "
                    "Return valid JSON only. Keep translations concise, accurate, and beginner-friendly. "
                    "Do not include markdown fences or extra commentary."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "task": (
                            "Translate dictionary content into Simplified Chinese for Chinese users with weak English. "
                            "Preserve meaning distinctions. Return JSON with keys: meanings, learning_tip_zh, "
                            "synonyms_zh, antonyms_zh. meanings must align by index with the input meanings, and each "
                            "definition must align by index with the input definitions. Each definition object must "
                            "contain zh and example_zh."
                        ),
                        "entry": compact_entry,
                    },
                    ensure_ascii=False,
                ),
            },
        ]

        request_payload = {
            "model": self._model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=request_payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DictionaryEnrichmentError("DeepSeek enrichment request failed.") from exc

        try:
            content = response.json()["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise ValueError("DeepSeek returned a non-text response.")
            return json.loads(content)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise DictionaryEnrichmentError("DeepSeek enrichment response was invalid.") from exc

    def _apply_translation_payload(
        self, entry: DictionarySearchResponse, payload: dict
    ) -> DictionarySearchResponse:
        localized = entry.model_copy(deep=True)

        meanings_payload = payload.get("meanings")
        if isinstance(meanings_payload, list):
            for meaning, translated_meaning in zip(localized.meanings, meanings_payload):
                if not isinstance(translated_meaning, dict):
                    continue
                definitions_payload = translated_meaning.get("definitions")
                if not isinstance(definitions_payload, list):
                    continue

                for definition, translated_definition in zip(meaning.definitions, definitions_payload):
                    if not isinstance(translated_definition, dict):
                        continue
                    zh = translated_definition.get("zh")
                    example_zh = translated_definition.get("example_zh")
                    if isinstance(zh, str):
                        definition.zh = zh.strip()
                    if isinstance(example_zh, str):
                        definition.example_zh = example_zh.strip()

        learning_tip_zh = payload.get("learning_tip_zh")
        if isinstance(learning_tip_zh, str) and learning_tip_zh.strip():
            localized.learning_tip = learning_tip_zh.strip()

        synonyms_zh = payload.get("synonyms_zh")
        if isinstance(synonyms_zh, list):
            localized.synonyms = [item.strip() for item in synonyms_zh if isinstance(item, str) and item.strip()]

        antonyms_zh = payload.get("antonyms_zh")
        if isinstance(antonyms_zh, list):
            localized.antonyms = [item.strip() for item in antonyms_zh if isinstance(item, str) and item.strip()]

        return localized
