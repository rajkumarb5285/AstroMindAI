import re

from typing_extensions import TypedDict

from backend.app.knowledge.corpus import KnowledgeChunk, load_curated_chunks
from backend.app.knowledge.sources import SOURCE_ALLOWLIST, compute_content_hash, verify_source_allowed


class SearchResult(TypedDict):
    chunk_id: str
    source_id: str
    source_title: str
    chapter: str
    verse: str
    topic: str
    content: str
    score: float
    citation_label: str


# Security: Prohibited content patterns in knowledge ingestion
DANGEROUS_INGESTION_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"eval\(",
    r"base64,",
    r"document\.cookie",
    r"system\.prompt",
    r"ignore previous instructions",
    r"bypass security",
    r"you are now in developer mode",
]


class KnowledgeStore:
    """
    Curated, Access-Controlled Vedic Knowledge Retrieval Store.
    Implements source allowlisting, content integrity checking, and keyword/BM25 retrieval.
    """

    MAX_RETRIEVAL_CHUNKS = 5
    MAX_DOCUMENT_BYTES = 1048576  # 1MB limit

    def __init__(self):
        self._chunks: dict[str, KnowledgeChunk] = {}
        self._initialize_curated_corpus()

    def _initialize_curated_corpus(self):
        """Loads and verifies curated classical texts into the memory store."""
        raw_chunks = load_curated_chunks()
        for chunk in raw_chunks:
            # 1. Verify source allowlist
            verify_source_allowed(chunk["source_id"])

            # 2. Verify content integrity hash
            actual_hash = compute_content_hash(chunk["content"])
            if actual_hash != chunk["content_hash"]:
                raise ValueError(
                    f"Integrity check failed for chunk {chunk['chunk_id']}: "
                    f"expected {chunk['content_hash']}, got {actual_hash}"
                )

            self._chunks[chunk["chunk_id"]] = chunk

    @classmethod
    def validate_document_for_ingestion(cls, content: str, source_id: str) -> None:
        """
        Validates untrusted input before considering it for knowledge ingestion:
        - Max size limit
        - Anti-injection pattern scanning
        - Source allowlist confirmation
        """
        # 1. Size limit
        if len(content.encode("utf-8")) > cls.MAX_DOCUMENT_BYTES:
            raise ValueError(f"Document exceeds maximum permitted size of {cls.MAX_DOCUMENT_BYTES} bytes.")

        # 2. Allowlist verification
        verify_source_allowed(source_id)

        # 3. Injection / Active script detection
        content_lower = content.lower()
        for pattern in DANGEROUS_INGESTION_PATTERNS:
            if re.search(pattern, content_lower):
                raise PermissionError(
                    f"Security Rejection: Malicious/active payload pattern '{pattern}' detected in document."
                )

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """
        Performs bounded keyword/semantic relevance search over the curated corpus.
        Filters strictly by approved sources.
        """
        bounded_k = min(max(1, top_k), self.MAX_RETRIEVAL_CHUNKS)
        query_tokens = [tok.lower() for tok in re.findall(r"\b\w{3,}\b", query)]

        scored_results: list[tuple[float, KnowledgeChunk]] = []

        for chunk in self._chunks.values():
            score = 0.0
            content_lower = chunk["content"].lower()
            topic_lower = chunk["topic"].lower()
            keywords_lower = [k.lower() for k in chunk["keywords"]]

            for token in query_tokens:
                # Topic match has highest weight
                if token in topic_lower:
                    score += 5.0
                # Keyword match
                if any(token in kw for kw in keywords_lower):
                    score += 3.0
                # Content frequency match
                count = content_lower.count(token)
                if count > 0:
                    score += min(count * 1.0, 4.0)

            if score > 0:
                scored_results.append((score, chunk))

        # Sort by relevance score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)

        results: list[SearchResult] = []
        for score, ch in scored_results[:bounded_k]:
            meta = SOURCE_ALLOWLIST.get(ch["source_id"])
            src_name = meta.get("title", ch["source_title"]) if meta else ch["source_title"]
            citation = f"{src_name}, {ch['chapter']}, {ch['verse']}"

            results.append(
                {
                    "chunk_id": ch["chunk_id"],
                    "source_id": ch["source_id"],
                    "source_title": src_name,
                    "chapter": ch["chapter"],
                    "verse": ch["verse"],
                    "topic": ch["topic"],
                    "content": ch["content"],
                    "score": round(score, 2),
                    "citation_label": citation,
                }
            )

        return results

    def get_chunk_by_id(self, chunk_id: str) -> KnowledgeChunk | None:
        """Retrieves an individual chunk by ID."""
        return self._chunks.get(chunk_id)

    @property
    def total_chunks_count(self) -> int:
        return len(self._chunks)


# Global singleton instance for knowledge store
global_knowledge_store = KnowledgeStore()
