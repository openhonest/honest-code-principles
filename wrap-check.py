#!/usr/bin/env python3
"""Refuse a hard-wrapped markdown file.

One paragraph is one line, however long. A hard wrap fights the editor's own wrapping, breaks reflow
in Typora and every other renderer, and turns a one-word edit into a whole-paragraph rewrap.

The rule existed as prose for a long time and was broken anyway, twice in one day, the second time in
this repository's first commit. A rule with nothing running it is advice. This is the operation.

Detection is a paragraph of two or more lines where a line ends without terminal punctuation and the
next line continues it in lower case: that is a sentence cut in half, which is what a hard wrap makes
and what deliberate prose does not.
"""

import re
import sys
from pathlib import Path

CONTINUES = re.compile(r"[^.:;!?)\]]$")
LOWER_START = re.compile(r"^[a-z(`\"']")
SKIP = re.compile(r"^\s*(#{1,6} |[-*+] |\d+\. |> |\| |```|---\s*$)")


def wrapped_lines(text: str) -> list[int]:
    """The 1-based line numbers that end mid-sentence with a continuation below. Pure."""
    lines, fence, found = text.split("\n"), False, []
    for i, line in enumerate(lines[:-1]):
        if line.strip().startswith("```"):
            fence = not fence
        if fence or SKIP.match(line) or not line.strip():
            continue
        nxt = lines[i + 1]
        if nxt.strip() and not SKIP.match(nxt) and CONTINUES.search(line.rstrip()) and LOWER_START.match(nxt.strip()):
            found.append(i + 1)
    return found


def main(paths: list[str]) -> int:
    bad = {p: wrapped_lines(Path(p).read_text(encoding="utf-8")) for p in paths}
    bad = {p: n for p, n in bad.items() if n}
    if not bad:
        print(f"wrap-check: {len(paths)} file(s), one paragraph per line.")
        return 0
    for path, numbers in bad.items():
        print(f"wrap-check: {path} is hard-wrapped at line(s) {', '.join(map(str, numbers))}.", file=sys.stderr)
    print("  One paragraph is one line. Join them and commit again.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or [str(p) for p in Path(".").rglob("*.md")]))
