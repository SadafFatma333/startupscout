# utils/observability/langfuse.py
from __future__ import annotations
import os
import time
import traceback
from contextlib import contextmanager
from typing import Any, Dict, Optional
from config.settings import (
    LANGFUSE_ENABLED, LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_SAMPLING_RATE
)

_langfuse = None
def _client():
    global _langfuse
    if not LANGFUSE_ENABLED:
        return None
    if not (LANGFUSE_HOST and LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY):
        return None
    if _langfuse is None:
        try:
            from langfuse import Langfuse
            _langfuse = Langfuse(
                host=LANGFUSE_HOST,
                public_key=LANGFUSE_PUBLIC_KEY,
                secret_key=LANGFUSE_SECRET_KEY,
                # SDK-level sampling if supported; otherwise we'll sample in code
            )
        except Exception:
            _langfuse = None
    return _langfuse

def _sampled() -> bool:
    import random
    try:
        return random.random() < float(LANGFUSE_SAMPLING_RATE)
    except Exception:
        return False

def _truncate(s: Optional[str], limit: int = 2000) -> Optional[str]:
    if s is None:
        return None
    return s if len(s) <= limit else s[:limit] + "…[truncated]"

def _redact(s: Optional[str]) -> Optional[str]:
    # Minimal redaction; extend if needed
    return s

@contextmanager
def lf_trace(name: str, user_id: Optional[str] = None, session_id: Optional[str] = None,
             input_text: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
             request_id: Optional[str] = None):
    """Context manager that yields (trace, enabled: bool). No-ops if disabled or not sampled."""
    client = _client()
    enabled = bool(client) and _sampled()
    trace = None
    start = time.time()
    try:
        if enabled:
            # Use the new LangFuse API - start_as_current_span for the main trace
            trace = client.start_as_current_span(
                name=name,
                input=_truncate(_redact(input_text)),
                metadata={
                    **(metadata or {}),
                    "user_id": user_id,
                    "session_id": session_id,
                    "request_id": request_id
                }
            )
        yield trace, enabled
    except Exception as e:
        if trace is not None:
            try:
                client.update_current_trace(level="ERROR", metadata={"exception": repr(e), "stack": traceback.format_exc()})
            except Exception:
                pass
        raise
    finally:
        if enabled and trace is not None:
            try:
                client.update_current_trace(output=None, metadata={"duration_ms": int((time.time() - start) * 1000)})
            except Exception:
                pass

@contextmanager
def lf_span(trace, name: str, metadata: Optional[Dict[str, Any]] = None):
    """Nested span helper; safe if trace is None."""
    if trace is None:
        yield None
        return
    client = _client()
    if client is None:
        yield None
        return
    span = None
    try:
        # Use the new LangFuse API for nested spans
        span = client.start_as_current_span(name=name, metadata=metadata or {})
        yield span
    except Exception as e:
        try:
            if span is not None:
                client.update_current_span(level="ERROR", metadata={"exception": repr(e), "stack": traceback.format_exc()})
        except Exception:
            pass
        raise
    finally:
        try:
            if span is not None:
                # LangFuse automatically ends spans when exiting the context
                pass
        except Exception:
            pass

def lf_log_event(trace, name: str, data: Dict[str, Any]):
    """Attach small custom events; safe if trace is None."""
    if trace is None:
        return
    client = _client()
    if client is None:
        return
    try:
        client.create_event(name=name, metadata=data)
    except Exception:
        pass

def lf_log_llm_usage(trace, model: str, prompt_tokens: int, completion_tokens: int, 
                    total_tokens: int, duration_ms: int, cost_usd: float = None):
    """Log detailed LLM usage metrics including cost calculation."""
    if trace is None:
        return
    client = _client()
    if client is None:
        return
    
    # Calculate cost if not provided (rough estimates for common models)
    if cost_usd is None:
        cost_usd = _calculate_model_cost(model, prompt_tokens, completion_tokens)
    
    try:
        # Calculate metrics
        tokens_per_second = round(total_tokens / (duration_ms / 1000), 2) if duration_ms > 0 else 0
        cost_per_1k_tokens = round(cost_usd / (total_tokens / 1000), 6) if total_tokens > 0 else 0
        
        # Create scores for metrics visualization (these will show up in graphs)
        try:
            client.create_score(
                name="cost_usd",
                value=round(cost_usd, 6),
                trace_id=client.get_current_trace_id()
            )
        except Exception:
            pass
            
        try:
            client.create_score(
                name="tokens_per_second", 
                value=tokens_per_second,
                trace_id=client.get_current_trace_id()
            )
        except Exception:
            pass
            
        try:
            client.create_score(
                name="total_tokens",
                value=total_tokens,
                trace_id=client.get_current_trace_id()
            )
        except Exception:
            pass
            
        try:
            client.create_score(
                name="duration_ms",
                value=duration_ms,
                trace_id=client.get_current_trace_id()
            )
        except Exception:
            pass
        
        # Also log as an event with detailed metrics
        client.create_event(
            name="llm.usage",
            metadata={
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "duration_ms": duration_ms,
                "cost_usd": round(cost_usd, 6),
                "tokens_per_second": tokens_per_second,
                "cost_per_1k_tokens": cost_per_1k_tokens
            }
        )
    except Exception:
        pass

def _calculate_model_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate approximate cost based on model pricing (as of 2024)."""
    # Pricing per 1K tokens (input/output)
    pricing = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    }
    
    # Normalize model name (remove version suffixes for matching)
    model_key = model.lower()
    for key in pricing.keys():
        if key in model_key:
            rates = pricing[key]
            input_cost = (prompt_tokens / 1000) * rates["input"]
            output_cost = (completion_tokens / 1000) * rates["output"]
            return input_cost + output_cost
    
    # Default fallback pricing (GPT-4o-mini rates)
    return (prompt_tokens / 1000) * 0.00015 + (completion_tokens / 1000) * 0.0006
