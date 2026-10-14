"""Tests for llm-trace model_health."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def _store():
    tmp = tempfile.TemporaryDirectory()
    s = TraceStore(Path(tmp.name) / "t.db")
    return s, tmp


def test_health_rates():
    s, tmp = _store()
    s.record("gpt", "p1", "ok response")
    s.record("gpt", "p2", "ok again")
    s.record("gpt", "p3", "ERROR: rate limit exceeded", latency_ms=500)
    s.record("claude", "p4", "timeout after 30s", latency_ms=2000)
    s.record("claude", "p5", "fine", latency_ms=100)
    health = {h["model"]: h for h in s.model_health()}
    assert health["claude"]["error_rate"] == 0.5
    assert health["gpt"]["error_rate"] == round(1 / 3, 3)
    assert health["claude"]["avg_latency_ms"] == 1050.0
    s.close()
    tmp.cleanup()
    print("test_health_rates: ok")


def test_health_sorted_by_error_rate():
    s, tmp = _store()
    s.record("a", "p", "ok")
    s.record("b", "p", "failed to connect")
    s.record("c", "p", "error boom")
    health = s.model_health()
    assert health[0]["model"] in ("b", "c")  # highest error rate first
    assert health[-1]["model"] == "a"        # clean model last
    s.close()
    tmp.cleanup()
    print("test_health_sorted_by_error_rate: ok")


def test_empty_store():
    s, tmp = _store()
    assert s.model_health() == []
    s.close()
    tmp.cleanup()
    print("test_empty_store: ok")


if __name__ == "__main__":
    test_health_rates()
    test_health_sorted_by_error_rate()
    test_empty_store()
    print("llm-trace model_health tests passed")
