# llm-trace

> Lightweight observability for LLM calls. Record prompts, responses, tokens,
> and latency to a local SQLite file. No cloud, no vendor lock-in.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

When you call an LLM from scripts, agents, or tests, you lose the ability to
answer simple questions: what did I actually ask? How many tokens did that
cost? Which model was slowest? `llm-trace` records every call to a local
SQLite file and lets you query it back.

## Install

```bash
git clone https://github.com/connectjackofficial-source/llm-trace.git
cd llm-trace
```

## Usage

```bash
# record a call manually
python -m llm_trace.cli record \
  --model gpt-4o --prompt "hello" --response "hi" \
  --tokens-in 5 --tokens-out 2 --latency-ms 120

# recent traces
python -m llm_trace.cli summary

# totals
python -m llm_trace.cli totals

# per-model breakdown
python -m llm_trace.cli by-model

# keep only the newest 500 traces
python -m llm_trace.cli prune --keep 500

# export recent traces to CSV (handy for spreadsheets)
python -m llm_trace.cli export --out traces.csv

# wipe everything
python -m llm_trace.cli clear
```

## Data

Stored at `~/.llm-trace/traces.db` (override with `LLM_TRACE_DIR`).
One table, inspect it with any SQLite viewer.

## Why not Langfuse / LangSmith?

Those are great, but they need a server, an account, and a network call.
`llm-trace` is one file, one command, zero setup. Use it for local scripts
and quick experiments; graduate to a hosted platform when you need dashboards.

## License

MIT
