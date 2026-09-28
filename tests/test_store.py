"""Tests for llm-trace store."""
import tempfile
from pathlib import Path

from llm_trace.store import TraceStore


def test_record_and_summary():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        rid = store.record("gpt-4o", "hi", "hello", 5, 2, 100)
        assert rid == 1
        rows = store.summary()
        assert len(rows) == 1
        assert rows[0]["model"] == "gpt-4o"
        store.conn.close()
    print("test_record_and_summary: ok")


def test_totals():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        store.record("m", "a", "b", 10, 5, 200)
        store.record("m", "c", "d", 20, 8, 400)
        t = store.totals()
        assert t["calls"] == 2
        assert t["tokens_in"] == 30
        assert t["tokens_out"] == 13
        store.conn.close()
    print("test_totals: ok")


if __name__ == "__main__":
    test_record_and_summary()
    test_totals()
    print("llm-trace tests passed")
