"""llm-trace CLI."""
import argparse
import json

from .store import TraceStore


def main():
    ap = argparse.ArgumentParser(prog="llm-trace")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="record a call manually")
    r.add_argument("--model", required=True)
    r.add_argument("--prompt", required=True)
    r.add_argument("--response", required=True)
    r.add_argument("--tokens-in", type=int, default=0)
    r.add_argument("--tokens-out", type=int, default=0)
    r.add_argument("--latency-ms", type=int, default=0)

    s = sub.add_parser("summary", help="recent traces")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--model", default=None)
    sub.add_parser("totals", help="aggregated totals")
    sub.add_parser("by-model", help="per-model breakdown")
    sub.add_parser("clear", help="delete all traces")

    p = sub.add_parser("prune", help="keep only the newest N traces")
    p.add_argument("--keep", type=int, default=1000)

    e = sub.add_parser("export", help="export traces to CSV")
    e.add_argument("--out", default=None)
    e.add_argument("--limit", type=int, default=500)

    d = sub.add_parser("digest", help="per-day totals for the last N days")
    d.add_argument("--days", type=int, default=7)

    slow = sub.add_parser("slow", help="the N slowest calls (perf outliers)")
    slow.add_argument("--n", type=int, default=5)

    args = ap.parse_args()
    store = TraceStore()

    if args.cmd == "record":
        rid = store.record(args.model, args.prompt, args.response,
                           args.tokens_in, args.tokens_out, args.latency_ms)
        print(json.dumps({"recorded": True, "id": rid}))
    elif args.cmd == "summary":
        rows = store.summary(limit=args.limit)
        if args.model:
            rows = [r for r in rows if r["model"] == args.model]
        for row in rows:
            print(f"[{row['id']}] {row['ts']} {row['model']} "
                  f"in={row['tokens_in']} out={row['tokens_out']} "
                  f"{row['latency_ms']}ms")
    elif args.cmd == "totals":
        print(json.dumps(store.totals(), indent=2))
    elif args.cmd == "by-model":
        print(json.dumps(store.by_model(), indent=2))
    elif args.cmd == "clear":
        print(json.dumps({"deleted": store.clear()}))
    elif args.cmd == "prune":
        print(json.dumps({"deleted": store.prune(keep=args.keep)}))
    elif args.cmd == "export":
        out = store.export_csv(path=args.out, limit=args.limit)
        print(json.dumps({"exported": str(out), "rows": args.limit}))
    elif args.cmd == "digest":
        print(json.dumps(store.digest(days=args.days), indent=2))
    elif args.cmd == "slow":
        print(json.dumps(store.slowest(n=args.n), indent=2))


if __name__ == "__main__":
    main()
