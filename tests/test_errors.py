"""Tests for TraceStore.errors."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def _store():
    tmp = tempfile.TemporaryDirectory()
    s = TraceStore(Path(tmp.name) / "t.db")
    s.record("gpt-4", "summarize this", "Here is a clean summary.")
    s.record("claude", "parse json", "Error: unexpected token at position 3",
             tokens_in=10, latency_ms=500)
    s.record("gemini", "translate", "Timeout after 30s, please retry",
             tokens_out=5)
    s.record("gpt-4", "hi", "response denied: no permission")
    return s, tmp


def test_error_detection():
    s, tmp = _store()
    errs = s.errors()
    markers = {e["error"] for e in errs}
    assert "error" in markers
    assert "timeout" in markers
    assert "denied" in markers
    # clean call is not flagged
    assert all(e["id"] != 1 for e in errs)
    s.close()
    tmp.cleanup()
    print("test_error_detection: ok")


def test_limit():
    s, tmp = _store()
    errs = s.errors(limit=1)
    assert len(errs) == 1
    assert errs[0]["id"] == 4  # newest error first
    s.close()
    tmp.cleanup()
    print("test_limit: ok")


def test_fields_and_truncation():
    s, tmp = _store()
    errs = s.errors()
    first = errs[0]
    assert set(first) >= {"id", "ts", "model", "error", "response",
                          "latency_ms"}
    assert len(first["prompt"]) <= 60
    s.close()
    tmp.cleanup()
    print("test_fields_and_truncation: ok")


if __name__ == "__main__":
    test_error_detection()
    test_limit()
    test_fields_and_truncation()
    print("llm-trace errors tests passed")
