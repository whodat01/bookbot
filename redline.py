#!/usr/bin/env python3
"""
Lightweight document redline comparison tool.

Compares two text documents and produces a redline showing additions,
deletions, and unchanged text. Supports terminal (colored) and HTML output.

Usage:
    python redline.py original.txt revised.txt
    python redline.py original.txt revised.txt --mode word
    python redline.py original.txt revised.txt --format html -o diff.html
"""

import argparse
import difflib
import sys
from pathlib import Path


# ── ANSI helpers ──────────────────────────────────────────────────────────────

RED = "\033[31m"
GREEN = "\033[32m"
STRIKETHROUGH = "\033[9m"
RESET = "\033[0m"


# ── Diffing core ─────────────────────────────────────────────────────────────


def diff_lines(original: str, revised: str) -> list[dict]:
    """Return a list of change records at the line level.

    Each record: {"tag": "equal"|"insert"|"delete"|"replace",
                  "original": [...], "revised": [...]}
    """
    orig_lines = original.splitlines(keepends=True)
    rev_lines = revised.splitlines(keepends=True)
    sm = difflib.SequenceMatcher(None, orig_lines, rev_lines)
    changes = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        changes.append(
            {
                "tag": tag,
                "original": orig_lines[i1:i2],
                "revised": rev_lines[j1:j2],
            }
        )
    return changes


def diff_words(original: str, revised: str) -> list[dict]:
    """Return a list of change records at the word level.

    Whitespace tokens are preserved so the output can be reassembled into
    readable text.
    """
    orig_tokens = _tokenize(original)
    rev_tokens = _tokenize(revised)
    sm = difflib.SequenceMatcher(None, orig_tokens, rev_tokens)
    changes = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        changes.append(
            {
                "tag": tag,
                "original": orig_tokens[i1:i2],
                "revised": rev_tokens[j1:j2],
            }
        )
    return changes


def _tokenize(text: str) -> list[str]:
    """Split *text* into word and whitespace tokens."""
    tokens: list[str] = []
    current: list[str] = []
    in_space = False
    for ch in text:
        is_space = ch in (" ", "\t", "\n", "\r")
        if is_space != in_space and current:
            tokens.append("".join(current))
            current = []
        current.append(ch)
        in_space = is_space
    if current:
        tokens.append("".join(current))
    return tokens


# ── Terminal (ANSI) formatter ────────────────────────────────────────────────


def format_terminal_line(changes: list[dict]) -> str:
    """Render line-level changes with ANSI colour codes."""
    parts: list[str] = []
    for c in changes:
        if c["tag"] == "equal":
            parts.append("".join(c["revised"]))
        elif c["tag"] == "insert":
            for line in c["revised"]:
                parts.append(f"{GREEN}+ {line.rstrip()}{RESET}\n")
        elif c["tag"] == "delete":
            for line in c["original"]:
                parts.append(f"{RED}{STRIKETHROUGH}- {line.rstrip()}{RESET}\n")
        elif c["tag"] == "replace":
            for line in c["original"]:
                parts.append(f"{RED}{STRIKETHROUGH}- {line.rstrip()}{RESET}\n")
            for line in c["revised"]:
                parts.append(f"{GREEN}+ {line.rstrip()}{RESET}\n")
    return "".join(parts)


def format_terminal_word(changes: list[dict]) -> str:
    """Render word-level changes with ANSI colour codes."""
    parts: list[str] = []
    for c in changes:
        if c["tag"] == "equal":
            parts.append("".join(c["revised"]))
        elif c["tag"] == "insert":
            parts.append(f"{GREEN}{''.join(c['revised'])}{RESET}")
        elif c["tag"] == "delete":
            parts.append(
                f"{RED}{STRIKETHROUGH}{''.join(c['original'])}{RESET}"
            )
        elif c["tag"] == "replace":
            parts.append(
                f"{RED}{STRIKETHROUGH}{''.join(c['original'])}{RESET}"
            )
            parts.append(f"{GREEN}{''.join(c['revised'])}{RESET}")
    return "".join(parts)


# ── HTML formatter ───────────────────────────────────────────────────────────

_HTML_HEADER = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redline Comparison</title>
<style>
  body  { font-family: "Segoe UI", Arial, sans-serif; margin: 2em; line-height: 1.6; }
  .add  { background: #d4edda; color: #155724; text-decoration: underline; }
  .del  { background: #f8d7da; color: #721c24; text-decoration: line-through; }
  pre   { white-space: pre-wrap; word-wrap: break-word; }
</style>
</head>
<body>
<h1>Redline Comparison</h1>
<pre>
"""

_HTML_FOOTER = """\
</pre>
</body>
</html>
"""


def _html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_html_line(changes: list[dict]) -> str:
    parts: list[str] = [_HTML_HEADER]
    for c in changes:
        if c["tag"] == "equal":
            parts.append(_html_escape("".join(c["revised"])))
        elif c["tag"] == "insert":
            parts.append(
                f'<span class="add">{_html_escape("".join(c["revised"]))}</span>'
            )
        elif c["tag"] == "delete":
            parts.append(
                f'<span class="del">{_html_escape("".join(c["original"]))}</span>'
            )
        elif c["tag"] == "replace":
            parts.append(
                f'<span class="del">{_html_escape("".join(c["original"]))}</span>'
            )
            parts.append(
                f'<span class="add">{_html_escape("".join(c["revised"]))}</span>'
            )
    parts.append(_HTML_FOOTER)
    return "".join(parts)


def format_html_word(changes: list[dict]) -> str:
    parts: list[str] = [_HTML_HEADER]
    for c in changes:
        if c["tag"] == "equal":
            parts.append(_html_escape("".join(c["revised"])))
        elif c["tag"] == "insert":
            parts.append(
                f'<span class="add">{_html_escape("".join(c["revised"]))}</span>'
            )
        elif c["tag"] == "delete":
            parts.append(
                f'<span class="del">{_html_escape("".join(c["original"]))}</span>'
            )
        elif c["tag"] == "replace":
            parts.append(
                f'<span class="del">{_html_escape("".join(c["original"]))}</span>'
            )
            parts.append(
                f'<span class="add">{_html_escape("".join(c["revised"]))}</span>'
            )
    parts.append(_HTML_FOOTER)
    return "".join(parts)


# ── Public API ───────────────────────────────────────────────────────────────


def redline(
    original: str,
    revised: str,
    *,
    mode: str = "word",
    output_format: str = "terminal",
) -> str:
    """Compare *original* and *revised* text and return a redline string.

    Parameters
    ----------
    mode : ``"word"`` | ``"line"``
        Granularity of the comparison.
    output_format : ``"terminal"`` | ``"html"``
        Rendering format.
    """
    if mode == "word":
        changes = diff_words(original, revised)
        formatter = format_html_word if output_format == "html" else format_terminal_word
    else:
        changes = diff_lines(original, revised)
        formatter = format_html_line if output_format == "html" else format_terminal_line
    return formatter(changes)


# ── CLI ──────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compare two documents and produce a redline of the changes.",
    )
    p.add_argument("original", help="Path to the original document")
    p.add_argument("revised", help="Path to the revised document")
    p.add_argument(
        "--mode",
        choices=["word", "line"],
        default="word",
        help="Comparison granularity (default: word)",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["terminal", "html"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    p.add_argument(
        "-o",
        "--output",
        help="Write output to a file instead of stdout",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    orig_path = Path(args.original)
    rev_path = Path(args.revised)

    if not orig_path.is_file():
        sys.exit(f"Error: file not found: {orig_path}")
    if not rev_path.is_file():
        sys.exit(f"Error: file not found: {rev_path}")

    original = orig_path.read_text(encoding="utf-8")
    revised = rev_path.read_text(encoding="utf-8")

    result = redline(original, revised, mode=args.mode, output_format=args.fmt)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Redline written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
