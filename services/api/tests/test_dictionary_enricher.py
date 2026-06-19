from app.schemas.dictionary import DefinitionItem, DictionarySearchResponse, MeaningItem
from app.services.dictionary.deepseek import DeepSeekDictionaryEnricher


def test_apply_translation_payload_merges_chinese_fields() -> None:
    entry = DictionarySearchResponse(
        word="halo",
        phonetic="/ˈheɪləʊ/",
        audio_url="https://audio.example/halo.mp3",
        meanings=[
            MeaningItem(
                part_of_speech="noun",
                definitions=[
                    DefinitionItem(
                        en="A circular band of coloured light.",
                        zh="",
                        example="A halo appeared around the moon.",
                        example_zh="",
                    )
                ],
            )
        ],
        synonyms=["glory"],
        antonyms=["darkness"],
        learning_tip="Start with the noun sense of halo.",
    )
    payload = {
        "meanings": [
            {
                "definitions": [
                    {
                        "zh": "光环；光圈。",
                        "example_zh": "月亮周围出现了一圈光环。"
                    }
                ]
            }
        ],
        "learning_tip_zh": "先记住它最常见的意思：光环。",
        "synonyms_zh": ["光环", "荣耀"],
        "antonyms_zh": ["黑暗"],
    }

    result = DeepSeekDictionaryEnricher()._apply_translation_payload(entry, payload)

    assert result.meanings[0].definitions[0].zh == "光环；光圈。"
    assert result.meanings[0].definitions[0].example_zh == "月亮周围出现了一圈光环。"
    assert result.learning_tip == "先记住它最常见的意思：光环。"
    assert result.synonyms == ["光环", "荣耀"]
    assert result.antonyms == ["黑暗"]
