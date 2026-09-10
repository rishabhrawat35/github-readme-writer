#!/usr/bin/env python3
"""Lint a README against the github-readme-writer rules. Exit 1 on any finding.

usage: python3 lint.py <README.md> [--max-body-words 1800] [--min-body-words 150]

Checks: relative links and images exist (markdown, reference-style, HTML
<a href>/<img src>); #anchors match a heading (GitHub rule, incl. -1 -2 for
duplicates and emoji stripping); no unclosed code fence; no placeholders
(<thing>, TODO, TBD, lorem, xxx) in prose or commands; no banned filler words
in prose (code spans and code blocks are exempt); a code block in the first
40 lines; a first heading exists; body word count (outside code blocks and
tables) within bounds; a "License" heading exists.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

BANNED = ["simply", "just", "easy", "easily", "powerful", "seamless", "seamlessly", "robust",
          "cutting-edge", "state-of-the-art", "blazing", "leverage", "leverages", "best-in-class",
          "world-class", "effortless", "effortlessly", "comprehensive", "empower", "empowers", "unlock",
          "delve", "streamline", "streamlines", "elevate", "game-changing", "ensure", "ensures"]
HTML_TAGS = {"a", "abbr", "b", "br", "blockquote", "code", "dd", "del", "details", "div", "dl", "dt",
             "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "ins", "kbd", "li", "ol",
             "p", "picture", "pre", "s", "samp", "small", "source", "span", "strong", "sub",
             "summary", "sup", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul", "var",
             "video", "center", "font", "u", "tt", "big", "strike", "input", "ruby", "rt", "rp",
             "svg", "path", "g", "rect", "circle", "text", "figure", "figcaption", "caption", "wbr"}
PLACEHOLDER_WORDS = {"thing", "feature", "name", "path", "file", "filename", "repo", "dir", "folder",
                     "url", "slug", "placeholder", "tbd", "command", "arg", "args", "value", "version",
                     "token", "key", "id", "user", "username", "password", "email", "host", "port",
                     "project", "package", "project-name", "your-name", "insert", "description",
                     "org", "owner", "branch", "tag", "date", "n", "x", "y", "number", "text"}
PLACEHOLDER_TEXT = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|lorem ipsum|\bxxx+\b|\[insert [^\]]*\]", re.I)
ANGLE = re.compile(r"<([A-Za-z][A-Za-z0-9_./ -]{0,40})>")
LINK = re.compile(r"\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)", re.M)
HTML_HREF = re.compile(r"<(?:a|img|source|video)\b[^>]*?\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
# A code-block line that is a command the reader is meant to type.
RUNNER = re.compile(r"^(\$ |> |(sudo |uv run |npx |pipx run )?(python3?|node|npm|pnpm|yarn|bun|deno|pip3?|uv|cargo|go|make|just|"
                    r"docker|docker-compose|kubectl|git|gh|claude|codex|gemini|cursor|bash|sh|\./|/[a-z][\w.-]*\b))")


def gh_anchor(heading: str) -> str:
    """GitHub's heading → anchor rule: lowercase, drop punctuation and emoji, space → '-'."""
    h = re.sub(r"`([^`]*)`", r"\1", heading)          # backticks are removed, content kept
    h = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", h)  # links keep their text
    h = re.sub(r"<[^>]+>", "", h).strip().lower()
    out = []
    for ch in h:
        cat = unicodedata.category(ch)
        if ch in " -_" or cat[0] in "LN":
            out.append(ch)
    return "".join(out).replace(" ", "-")


def is_placeholder(token: str) -> bool:
    t = token.strip().lower().rstrip("/")
    if not t or t.split()[0] in HTML_TAGS or t.startswith(("http", "mailto")) or "@" in t:
        return False  # an HTML tag, an autolink or an e-mail address
    first = t.split()[0]
    return first in PLACEHOLDER_WORDS or first.startswith("your") or any(c in first for c in "/_-")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("readme")
    ap.add_argument("--max-body-words", type=int, default=1800)
    ap.add_argument("--min-body-words", type=int, default=150)
    a = ap.parse_args()
    path = Path(a.readme)
    if not path.is_file():
        sys.exit(f"no file: {path}")
    root = path.parent
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings = []

    # Split prose from code blocks; keep line numbers for messages.
    in_code, fence_mark, fence_line = False, "", 0
    body, code, headings, code_first40 = [], [], [], False
    for i, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if m and (not in_code or line.strip().startswith(fence_mark[0] * len(fence_mark))):
            if not in_code:
                in_code, fence_mark, fence_line = True, m.group(1), i
                if i <= 40:
                    code_first40 = True
            else:
                in_code = False
            continue
        if in_code:
            code.append((i, line))
            continue
        h = re.match(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if h:
            headings.append(h.group(2))
        if line.strip().startswith("|"):
            continue
        body.append((i, line))
    if in_code:
        findings.append(f"unclosed code fence opened at line {fence_line}; everything after it renders as code")
    for hm in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", text, re.S | re.I):
        headings.append(re.sub(r"<[^>]+>", "", hm.group(2)).strip())
    if not headings:
        findings.append("no heading at all")
    if not code_first40:
        findings.append("no code block in the first 40 lines — the first screen must show a command")

    body_text = "\n".join(l for _, l in body)
    no_links = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)", r"\1", body_text)
    words = len(re.findall(r"\b\w+\b", no_links))
    if words > a.max_body_words:
        findings.append(f"body prose is {words} words (> {a.max_body_words}); move depth to docs/")
    if words < a.min_body_words:
        print(f"warning: body prose is {words} words (< {a.min_body_words}); fine for a tiny repo, otherwise the reader will not get context")

    # Anchors, with GitHub's -1, -2 suffixes for duplicate headings.
    anchors, seen = set(), {}
    for h in headings:
        k = gh_anchor(h)
        n = seen.get(k, 0)
        anchors.add(k if n == 0 else f"{k}-{n}")
        seen[k] = n + 1

    def check_target(target: str, where: str):
        target = target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        target = target.replace("\\", "")
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return  # http:, https:, mailto:, tel:, data: …
        if target.startswith("#"):
            if target[1:].lower() not in anchors:
                findings.append(f"{where}: anchor {target} matches no heading")
            return
        file_part = target.split("#")[0].split("?")[0]
        p = (root / file_part.lstrip("/")).resolve() if file_part.startswith("/") else (root / file_part).resolve()
        if not p.exists():
            findings.append(f"{where}: link target does not exist: {target}")

    code_lines = {ln for ln, _ in code}
    noncode = "\n".join("" if i in code_lines else l for i, l in enumerate(lines, 1))  # line numbers preserved
    for rx in (LINK, REF_DEF, HTML_HREF):
        for m in rx.finditer(noncode):
            check_target(m.group(1), f"line {noncode.count(chr(10), 0, m.start()) + 1}")

    # Placeholders: in prose (outside code spans) and inside commands (code blocks).
    for ln, line in body:
        stripped = re.sub(r"`[^`]*`", "", line)
        stripped = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", stripped)
        for m in PLACEHOLDER_TEXT.finditer(stripped):
            findings.append(f"line {ln}: placeholder text {m.group(0)!r}")
        for m in ANGLE.finditer(stripped):
            if is_placeholder(m.group(1)):
                findings.append(f"line {ln}: placeholder {m.group(0)!r} in prose — use a real value")
    for ln, line in code:
        cmd = re.sub(r"\s#.*$", "", line.strip())  # drop a trailing comment
        if not RUNNER.match(cmd):
            continue  # output, file trees and comments may legitimately show <thing>
        for m in ANGLE.finditer(cmd):
            if is_placeholder(m.group(1)):
                findings.append(f"line {ln}: placeholder {m.group(0)!r} in a command — show a realistic argument")

    # Banned words: whole words, prose only, code spans and link targets exempt.
    for ln, line in body:
        stripped = re.sub(r"`[^`]*`", "", line)
        stripped = re.sub(r"\]\([^)]*\)", "]", stripped)
        stripped = re.sub(r"<[^>]+>", "", stripped)
        for w in BANNED:
            for m in re.finditer(rf"(?<![\w-]){re.escape(w)}(?![\w-])", stripped, re.I):
                ctx = stripped[max(0, m.start() - 25):m.end() + 25].strip()
                findings.append(f"line {ln}: banned word {w!r}: …{ctx}…")

    if not any(re.search(r"\blicen[cs]e\b", h, re.I) for h in headings):
        findings.append("no License section (say 'No license yet' if there is no LICENSE file)")

    findings = list(dict.fromkeys(findings))
    if findings:
        print(f"{len(findings)} finding(s) in {path}:")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    print(f"OK — {path}: {len(headings)} headings, {words} body words, links and anchors resolve")


if __name__ == "__main__":
    main()
