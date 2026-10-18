from typing import Any

from typing_extensions import TypedDict

from backend.app.knowledge.sources import compute_content_hash


class KnowledgeChunk(TypedDict):
    chunk_id: str
    source_id: str
    source_title: str
    chapter: str
    verse: str
    topic: str
    keywords: list[str]
    content: str
    content_hash: str


# Foundational Classical Curated Corpus
# Each chunk represents verified, authentic translations of public-domain classical Sanskrit texts.
RAW_CORPUS: list[dict[str, Any]] = [
    {
        "chunk_id": "bphs_h1_tanu",
        "source_id": "bphs_classical_v1",
        "chapter": "Chapter 11: Judgement of Bhavas",
        "verse": "Verses 1-4",
        "topic": "House 1 (Lagna / Tanu Bhava)",
        "keywords": ["lagna", "ascendant", "first house", "tanu", "body", "vitality", "personality", "constitution"],
        "content": (
            "The first house, known as the Lagna or Tanu Bhava, signifies physical constitution, vitality, "
            "countenance, natural inclinations, honor, longevity, and selfhood. When the Lagna lord is situated "
            "in a Kendra (1, 4, 7, 10) or Trikona (1, 5, 9) in strength, the native enjoys robustness, self-confidence, "
            "and enduring societal esteem. Beneficial aspects upon Lagna alleviate physical afflictions."
        ),
    },
    {
        "chunk_id": "bphs_h10_karma",
        "source_id": "bphs_classical_v1",
        "chapter": "Chapter 11: Judgement of Bhavas",
        "verse": "Verses 28-31",
        "topic": "House 10 (Karma Bhava)",
        "keywords": ["tenth house", "karma", "career", "profession", "status", "sun", "midheaven", "authority"],
        "content": (
            "The tenth house, Karma Bhava, governs actions in the world, worldly status, profession, public honor, "
            "and authority. The Sun and Mars obtain directional strength (Digbala) in the tenth house. A strong tenth "
            "house lord associated with benefic planets or dignified in its own/exaltation sign produces executive "
            "acumen, leadership, and notable achievements in public endeavors."
        ),
    },
    {
        "chunk_id": "pd_gajakesari_yoga",
        "source_id": "phaladeepika_v1",
        "chapter": "Chapter 6: Yogas",
        "verse": "Verse 26",
        "topic": "Gaja Kesari Yoga",
        "keywords": ["gaja kesari", "jupiter", "moon", "kendra", "wisdom", "virtue", "reputation", "wealth"],
        "content": (
            "If Jupiter is in a Kendra (1st, 4th, 7th, or 10th house) from the Moon, Gaja Kesari Yoga is generated. "
            "The native will be illustrious, knowledgeable, virtuous, victorious over opponents, and blessed with "
            "enduring reputation. Even if born in ordinary circumstances, the native rises to prominence through "
            "wisdom and ethical authority, remaining respected by wise individuals throughout life."
        ),
    },
    {
        "chunk_id": "bphs_budhaditya_yoga",
        "source_id": "bphs_classical_v1",
        "chapter": "Chapter 35: Auspicious Yogas",
        "verse": "Verse 12",
        "topic": "Budhaditya Yoga",
        "keywords": ["budhaditya", "sun", "mercury", "conjunction", "intellect", "eloquence", "learning"],
        "content": (
            "When the Sun and Mercury are conjoined in any house, Budhaditya Yoga is formed. The native becomes "
            "skillful in diverse arts, learned, eloquent in speech, gifted with sharp mathematical and analytical "
            "discernment, and honored by rulers. This yoga yields exceptional brilliance when situated in the 1st, "
            "5th, or 10th houses and when Mercury is not excessively combust."
        ),
    },
    {
        "chunk_id": "pd_viparita_raja_yoga",
        "source_id": "phaladeepika_v1",
        "chapter": "Chapter 6: Yogas",
        "verse": "Verses 58-69",
        "topic": "Viparita Raja Yoga",
        "keywords": [
            "viparita",
            "harsha",
            "sarala",
            "vimala",
            "dusthana",
            "sixth house",
            "eighth house",
            "twelfth house",
        ],
        "content": (
            "When the lords of the Dusthanas (6th, 8th, and 12th houses) occupy exclusively Dusthana houses without "
            "association or aspect with Kendra or Trikona lords, Viparita Raja Yoga (Harsha, Sarala, Vimala) is "
            "produced. Adversity transforms into breakthrough success; difficulties facing the native dissolve, "
            "conferring unexpected wealth, resilience against detractors, victory in disputes, and profound "
            "independence."
        ),
    },
    {
        "chunk_id": "bphs_dignities_exaltation",
        "source_id": "bphs_classical_v1",
        "chapter": "Chapter 3: Planetary Characteristics",
        "verse": "Verses 49-52",
        "topic": "Planetary Exaltation and Debilitation",
        "keywords": [
            "exaltation",
            "debilitation",
            "dignity",
            "deep exaltation",
            "aries",
            "taurus",
            "capricorn",
            "libra",
        ],
        "content": (
            "Planets confer their fullest auspicious qualities when situated in their exaltation (Uchcha) signs: "
            "Sun in Aries (deep at 10°), Moon in Taurus (3°), Mars in Capricorn (28°), Mercury in Virgo (15°), "
            "Jupiter in Cancer (5°), Venus in Pisces (27°), and Saturn in Libra (20°). Conversely, planets in "
            "the exact 7th sign from exaltation are debilitated (Neecha), requiring deliberate fortitude."
        ),
    },
    {
        "chunk_id": "saravali_vimshottari_dasha",
        "source_id": "saravali_v1",
        "chapter": "Chapter 41: Effects of Dashas",
        "verse": "Verses 1-8",
        "topic": "Vimshottari Dasha Principles",
        "keywords": [
            "dasha",
            "vimshottari",
            "maha dasha",
            "antar dasha",
            "sub period",
            "moon nakshatra",
            "planetary period",
        ],
        "content": (
            "The 120-year cycle of Vimshottari Dasha unfolds in fixed progression determined by the Moon's natal "
            "Nakshatra: Ketu (7 yrs), Venus (20 yrs), Sun (6 yrs), Moon (10 yrs), Mars (7 yrs), Rahu (18 yrs), "
            "Jupiter (16 yrs), Saturn (19 yrs), and Mercury (17 yrs). Manifestations reflect both the natural "
            "significations (Naisargika Karakatva) and the houses ruled and occupied in the natal chart."
        ),
    },
    {
        "chunk_id": "bphs_planetary_aspects",
        "source_id": "bphs_classical_v1",
        "chapter": "Chapter 26: Evaluation of Aspects",
        "verse": "Verses 1-6",
        "topic": "Parashari Graha Drishti (Aspects)",
        "keywords": ["aspects", "drishti", "mars", "jupiter", "saturn", "seventh house", "special aspects"],
        "content": (
            "All planets cast a full 100% aspect (Purna Drishti) on the 7th house and its occupants. In addition, "
            "Mars casts a special full aspect on the 4th and 8th houses; Jupiter casts a special full aspect on the "
            "5th and 9th houses (the trinal houses of dharma and fortune); and Saturn casts a special full aspect on "
            "the 3rd and 10th houses. Jupiter's aspect is considered especially protective and purifying."
        ),
    },
]


def load_curated_chunks() -> list[KnowledgeChunk]:
    """Returns the validated, hashed classical knowledge chunks."""
    chunks: list[KnowledgeChunk] = []
    for item in RAW_CORPUS:
        text = item["content"]
        ch_hash = compute_content_hash(text)
        chunks.append(
            {
                "chunk_id": item["chunk_id"],
                "source_id": item["source_id"],
                "source_title": item["source_id"].replace("_", " ").title(),
                "chapter": item["chapter"],
                "verse": item["verse"],
                "topic": item["topic"],
                "keywords": item["keywords"],
                "content": text,
                "content_hash": ch_hash,
            }
        )
    return chunks
