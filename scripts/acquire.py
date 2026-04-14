#!/usr/bin/env python3
"""
Download the Disease Ontology OWL from the OBO Foundry PURL (public, no auth).

Usage:
    python scripts/acquire.py --output tmp/doid_raw.owl
    python scripts/acquire.py --output tmp/doid_raw.owl --url https://example.org/doid.owl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

DEFAULT_DOID_URL = "http://purl.obolibrary.org/obo/doid.owl"
CHUNK_SIZE = 1024 * 1024


def download(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url}", file=sys.stderr)
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(output, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                fh.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(
                        f"\r  {pct:.1f}%  ({downloaded:,} / {total:,} bytes)",
                        end="",
                        file=sys.stderr,
                    )
        print(file=sys.stderr)
    print(f"Saved: {output}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download DOID OWL")
    parser.add_argument("--output", type=Path, default=Path("tmp/doid_raw.owl"))
    parser.add_argument("--url", default=None, help="Override download URL")
    args = parser.parse_args()

    url = args.url if args.url else DEFAULT_DOID_URL
    download(url, args.output)


if __name__ == "__main__":
    main()
