"""Tests for llm-trace export_json."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def test_export_json():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "t.db"
        with TraceStore(db) as s:
            s.record("gpt", "hello", "hi there", 10, 5, 42, tags=["a"])
            s.record("claude", "bye", "see you", 8, 3, 55)
            out = Path(td) / "traces.json"
            n = s.export_json(out)
            assert n == 2
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 2
        assert data[0]["model"] == "gpt"
        assert data[0]["tags"] == ["a"]
        assert set(data[0]) == {"id", "ts", "model", "prompt", "response",
                                "tokens_in", "tokens_out", "latency_ms",
                                "tags"}
    print("test_export_json: ok")


def test_export_empty():
    with tempfile.TemporaryDirectory() as td:
        with TraceStore(Path(td) / "t.db") as s:
            out = Path(td) / "e.json"
            assert s.export_json(out) == 0
        assert json.loads(out.read_text(encoding="utf-8")) == []
    print("test_export_empty: ok")


if __name__ == "__main__":
    test_export_json()
    test_export_empty()
    print("llm-trace export_json tests passed")
