"""Tests for slow-call ranking."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def test_slowest_ranks_by_latency():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        try:
            store.record("sonnet", "slow", "r", latency_ms=100)
            store.record("opus", "fast", "r", latency_ms=10)
            store.record("sonnet", "slowest", "r", latency_ms=500)
            slow = store.slowest(n=3)
            assert slow[0]["latency_ms"] == 500
            assert slow[1]["latency_ms"] == 100
            assert slow[2]["latency_ms"] == 10
            assert slow[0]["prompt"] == "slowest"
            assert "model" in slow[0]
        finally:
            store.close()
    print("test_slowest_ranks_by_latency: ok")


def test_slowest_skips_zero():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        try:
            store.record("sonnet", "no-latency", "r", latency_ms=0)
            assert store.slowest() == []
        finally:
            store.close()
    print("test_slowest_skips_zero: ok")


def test_slowest_limit():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        try:
            for i in range(6):
                store.record("sonnet", f"c{i}", "r", latency_ms=i * 10 + 1)
            assert len(store.slowest(n=3)) == 3
            assert store.slowest(n=99)[0]["latency_ms"] == 51
        finally:
            store.close()
    print("test_slowest_limit: ok")


if __name__ == "__main__":
    test_slowest_ranks_by_latency()
    test_slowest_skips_zero()
    test_slowest_limit()
    print("llm-trace slowest tests passed")
