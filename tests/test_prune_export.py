"""Tests for prune and CSV export."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def test_prune_keeps_newest():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        for i in range(10):
            store.record(f"m{i % 3}", f"p{i}", "r", 5, 2, 10)
        deleted = store.prune(keep=4)
        assert deleted == 6
        assert store.totals()["calls"] == 4
        store.close()
    print("test_prune_keeps_newest: ok")


def test_export_csv():
    with tempfile.TemporaryDirectory() as d:
        store = TraceStore(Path(d) / "t.db")
        store.record("gpt-4o", "hello", "hi", 5, 2, 10)
        out = store.export_csv(Path(d) / "out.csv")
        lines = out.read_text(encoding="utf-8").splitlines()
        assert lines[0].startswith("id,ts,model")
        assert len(lines) == 2
        store.close()
    print("test_export_csv: ok")


if __name__ == "__main__":
    test_prune_keeps_newest()
    test_export_csv()
    print("llm-trace prune/export tests passed")
