import logfire
from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails

from app.config import settings
from app.guardrails.colang_rules import (
    COLANG_CONTENT,
    YAML_CONTENT,
    RAIL_INDICATORS,
)

_rails: LLMRails | None = None


def initialize_rails() -> None:
    """Initialize NeMo Guardrails once at application startup."""
    global _rails

    guard_llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0,
    )

    config = RailsConfig.from_content(
        colang_content=COLANG_CONTENT,
        yaml_content=YAML_CONTENT,
    )

    # Pass the LangChain LLM directly
    _rails = LLMRails(config=config, llm=guard_llm)

    logfire.info("🛡️ NeMo Guardrails initialized (llama-3.1-8b-instant)")


def guard(message: str) -> tuple[bool, str | None]:
    """
    Returns:
        (True, response)  - rail fired
        (False, None)     - safe, continue to RAG
    """

    if _rails is None:
        logfire.warning("⚠️ Guardrails not initialized")
        return False, None

    with logfire.span("🛡️ Guardrails Check"):
        result = _rails.generate(
            messages=[{"role": "user", "content": message}]
        )

        content = result.get("content", "") if isinstance(result, dict) else str(result)

        logfire.info(f"Guard response: {content}")

        fired = any(indicator in content for indicator in RAIL_INDICATORS)

        if fired:
            logfire.info(f"🛡️ Rail fired | query='{message[:80]}'")
            return True, content

        logfire.info("✅ Rails passed")
        return False, None