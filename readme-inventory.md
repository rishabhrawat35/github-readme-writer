# Inventory of `github-readme-writer`

Tick every line after reading the file. An unticked line is a gap in the README.

- **Reader:** anyone opening this repository for the first time, plus the AI agent that will run the skill, which is redirected to SKILL.md.
- **Goal:** within ten minutes, know what the skill does, what trying it costs, and run the two scripts on one of their own repositories.
- **Doubt:** "Will this produce a README that is true about my repository, or another template?"

## Every file in the repository

- [x] `CHALLENGER.md` (text) — README Challenger
- [x] `inventory.py` (text) — Walk a repository and write readme-inventory.md, a checklist that lists every file. — python script (`python3 inventory.py`); CLI with flags; run it with --help; has main(); reads sys.argv; executable script (shebang)
- [x] `lint.py` (text) — Check a README against the github-readme-writer rules; exit 1 on any finding. — python script (`python3 lint.py`); CLI with flags; run it with --help; has main(); executable script (shebang)
- [x] `readme-challenge.md` (text) — Challenge notes for the github-readme-writer README (2026-09-10)
- [x] `README.md` (text) — GitHub README Writer — existing README of 1696 words; keep a copy before rewriting
- [x] `README.prev.md` (text) — 📘 GitHub README Writer
- [x] `SKILL.md` (text) — Writes or rewrites the README of a repository so an end user gets full context in one read: what it is, who it — agent instructions

## Vendored and generated folders, listed but not opened

- none

## Python imports outside the standard library (verify that each is declared as a dependency)

none

Total: 7 files listed; 0 symlinks; 0 folders not opened; 0 secret files not read.
