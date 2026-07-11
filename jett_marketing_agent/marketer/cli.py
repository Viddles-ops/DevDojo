"""On-demand PDF generation from the command line (for scripts and agents).

    python -m marketer.cli <dataset-id> [--out FILE.pdf]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from marketer import narrator, pdf_writer, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Jett-branded PDF.")
    parser.add_argument("dataset", nargs="?", help="dataset id (see --list)")
    parser.add_argument("--out", type=Path, help="output path (default <dataset>.pdf)")
    parser.add_argument("--list", action="store_true", help="list available datasets")
    args = parser.parse_args()

    if args.list or not args.dataset:
        for d in stats.list_datasets():
            print(d)
        return

    ds = stats.load_dataset(args.dataset)
    narrative, used_llm = narrator.narrate(ds)
    out = args.out or Path(f"{args.dataset}.pdf")
    out.write_bytes(pdf_writer.render_pdf(ds, narrative))
    note = "Ollama narrative" if used_llm else "fallback narrative (Ollama down)"
    if ds.suppressed:
        note += f"; {ds.suppressed} metric(s) suppressed (small cell)"
    print(f"Wrote {out} ({note})")


if __name__ == "__main__":
    main()
