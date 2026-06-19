from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps.common import get_db
from app.schemas.dictionary import (
    DictionarySearchRequest,
    DictionarySearchResponse,
    DictionarySuggestionResponse,
)
from app.services.dictionary.guard import build_dictionary_request_context
from app.services.dictionary.service import search_dictionary, suggest_words

router = APIRouter()


@router.post("/search", response_model=DictionarySearchResponse)
async def search(
    request: Request,
    payload: DictionarySearchRequest,
    db: Session = Depends(get_db),
) -> DictionarySearchResponse:
    context = await build_dictionary_request_context(request)
    return await search_dictionary(payload.word, context, db)


@router.get("/suggestions", response_model=DictionarySuggestionResponse)
async def suggestions(q: str = Query(..., min_length=1, max_length=64)) -> DictionarySuggestionResponse:
    return await suggest_words(q)
