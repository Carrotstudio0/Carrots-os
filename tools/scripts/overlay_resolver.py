#!/usr/bin/env python3
"""Resolve CarrotOS overlay order from a simple YAML manifest.

This tool intentionally avoids external dependencies in the baseline scaffold.
"""

from __future__ import annotations

from pathlib import Path
from typing import List


def parse_overlay_order(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    order: List[str] = []
    in_list = False

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("overlay_order:"):
            in_list = True
            continue
        if in_list and line.startswith("-"):
            order.append(line[1:].strip())
            continue
        if in_list and not line.startswith("-"):
            break

    if not order:
        raise ValueError(f"No overlay_order entries found in {path}")
    return order


def main() -> int:
    manifest = Path("build/manifests/overlay-order.yaml")
    if not manifest.exists():
        print(f"error: missing manifest: {manifest}")
        return 2

    order = parse_overlay_order(manifest)
    print("overlay order:")
    for idx, entry in enumerate(order, start=1):
        print(f"{idx}. {entry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
