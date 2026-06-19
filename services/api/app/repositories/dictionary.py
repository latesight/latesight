from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dictionary_cache import DictionaryCache
from app.schemas.dictionary import DictionarySearchResponse


def get_dictionary_cache_by_word(db: Session, word: str) -> DictionaryCache | None:
    normalized = word.strip().lower()
    if not normalized:
        return None

    statement = select(DictionaryCache).where(DictionaryCache.word == normalized)
    return db.execute(statement).scalar_one_or_none()


def save_provider_dictionary_response(
    db: Session,
    *,
    word: str,
    provider: str,
    response: DictionarySearchResponse,
) -> DictionaryCache:
    normalized = word.strip().lower()
    record = get_dictionary_cache_by_word(db, normalized)
    if record is None:
        record = DictionaryCache(
            word=normalized,
            provider=provider,
            provider_response=response.model_dump(mode="json"),
            deepseek_response={},
        )
        db.add(record)
    else:
        record.provider = provider
        record.provider_response = response.model_dump(mode="json")
        record.deepseek_response = {}

    db.commit()
    db.refresh(record)
    return record


def save_deepseek_dictionary_response(
    db: Session,
    *,
    word: str,
    payload: dict,
) -> DictionaryCache:
    normalized = word.strip().lower()
    record = get_dictionary_cache_by_word(db, normalized)
    if record is None:
        raise ValueError(f'Dictionary cache for "{normalized}" must exist before saving DeepSeek data.')

    record.deepseek_response = payload
    db.commit()
    db.refresh(record)
    return record
