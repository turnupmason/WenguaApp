"""Read original-chart JSON and render health/severity research template."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from src.wengua.health_severity_template import render_health_severity


def main(argv=None):
    ap = argparse.ArgumentParser(description="Health/severity detailed symbolic template")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--database", default=None, help="Optional read-only full SQLite")
    args = ap.parse_args(argv)
    source, destination = Path(args.input).resolve(), Path(args.output).resolve()
    if source == destination:
        ap.error("Output must differ from input: immutable source chart")
    payload = json.loads(source.read_text(encoding="utf-8"))
    report = render_health_severity(
        payload["chart"], payload["inquiry"],
        calendar=payload.get("calendar") or payload.get("calendar_inputs") or {},
        db_path=args.database)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": report["status"], "sections": len(report["sections"]),
                      "result": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
