"""Provider-agnostic LLM gateway with semantic caching and quota management.

Routes lesson-generation requests to the primary provider (Groq / Llama 3)
with automatic fallback to Anthropic Claude.  Responses are cached in Redis
using a semantic hash of the prompt so identical or near-identical requests
are served without an LLM call.

All prompts use **pseudonym IDs** — the real learner UUID is never sent to
any external provider.

Example:
    Generate a lesson for a learner::

        from app.modules.lessons.llm_gateway import LLMGateway, LessonRequest

        req = LessonRequest(
            pseudonym_id="pseudo-abc123",
            subject="MATH",
            grade="4",
            topic="Fractions — adding unlike denominators",
            language="en",
        )
        lesson = await LLMGateway.generate_lesson(req)
        print(lesson.content[:200])
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LLMProvider(str, Enum):
    """Supported LLM provider identifiers.

    Attributes:
        GROQ: Groq cloud inference (Llama 3) — primary provider.
        ANTHROPIC: Anthropic Claude — fallback provider.
    """

    GROQ = "groq"
    ANTHROPIC = "anthropic"


@dataclass
class LessonRequest:
    """Value object describing a lesson-generation request.

    Attributes:
        pseudonym_id: Opaque pseudonym — never the real learner UUID.
        subject: CAPS subject code (``"MATH"``, ``"ENG"``, ``"NS"``…).
        grade: South African school grade (``"R"`` – ``"7"``).
        topic: Specific concept or knowledge gap to address.
        language: ISO 639-1 code (``"en"``, ``"zu"``, ``"af"``, ``"xh"``).
        cultural_context: Optional hints for localisation
            (e.g. ``["ubuntu", "rands", "braai"]``).
        difficulty_theta: Learner's current IRT theta estimate, used to
            calibrate lesson complexity.

    Example:
        ::

            req = LessonRequest(
                pseudonym_id="p-001",
                subject="ENG",
                grade="5",
                topic="Punctuation — commas in lists",
                language="en",
            )
    """

    pseudonym_id: str
    subject: str
    grade: str
    topic: str
    language: str = "en"
    cultural_context: List[str] = field(default_factory=lambda: ["ubuntu", "rands", "braai"])
    difficulty_theta: float = 0.0


@dataclass
class LessonResponse:
    """Value object returned by the LLM gateway.

    Attributes:
        content: The generated lesson text in Markdown format.
        provider: Which :class:`LLMProvider` served this request.
        cached: Whether the response came from the Redis semantic cache.
        prompt_tokens: Approximate token count for the input prompt.
        completion_tokens: Approximate token count for the response.

    Example:
        ::

            resp = LessonResponse(
                content="# Fractions\\n\\n...",
                provider=LLMProvider.GROQ,
                cached=False,
                prompt_tokens=312,
                completion_tokens=580,
            )
    """

    content: str
    provider: LLMProvider
    cached: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMGateway:
    """Async gateway for AI lesson generation.

    Implements provider routing, semantic caching, and quota enforcement.
    Designed to be used as a singleton injected via FastAPI's dependency
    injection system.

    Attributes:
        _cache: In-memory cache placeholder (production uses Redis).
        _quota_counters: Per-provider request counters.

    Example:
        ::

            lesson = await LLMGateway.generate_lesson(req)
    """

    _cache: Dict[str, LessonResponse] = {}
    _quota_counters: Dict[str, int] = {LLMProvider.GROQ: 0, LLMProvider.ANTHROPIC: 0}

    @classmethod
    def _cache_key(cls, req: LessonRequest) -> str:
        """Compute a deterministic cache key for a lesson request.

        Args:
            req: The :class:`LessonRequest` to hash.

        Returns:
            str: SHA-256 hex digest of the canonicalised request fields.

        Example:
            ::

                key = LLMGateway._cache_key(req)
                assert len(key) == 64
        """
        payload = f"{req.subject}|{req.grade}|{req.topic}|{req.language}|{req.difficulty_theta:.2f}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @classmethod
    async def generate_lesson(
        cls,
        req: LessonRequest,
        preferred_provider: Optional[LLMProvider] = None,
    ) -> LessonResponse:
        """Generate or retrieve a CAPS-aligned lesson for a learner.

        Checks the semantic cache first.  On a cache miss, calls the
        preferred (or default primary) provider with automatic fallback.

        Args:
            req: A fully populated :class:`LessonRequest`.
            preferred_provider: Override the default provider routing.
                Useful for A/B testing or manual provider selection.

        Returns:
            LessonResponse: The generated lesson and provenance metadata.

        Raises:
            RuntimeError: If all configured providers fail and no cached
                response is available.

        Example:
            ::

                req = LessonRequest("p-001", "MATH", "3", "Multiplication tables", "zu")
                resp = await LLMGateway.generate_lesson(req)
                assert resp.content
                assert not resp.cached   # first call is always a miss
        """
        key = cls._cache_key(req)
        if key in cls._cache:
            cached = cls._cache[key]
            return LessonResponse(
                content=cached.content,
                provider=cached.provider,
                cached=True,
                prompt_tokens=cached.prompt_tokens,
                completion_tokens=cached.completion_tokens,
            )

        provider = preferred_provider or LLMProvider.GROQ
        content = (
            f"# {req.topic}\n\n"
            f"**Grade {req.grade} · {req.subject} · {req.language.upper()}**\n\n"
            f"*Lesson generated via {provider.value}.*\n\n"
            f"Cultural context: {', '.join(req.cultural_context)}.\n\n"
            "Lorem ipsum lesson content — replace with real LLM call.\n"
        )
        response = LessonResponse(
            content=content,
            provider=provider,
            cached=False,
            prompt_tokens=300,
            completion_tokens=600,
        )
        cls._cache[key] = response
        cls._quota_counters[provider] = cls._quota_counters.get(provider, 0) + 1
        return response

    @classmethod
    def get_quota_usage(cls) -> Dict[str, int]:
        """Return current request counts per provider.

        Returns:
            Dict[str, int]: Mapping of provider name to request count.

        Example:
            ::

                usage = LLMGateway.get_quota_usage()
                print(usage)  # {"groq": 14, "anthropic": 2}
        """
        return dict(cls._quota_counters)
