"""Test by_model breakdown."""
import tempfile
from pathlib import Path

from llm_trace.store import TraceStore


def test_by_model():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        store.record("gpt-4o", "a", "b", 10, 5, 100)
        store.record("gpt-4o", "c", "d", 20, 8, 200)
        store.record("haiku", "e", "f", 5, 2, 50)
        stats = store.by_model()
        assert stats["gpt-4o"]["calls"] == 2
        assert stats["gpt-4o"]["tokens_in"] == 30
        assert stats["haiku"]["calls"] == 1
        store.conn.close()
    print("test_by_model: ok")


if __name__ == "__main__":
    test_by_model()
    print("by_model test passed")
