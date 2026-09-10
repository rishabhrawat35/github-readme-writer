# Inventory of `github-readme-writer`

Tick every line as you read the file. An unticked line is a gap in the README.

- **Reader:** a developer or PM deciding whether to install this skill for their repos, plus the AI agent that will run it (redirected to SKILL.md).
- **Job:** in ten minutes, know what the skill does, what it costs to try, and run the two scripts on one of their own repos.
- **Doubt:** "Will this produce a README that is actually true about my repo, or another template?"

## Files

- [x] `CHALLENGER.md` (2,898 B, text) — README Challenger
- [x] `inventory.py` (19,338 B, text) — Walk a repository and write readme-inventory.md: every file, nothing skipped. — python script (`python3 inventory.py`); CLI with flags — run with --help; has main(); reads sys.argv; executable script (shebang)
- [x] `lint.py` (9,519 B, text) — Lint a README against the github-readme-writer rules. Exit 1 on any finding. — python script (`python3 lint.py`); CLI with flags — run with --help; has main(); executable script (shebang)
- [x] `README.md` (7,004 B, text) — 📘 GitHub README Writer — existing README, 1042 words — keep a copy before rewriting
- [x] `README.prev.md` (7,004 B, text) — 📘 GitHub README Writer
- [x] `SKILL.md` (20,223 B, text) — Writes or rewrites the README of a repository so an end user gets full context in one read: what it is, who it — agent instructions

## Not opened (vendored / generated)

- none

## Python imports that are not stdlib (verify each is declared)

none

Total: 6 files, 65,986 bytes listed; 0 symlinks; 0 folders not opened; 0 secret files not read.
