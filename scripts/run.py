#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "merc-py"))
from merc import Benchmarks, ToolNotFoundError  # type: ignore


def main():
    parser = argparse.ArgumentParser(
        description="Run merc-sym reduce strong-bisim-sigref on every .lps file in a directory"
    )
    parser.add_argument("merc_path", help="Path to the directory containing the merc-sym binary")
    parser.add_argument("lps_dir", help="Directory to search for .lps files")
    parser.add_argument("--output", "-o", default="results.ndjson", help="Output NDJSON file (default: results.ndjson)")
    parser.add_argument("--runs", "-r", type=int, default=5, help="Number of runs per benchmark (default: 5)")
    args = parser.parse_args()

    merc_sym = os.path.join(args.merc_path, "merc-sym")
    lps_files = sorted(Path(args.lps_dir).rglob("*.lps"))

    if not lps_files:
        print(f"No .lps files found in {args.lps_dir}", file=sys.stderr)
        sys.exit(1)

    bench = Benchmarks(runs=args.runs)
    for lps_file in lps_files:
        name = str(lps_file.relative_to(args.lps_dir))
        bench.add(name, merc_sym, ["reduce", "strong-bisim-sigref", str(lps_file)])

    try:
        bench.run(args.output)
    except ToolNotFoundError as e:
        print(f"Tool not found: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
