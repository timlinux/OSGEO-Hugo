#!/usr/bin/env python3
"""Generate the block/shortcode gallery page from data/shortcodes.json.

The registry in data/shortcodes.json is the single source of truth for
the project's shortcodes. Three consumers stay in lockstep through it:

  * this generator writes content/dev/blocks/index.md, rendering each
    registered shortcode as a live demo with the exact same snippet
    shown as syntax underneath (the two cannot drift: one string feeds
    both);
  * .nvim.lua reads the registry at runtime for the :InsertBlock
    picker (<leader>pa);
  * `osgeo blocks` runs this script, which also cross-checks the
    registry against the shortcode template files on disk and reports
    any drift (--check exits non-zero on drift, for CI).

Usage:
    generate_blocks_demo.py            # regenerate page + drift report
    generate_blocks_demo.py --check    # drift report only, exit 1 on drift
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "shortcodes.json"
OUTPUT = ROOT / "content" / "dev" / "blocks" / "index.md"
SHORTCODE_DIRS = [
    ROOT / "layouts" / "shortcodes",
    ROOT / "themes" / "hugo-bulma-blocks-theme" / "layouts" / "shortcodes",
]

GROUP_ORDER = ["Layout", "Content", "Data", "Utility"]

FRONT_MATTER = """---
type: "page"
title: "Block & Shortcode Gallery"
subtitle: "Every content block this site provides, with the syntax to use it"
description: "Live demos of all Hugo shortcodes available in this project, each followed by the exact markup that produced it."
draft: false
heroSize: "is-small"
HasBanner: true
---

<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate with: osgeo blocks
     Source of truth: data/shortcodes.json -->

This gallery is generated from `data/shortcodes.json` — the same
registry that powers the Neovim `:InsertBlock` picker. Each entry shows
the rendered block followed by the exact markup that produced it.

"""


def escape_snippet(snippet: str) -> str:
    """Escape shortcode delimiters so Hugo prints them literally."""
    return (
        snippet.replace("{{<", "{{</*")
        .replace(">}}", "*/>}}")
        .replace("{{%", "{{%/*")
        .replace("%}}", "*/%}}")
    )


def files_on_disk() -> set[str]:
    names: set[str] = set()
    for directory in SHORTCODE_DIRS:
        if directory.is_dir():
            names.update(p.stem for p in directory.glob("*.html"))
    return names


def drift_report(entries: list[dict]) -> tuple[set[str], set[str]]:
    registered = {e["name"] for e in entries}
    # Paired end-shortcodes are covered by their start entry.
    covered = set(registered)
    for entry in entries:
        if entry.get("pair_end"):
            covered.add(entry["pair_end"])
    on_disk = files_on_disk()
    missing = on_disk - covered  # exists on disk, absent from registry
    stale = registered - on_disk  # registered, but template file gone
    return missing, stale


def render(entries: list[dict]) -> str:
    out = [FRONT_MATTER]
    for group in GROUP_ORDER:
        members = [e for e in entries if e.get("group") == group]
        if not members:
            continue
        out.append(f"## {group} blocks\n\n")
        for entry in sorted(members, key=lambda e: e["name"]):
            # The wrapper div lets tooling (osgeo blocks --pdf) capture
            # each block as one slide.
            out.append(f'<div class="block-demo-card" id="block-{entry["name"]}">\n\n')
            out.append(f"### `{entry['name']}`\n\n")
            out.append(f"{entry['description']}\n\n")
            if entry.get("params"):
                params = " · ".join(
                    f"`{k}` — {v}" for k, v in sorted(entry["params"].items())
                )
                out.append(f"Parameters: {params}\n\n")
            if entry.get("demo_safe"):
                out.append(entry["snippet"].rstrip() + "\n\n")
            else:
                out.append(
                    "_This block depends on site data or external services"
                    " and is not demoed inline._\n\n"
                )
            # Plain fence: chroma's go-html-template lexer marks the
            # escaped delimiters as error tokens (ugly dark glyphs).
            out.append("```text\n")
            out.append(escape_snippet(entry["snippet"].rstrip()) + "\n")
            out.append("```\n\n</div>\n\n---\n\n")
    return "".join(out)


def main() -> int:
    check_only = "--check" in sys.argv
    entries = json.loads(REGISTRY.read_text())

    missing, stale = drift_report(entries)
    for name in sorted(missing):
        print(f"⚠ shortcode on disk but not in registry: {name}")
    for name in sorted(stale):
        print(f"⚠ registry entry without a template file: {name}")

    if not check_only:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(render(entries))
        print(f"✅ wrote {OUTPUT.relative_to(ROOT)} ({len(entries)} blocks)")

    if missing or stale:
        print("❌ registry and shortcode files have drifted"
              " — update data/shortcodes.json")
        return 1 if check_only else 0
    print("✅ registry and shortcode files are in lockstep")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
