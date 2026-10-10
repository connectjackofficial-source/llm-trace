"""llm-trace: lightweight observability for LLM calls.

Stores traces in a local SQLite DB. No cloud, no vendor lock-in.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional


def db_path() -> Path:
    root = os.environ.get("LLM_TRACE_DIR")
    if root:
        return Path(root) / "traces.db"
    return Path.home() / ".llm-trace" / "traces.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    model TEXT,
    prompt TEXT,
    response TEXT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    latency_ms INTEGER,
    tags TEXT
);
"""


class TraceStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def record(self, model: str, prompt: str, response: str,
               tokens_in: int = 0, tokens_out: int = 0,
               latency_ms: int = 0, tags: Optional[list] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO traces (ts, model, prompt, response, tokens_in, "
            "tokens_out, latency_ms, tags) VALUES (?,?,?,?,?,?,?,?)",
            (time.strftime("%Y-%m-%dT%H:%M:%S"), model, prompt, response,
             tokens_in, tokens_out, latency_ms,
             json.dumps(tags or [])))
        self.conn.commit()
        return cur.lastrowid

    def summary(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, ts, model, tokens_in, tokens_out, latency_ms "
            "FROM traces ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        keys = ["id", "ts", "model", "tokens_in", "tokens_out", "latency_ms"]
        return [dict(zip(keys, r)) for r in rows]

    def totals(self) -> dict:
        row = self.conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(tokens_in),0), "
            "COALESCE(SUM(tokens_out),0), COALESCE(AVG(latency_ms),0) "
            "FROM traces").fetchone()
        return {"calls": row[0], "tokens_in": row[1],
                "tokens_out": row[2], "avg_latency_ms": round(row[3])}

    def clear(self) -> int:
        cur = self.conn.execute("DELETE FROM traces")
        self.conn.commit()
        return cur.rowcount

    def by_model(self) -> dict:
        """Per-model aggregated stats."""
        rows = self.conn.execute(
            "SELECT model, COUNT(*), SUM(tokens_in), SUM(tokens_out), "
            "AVG(latency_ms) FROM traces GROUP BY model").fetchall()
        return {r[0]: {"calls": r[1], "tokens_in": r[2],
                       "tokens_out": r[3],
                       "avg_latency_ms": round(r[4])} for r in rows}

    def digest(self, days: int = 7) -> dict:
        """Per-day totals for the last N days: calls, tokens, avg latency."""
        out = {}
        rows = self.conn.execute(
            "SELECT substr(ts,1,10) AS day, COUNT(*), SUM(tokens_in), "
            "SUM(tokens_out), AVG(latency_ms) FROM traces "
            "WHERE substr(ts,1,10) >= date('now', ?) "
            "GROUP BY day ORDER BY day",
            (f"-{days} days",)).fetchall()
        for day, calls, tin, tout, avg in rows:
            out[day] = {"calls": calls, "tokens_in": tin,
                        "tokens_out": tout,
                        "avg_latency_ms": round(avg) if avg else 0}
        return out

    def slowest(self, n: int = 5) -> list[dict]:
        """The N slowest calls (latency > 0), most recent first."""
        rows = self.conn.execute(
            "SELECT id, ts, model, prompt, latency_ms FROM traces "
            "WHERE latency_ms > 0 ORDER BY latency_ms DESC, id DESC LIMIT ?",
            (n,)).fetchall()
        return [{"id": r[0], "ts": r[1], "model": r[2],
                 "prompt": (r[3] or "")[:60], "latency_ms": r[4]}
                for r in rows]

    def prune(self, keep: int = 1000) -> int:
        """Delete the oldest traces, keeping the newest *keep* rows."""
        cur = self.conn.execute(
            "DELETE FROM traces WHERE id NOT IN "
            "(SELECT id FROM traces ORDER BY id DESC LIMIT ?)", (keep,))
        self.conn.commit()
        return cur.rowcount

    def export_csv(self, path: Optional[Path] = None,
                   limit: int = 500) -> Path:
        """Write recent traces to a CSV file. Returns the output path."""
        import csv
        out = Path(path) if path else self.path.with_name("traces.csv")
        rows = self.conn.execute(
            "SELECT id, ts, model, tokens_in, tokens_out, latency_ms, "
            "prompt FROM traces ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "ts", "model", "tokens_in",
                             "tokens_out", "latency_ms", "prompt"])
            writer.writerows(rows)
        return out
