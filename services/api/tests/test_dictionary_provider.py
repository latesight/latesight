from app.services.dictionary.providers.free_dictionary import FreeDictionaryProvider


def test_normalize_dictionary_entry() -> None:
    provider = FreeDictionaryProvider()
    payload = [
        {
            "word": "resilience",
            "phonetic": "/rɪˈzɪliəns/",
            "phonetics": [{"text": "/rɪˈzɪliəns/", "audio": "https://audio.example/resilience.mp3"}],
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "The ability to recover quickly from difficulty.",
                            "example": "Resilience matters when conditions change.",
                            "synonyms": ["toughness"],
                            "antonyms": ["fragility"],
                        }
                    ],
                    "synonyms": ["adaptability"],
                    "antonyms": [],
                }
            ],
        }
    ]

    result = provider._normalize_entry("resilience", payload)

    assert result.word == "resilience"
    assert result.phonetic == "/rɪˈzɪliəns/"
    assert result.audio_url == "https://audio.example/resilience.mp3"
    assert result.meanings[0].part_of_speech == "noun"
    assert result.meanings[0].definitions[0].example == "Resilience matters when conditions change."
    assert result.meanings[0].definitions[0].example_zh == ""
    assert result.synonyms == ["toughness", "adaptability"]
    assert result.antonyms == ["fragility"]
