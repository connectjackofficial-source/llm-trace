"""Tests for the digest command."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def test_digest_empty():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        assert store.digest(days=7) == {}
        store.close()
    print("test_digest_empty: ok")


def test_digest_aggregates_today():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        store.record("gpt-4o", "a", "b", 10, 5, 20)
        store.record("haiku", "c", "d", 20, 10, 40)
        digest = store.digest(days=7)
        # one day bucket (today)
        assert len(digest) == 1
        day = list(digest.values())[0]
        assert day["calls"] == 2
        assert day["tokens_in"] == 30
        assert day["avg_latency_ms"] == 30
        store.close()
    print("test_digest_aggregates_today: ok")


if __name__ == "__main__":
    test_digest_empty()
    test_digest_aggregates_today()
    print("llm-trace digest tests passed")
