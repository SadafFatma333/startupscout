from __future__ import annotations

import json
from typing import List, Optional
from utils.env_loader import load_environment
from utils.logger import setup_logger

# Ensure .env loaded before clients initialize
project_root = load_environment()
logger = setup_logger("startupscout.llm_client")

try:
    from openai import OpenAI  # requires OPENAI_API_KEY
    _openai_client: Optional[OpenAI] = OpenAI()
except Exception as e:
    logger.info(f"OpenAI client not initialized: {e}")
    _openai_client = None

try:
    from ollama import Client as OllamaClient  # requires local Ollama
    _ollama_client: Optional[OllamaClient] = OllamaClient()
except Exception as e:
    logger.info(f"Ollama client not initialized: {e}")
    _ollama_client = None


# ------------------------------------------------------------
# Providers
# ------------------------------------------------------------
def _call_openai(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.3) -> str:
    if _openai_client is None:
        raise RuntimeError("OpenAI client unavailable. Ensure OPENAI_API_KEY is set and openai installed.")
    resp = _openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def _call_ollama(prompt: str, model: str = "llama3:8b", temperature: float = 0.3) -> str:
    if _ollama_client is None:
        raise RuntimeError("Ollama client unavailable. Ensure ollama is installed and model pulled.")
    resp = _ollama_client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature},
    )
    return resp.get("message", {}).get("content", "")


def call_llm(
    prompt: str,
    provider_priority: List[str] = ("openai", "local"),
    openai_model: str = "gpt-4o-mini",
    local_model: str = "llama3:8b",
    temperature: float = 0.3,
) -> str:
    """Attempt providers in order, fallback gracefully."""
    last_err = None
    for provider in provider_priority:
        try:
            if provider == "openai":
                return _call_openai(prompt, model=openai_model, temperature=temperature)
            if provider == "local":
                return _call_ollama(prompt, model=local_model, temperature=temperature)
            raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            last_err = e
            logger.warning(f"Provider {provider} failed: {e}")
    raise RuntimeError(f"All LLM providers failed. Last error: {last_err}")


def extract_json_or_empty(text: str) -> dict:
    """
    Extracts JSON safely from model output.
    Removes code fences and extra text. Returns {} on failure.
    """
    if not text:
        return {}

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        first_brace = cleaned.find("{")
        if first_brace != -1:
            cleaned = cleaned[first_brace:]
        cleaned = cleaned.strip()

    if "{" in cleaned and "}" in cleaned:
        start, end = cleaned.find("{"), cleaned.rfind("}") + 1
        candidate = cleaned[start:end]
    else:
        candidate = cleaned

    try:
        return json.loads(candidate)
    except Exception:
        return {}
