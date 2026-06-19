"use client";

import { FormEvent, useEffect, useRef, useState, useTransition } from "react";

type DictionaryDefinition = {
  en: string;
  zh: string;
  example: string;
  example_zh: string;
};

type DictionaryMeaning = {
  part_of_speech: string;
  definitions: DictionaryDefinition[];
};

type DictionaryResponse = {
  word: string;
  phonetic: string;
  audio_url: string;
  meanings: DictionaryMeaning[];
  origin: string;
  synonyms: string[];
  antonyms: string[];
  learning_tip: string;
};

type DictionarySuggestionResponse = {
  query: string;
  suggestions: string[];
};

const DEFAULT_WORD = "resilience";
const PART_OF_SPEECH_LABELS: Record<string, string> = {
  noun: "名词",
  verb: "动词",
  adjective: "形容词",
  adverb: "副词",
  pronoun: "代词",
  preposition: "介词",
  conjunction: "连词",
  interjection: "感叹词",
  article: "冠词",
  determiner: "限定词",
  auxiliary: "助动词",
  modal: "情态动词",
  phrase: "短语"
};

function getPartOfSpeechLabel(partOfSpeech: string) {
  return PART_OF_SPEECH_LABELS[partOfSpeech.trim().toLowerCase()] ?? partOfSpeech;
}

export function DictionarySearch() {
  const [word, setWord] = useState(DEFAULT_WORD);
  const [result, setResult] = useState<DictionaryResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [isPending, startTransition] = useTransition();
  const requestIdRef = useRef(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const normalized = word.trim().toLowerCase();

    if (normalized.length < 2) {
      setSuggestions([]);
      return;
    }

    requestIdRef.current += 1;
    const currentRequestId = requestIdRef.current;
    const controller = new AbortController();

    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch(
          `/api/v1/dictionary/suggestions?q=${encodeURIComponent(normalized)}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          return;
        }

        const payload = (await response.json()) as DictionarySuggestionResponse;
        if (requestIdRef.current === currentRequestId) {
          setSuggestions(payload.suggestions.filter((item) => item !== normalized));
        }
      } catch (suggestionError) {
        if (controller.signal.aborted) {
          return;
        }
        setSuggestions([]);
      }
    }, 180);

    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [word]);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, []);

  useEffect(() => {
    audioRef.current?.pause();
    audioRef.current = null;
    setIsPlayingAudio(false);
  }, [result?.audio_url]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalized = word.trim();
    if (!normalized) {
      setError("请输入要查询的单词。");
      setResult(null);
      return;
    }

    setError("");
    setShowSuggestions(false);

    startTransition(async () => {
      try {
        const response = await fetch("/api/v1/dictionary/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ word: normalized })
        });

        if (!response.ok) {
          const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
          throw new Error(payload?.detail || "查询失败，请稍后重试。");
        }

        const payload = (await response.json()) as DictionaryResponse;
        setResult(payload);
        setError("");
      } catch (submissionError) {
        const message =
          submissionError instanceof Error ? submissionError.message : "查询失败，请稍后重试。";
        setError(message);
        setResult(null);
      }
    });
  }

  function applySuggestion(nextWord: string) {
    setWord(nextWord);
    setShowSuggestions(false);
  }

  async function handlePronunciationPlay() {
    if (!result?.audio_url) {
      return;
    }

    try {
      let audio = audioRef.current;

      if (!audio || audio.src !== result.audio_url) {
        audio?.pause();
        audio = new Audio(result.audio_url);
        audio.onended = () => setIsPlayingAudio(false);
        audio.onerror = () => {
          setIsPlayingAudio(false);
          setError("发音播放失败，请稍后重试。");
        };
        audioRef.current = audio;
      } else {
        audio.pause();
        audio.currentTime = 0;
      }

      setError("");
      setIsPlayingAudio(true);
      await audio.play();
    } catch {
      setIsPlayingAudio(false);
      setError("发音播放失败，请稍后重试。");
    }
  }

  return (
    <div className="surface-panel dict-panel">
      <form onSubmit={handleSubmit}>
        <div className="search-stack">
          <div className="search-row">
            <input
              id="word"
              name="word"
              aria-label="输入要查询的单词"
              value={word}
              onChange={(event) => {
                setWord(event.target.value);
                setShowSuggestions(true);
              }}
              onFocus={() => setShowSuggestions(true)}
              placeholder="例如 resilience"
              autoComplete="off"
            />
            <button className="primary-button" type="submit" disabled={isPending}>
              {isPending ? "Searching..." : "Search"}
            </button>
          </div>
          {showSuggestions && suggestions.length ? (
            <div className="suggestion-panel" role="listbox" aria-label="Word suggestions">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="suggestion-item"
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => applySuggestion(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </form>

      <div className="query-hint">
        试试这些词：
        {" "}
        <button type="button" className="inline-chip" onClick={() => applySuggestion("resilience")}>
          resilience
        </button>
        <button type="button" className="inline-chip" onClick={() => applySuggestion("serendipity")}>
          serendipity
        </button>
        <button type="button" className="inline-chip" onClick={() => applySuggestion("clarity")}>
          clarity
        </button>
      </div>

      {error ? <p className="status-message status-message--error">{error}</p> : null}

      {result ? (
        <section className="result-panel" aria-live="polite">
          <div className="result-header">
            <div>
              <h2>{result.word}</h2>
            </div>
            <div className="result-meta">
              {result.phonetic ? <span>{result.phonetic}</span> : null}
              {result.audio_url ? (
                <button className="pronunciation-button" type="button" onClick={handlePronunciationPlay}>
                  {isPlayingAudio ? "播放中..." : "发音"}
                </button>
              ) : null}
            </div>
          </div>

          <div className="meaning-list">
            {result.meanings.map((meaning) => (
              <article className="meaning-card" key={`${meaning.part_of_speech}-${meaning.definitions[0]?.en}`}>
                <p className="meta-label">{getPartOfSpeechLabel(meaning.part_of_speech)}</p>
                {meaning.definitions.map((definition) => (
                  <div className="definition-block" key={definition.en}>
                    <p>{definition.zh || definition.en}</p>
                    {definition.zh ? <p className="definition-english">{definition.en}</p> : null}
                    {definition.example ? (
                      <p className="definition-example">
                        例句：{definition.example_zh || definition.example}
                      </p>
                    ) : null}
                    {definition.example && definition.example_zh ? (
                      <p className="definition-example definition-example--english">
                        Example: {definition.example}
                      </p>
                    ) : null}
                  </div>
                ))}
              </article>
            ))}
          </div>

          {result.learning_tip ? (
            <div className="support-grid">
              <article className="surface-panel support-card">
                <p className="meta-label">学习提示</p>
                <p>{result.learning_tip}</p>
              </article>
              <article className="surface-panel support-card">
                <p className="meta-label">近义词</p>
                <p>{result.synonyms.length ? result.synonyms.join(", ") : "暂无近义词数据。"}</p>
              </article>
              <article className="surface-panel support-card">
                <p className="meta-label">反义词</p>
                <p>{result.antonyms.length ? result.antonyms.join(", ") : "暂无反义词数据。"}</p>
              </article>
            </div>
          ) : null}
        </section>
      ) : (
        <div className="result-empty">
          <p className="meta-label">准备就绪</p>
          <p>输入单词并提交后，结果会出现在这里。</p>
        </div>
      )}
    </div>
  );
}
