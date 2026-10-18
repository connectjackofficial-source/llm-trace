"""Tests for TraceStore.search_prompts and stats_by_day."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_trace.store import TraceStore


def _store():
    tmp = tempfile.mkdtemp()
    return TraceStore(Path(tmp) / "t.db")


def test_search_prompts():
    st = _store()
    st.record("gpt-4o", "explain the diff algorithm", "ok", 10, 5, 120)
    st.record("gpt-4o", "summarize the meeting notes", "ok", 20, 8, 200)
    hits = st.search_prompts("diff")
    assert len(hits) == 1, hits
    assert hits[0]["model"] == "gpt-4o"
    assert st.search_prompts("meeting")[0]["prompt"].startswith("summarize")
    assert st.search_prompts("nonexistent-term") == []
    print("test_search_prompts: ok")


def test_stats_by_day_gap_free():
    st = _store()
    st.record("gpt-4o", "p", "r", 1, 1, 100)
    st.record("gpt-4o", "p", "r", 1, 1, 300)
    st.conn.execute("UPDATE traces SET ts = '2026-10-16T10:00:00' WHERE id = 1")
    st.conn.execute("UPDATE traces SET ts = '2026-10-16T11:00:00' WHERE id = 2")
    st.conn.commit()
    series = st.stats_by_day(days=3)
    assert len(series) == 3
    first = series[0]
    assert first["calls"] == 2, series
    assert first["latency_ms"] == 400
    assert first["avg_ms"] == 200.0
    assert series[1]["calls"] == 0  # gap-free
    print("test_stats_by_day_gap_free: ok")


if __name__ == "__main__":
    test_search_prompts()
    test_stats_by_day_gap_free()
    print("llm-trace batch2 tests passed")
