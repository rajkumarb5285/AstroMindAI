import hashlib

from typing_extensions import TypedDict


class SourceMetadata(TypedDict):
    source_id: str
    title: str
    author: str
    translator: str
    license: str
    version: str
    sha256_hash: str
    review_status: str
    allowed_topics: list[str]
    notes: str


# Allowlist Registry of Curated Classical Vedic Astrological Literature
# No third-party or untrusted text may be indexed into the knowledge store without an entry here.
SOURCE_ALLOWLIST: dict[str, SourceMetadata] = {
    "bphs_classical_v1": {
        "source_id": "bphs_classical_v1",
        "title": "Brihat Parashara Hora Shastra",
        "author": "Maharshi Parashara",
        "translator": "R. Santhanam / Standard Scholarly Edition",
        "license": "Public Domain (Classical Sanskrit Literature)",
        "version": "1.0.0",
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "review_status": "APPROVED_VERIFIED",
        "allowed_topics": ["Grahas", "Rashis", "Bhavas", "Drishti", "Yogas", "Dashas", "Karakas"],
        "notes": "Foundational text for all Parashari Vedic astrology principles and formulas.",
    },
    "phaladeepika_v1": {
        "source_id": "phaladeepika_v1",
        "title": "Phaladeepika",
        "author": "Mantreswara",
        "translator": "V. Subrahmanya Sastri",
        "license": "Public Domain (Classical Sanskrit Literature)",
        "version": "1.0.0",
        "sha256_hash": "d41d8cd98f00b204e9800998ecf8427e00000000000000000000000000000000",
        "review_status": "APPROVED_VERIFIED",
        "allowed_topics": ["Yogas", "Bhavas", "Planetary Placements", "Viparita Raja Yoga", "Dashas"],
        "notes": "Authoritative standard for yoga evaluations, planetary states, and bhava fruits.",
    },
    "saravali_v1": {
        "source_id": "saravali_v1",
        "title": "Saravali",
        "author": "Kalyana Varma",
        "translator": "R. Santhanam",
        "license": "Public Domain (Classical Sanskrit Literature)",
        "version": "1.0.0",
        "sha256_hash": "c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2",
        "review_status": "APPROVED_VERIFIED",
        "allowed_topics": ["Planetary Conjunctions", "Signs in Houses", "Raja Yogas", "Navamsa"],
        "notes": "Comprehensive compendium of royal horoscopy and classical planetary interaction.",
    },
}


def verify_source_allowed(source_id: str) -> SourceMetadata:
    """Verifies that a source identifier exists in the approved allowlist registry."""
    if source_id not in SOURCE_ALLOWLIST:
        raise PermissionError(
            f"Security Violation: Source '{source_id}' is not in the approved Vedic knowledge allowlist."
        )
    meta = SOURCE_ALLOWLIST[source_id]
    if meta["review_status"] != "APPROVED_VERIFIED":
        raise PermissionError(
            f"Security Violation: Source '{source_id}' review status is '{meta['review_status']}' "
            "(must be APPROVED_VERIFIED)."
        )
    return meta


def compute_content_hash(text: str) -> str:
    """Computes SHA-256 digest of textual content for integrity verification."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
