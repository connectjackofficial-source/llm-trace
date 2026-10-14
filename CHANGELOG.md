# Changelog

## 0.4.0 - 2026-10-14

- `errors(limit)` store method: flag calls whose response matches known
  error markers (error/exception/timeout/denied/retry…)
- `errors` CLI command: surface failing calls with the matched marker

## 0.3.0 - 2026-10-10

- `digest` command: per-day totals for the last N days
- `digest(days)` store method with SQL date filtering

## 0.2.0 - 2026-10-08

- `prune` command: keep only the newest N traces
- `export` command: write traces to CSV
- `clear` command: delete all traces
- close() / context-manager support

## 0.1.0 - 2026-09-29

- Initial release
- Record, summary, totals commands
- SQLite storage
