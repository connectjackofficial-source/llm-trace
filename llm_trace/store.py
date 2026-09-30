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
