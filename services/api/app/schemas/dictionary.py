from pydantic import BaseModel, Field


class DictionarySearchRequest(BaseModel):
    word: str = Field(min_length=1, max_length=128)


class DefinitionItem(BaseModel):
    en: str
    zh: str = ""
    example: str = ""
    example_zh: str = ""


class MeaningItem(BaseModel):
    part_of_speech: str
    definitions: list[DefinitionItem]


class DictionarySearchResponse(BaseModel):
    word: str
    phonetic: str = ""
    audio_url: str = ""
    meanings: list[MeaningItem]
    origin: str = ""
    synonyms: list[str] = []
    antonyms: list[str] = []
    learning_tip: str = ""


class DictionarySuggestionResponse(BaseModel):
    query: str
    suggestions: list[str]
