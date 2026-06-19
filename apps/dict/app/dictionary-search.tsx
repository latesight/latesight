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

const DEFAULT_WORD = "sight";

const DEFAULT_RESULT: DictionaryResponse = {
  word: "sight",
  phonetic: "/saɪt/",
  audio_url: "https://api.dictionaryapi.dev/media/pronunciations/en/sight-us.mp3",
  meanings: [
    {
      part_of_speech: "noun",
      definitions: [
        {
          en: "(in the singular) The ability to see.",
          zh: "视力",
          example: "He is losing his sight and now can barely read.",
          example_zh: "他正在失去视力，现在几乎无法阅读。"
        },
        {
          en: "The act of seeing; perception of objects by the eye; view.",
          zh: "看见；视觉；景象",
          example: "to gain sight of land",
          example_zh: "看见陆地"
        },
        {
          en: "Something seen.",
          zh: "所见之物；景象",
          example: "",
          example_zh: ""
        },
        {
          en: "Something worth seeing; a spectacle, either good or bad.",
          zh: "值得一看的东西；景象，无论好坏",
          example:
            "We went to London and saw all the sights – Buckingham Palace, Tower Bridge, and so on.",
          example_zh: "我们去了伦敦，参观了所有景点——白金汉宫、塔桥等等。"
        },
        {
          en: "A device used in aiming a projectile, through which the person aiming looks at the intended target.",
          zh: "瞄准器；瞄准镜",
          example: "",
          example_zh: ""
        },
        {
          en: "A small aperture through which objects are to be seen, and by which their direction is settled or ascertained.",
          zh: "观测孔；准星",
          example: "the sight of a quadrant",
          example_zh: "象限仪的观测孔"
        },
        {
          en: "A great deal, a lot; frequently used to intensify a comparative.",
          zh: "大量，许多（常用于加强比较级）",
          example: "This is a darn sight better than what I'm used to at home!",
          example_zh: "这比我家里常用的好得多！"
        },
        {
          en: "In a drawing, picture, etc., that part of the surface, as of paper or canvas, which is within the frame or the border or margin. In a frame, the open space, the opening.",
          zh: "（绘画等的）画面内区域；边框内的空白",
          example: "",
          example_zh: ""
        },
        {
          en: "The instrument of seeing; the eye.",
          zh: "视觉器官；眼睛",
          example: "",
          example_zh: ""
        },
        {
          en: "Mental view; opinion; judgment.",
          zh: "看法；观点；判断",
          example: "In their sight it was harmless.",
          example_zh: "在他们看来，这并无害处。"
        }
      ]
    },
    {
      part_of_speech: "verb",
      definitions: [
        {
          en: "To register visually.",
          zh: "看到；观察到",
          example: "",
          example_zh: ""
        },
        {
          en: "To get sight of (something).",
          zh: "看见；发现",
          example: "to sight land from a ship",
          example_zh: "从船上看见陆地"
        },
        {
          en: "To apply sights to; to adjust the sights of; also, to give the proper elevation and direction to by means of a sight.",
          zh: "安装瞄准器；调整瞄准器；用瞄准器对准",
          example: "to sight a rifle or a cannon",
          example_zh: "给步枪或大炮安装瞄准器"
        },
        {
          en: "To take aim at.",
          zh: "瞄准",
          example: "",
          example_zh: ""
        }
      ]
    }
  ],
  origin: "",
  synonyms: [
    "视觉 (vision)",
    "视力 (eyesight)",
    "视野 (field of view)",
    "瞥见 (glimpse)",
    "一瞥 (glance)",
    "发现 (discovery)",
    "景象 (spectacle)",
    "看见 (seeing)"
  ],
  antonyms: ["失明 (blindness)", "忽视 (ignore)", "忽略 (overlook)"],
  learning_tip: `从名词"视力 (eyesight)"的含义开始学习。名词 sight 最常见的用法指"视觉能力"，而动词则表示"看到、发现"。注意与同音词 cite（引用）和 site（地点）区分。`
};

const PART_OF_SPEECH_LABELS: Record<string, string> = {
  noun: "Noun",
  verb: "Verb",
  adjective: "Adjective",
  adverb: "Adverb",
  pronoun: "Pronoun",
  preposition: "Preposition",
  conjunction: "Conjunction",
  interjection: "Interjection",
  article: "Article",
  determiner: "Determiner",
  auxiliary: "Auxiliary",
  modal: "Modal",
  phrase: "Phrase"
};

function getPartOfSpeechLabel(partOfSpeech: string) {
  return PART_OF_SPEECH_LABELS[partOfSpeech.trim().toLowerCase()] ?? partOfSpeech;
}

export function DictionarySearch() {
  const [word, setWord] = useState(DEFAULT_WORD);
  const [result, setResult] = useState<DictionaryResponse | null>(DEFAULT_RESULT);
  const [error, setError] = useState<string>("");
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [isPending, startTransition] = useTransition();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const hasInteractedRef = useRef(false);

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

  function handleInputFocus() {
    if (!hasInteractedRef.current) {
      hasInteractedRef.current = true;
      setWord("");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalized = word.trim();
    if (!normalized) {
      setError("请输入要查询的单词。");
      return;
    }

    setError("");

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
              onChange={(event) => setWord(event.target.value)}
              onFocus={handleInputFocus}
              placeholder="例如 resilience"
              autoComplete="off"
            />
            <button className="primary-button" type="submit" disabled={isPending}>
              {isPending ? "Searching..." : "Search"}
            </button>
          </div>
        </div>
      </form>

      {error ? <p className="status-message status-message--error">{error}</p> : null}

      {result ? (
        <section className="result-panel" aria-live="polite">
          <div className="result-header">
            <div>
              <h2>{result.word}</h2>
            </div>
            <div className="result-meta">
              {result.phonetic ? (
                result.audio_url ? (
                  <button
                    className={`pronunciation-button${isPlayingAudio ? " pronunciation-button--playing" : ""}`}
                    type="button"
                    onClick={handlePronunciationPlay}
                    aria-label={isPlayingAudio ? `正在播放 ${result.word} 发音` : `播放 ${result.word} 发音`}
                  >
                    <span>{result.phonetic}</span>
                    {isPlayingAudio ? <span className="pronunciation-button__indicator" aria-hidden="true" /> : null}
                  </button>
                ) : (
                  <span>{result.phonetic}</span>
                )
              ) : null}
            </div>
          </div>

          <div className="meaning-list">
            {result.meanings.map((meaning) => (
              <article className="meaning-card" key={`${meaning.part_of_speech}-${meaning.definitions[0]?.en}`}>
                <p className="meta-label">{getPartOfSpeechLabel(meaning.part_of_speech)}</p>
                {meaning.definitions.map((definition) => (
                  <div className="definition-block" key={definition.en}>
                    <p>{definition.en}</p>
                    {definition.zh ? <p className="definition-chinese">{definition.zh}</p> : null}
                    {definition.example ? (
                      <p className="definition-example">
                        Example: {definition.example_zh || definition.example}
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
                <p className="meta-label">Learning Tip</p>
                <p>{result.learning_tip}</p>
              </article>
              <article className="surface-panel support-card">
                <p className="meta-label">Synonyms</p>
                <p>{result.synonyms.length ? result.synonyms.join(", ") : "No synonym data available."}</p>
              </article>
              <article className="surface-panel support-card">
                <p className="meta-label">Antonyms</p>
                <p>{result.antonyms.length ? result.antonyms.join(", ") : "No antonym data available."}</p>
              </article>
            </div>
          ) : null}
        </section>
      ) : (
        <div className="result-empty">
          <p className="meta-label">Ready</p>
          <p>Enter a word and submit. Results will appear here.</p>
        </div>
      )}
    </div>
  );
}
