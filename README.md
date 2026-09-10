# 📘 GitHub README Writer

### *Read every file, then write the README a stranger can use.*

**A skill for Claude (or any AI agent) that inventories a repository file by file, works out what it offers the end user, and writes a README with real commands, real output, and only the sections that repo needs.**

![Skill](https://img.shields.io/badge/type-agent%20skill-informational) ![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13%20tested-blue) ![Status](https://img.shields.io/badge/status-working-green)

**Status:** working, 2026-09-10. No LICENSE file yet.

Point it at a folder. It lists every file, reads each one, runs the repo's own commands in a scratch copy, drafts from a section menu, then a second pass re-runs every command and a linter rejects anything unproven.

```bash
python3 inventory.py ~/Downloads/idea-research        # writes readme-inventory.md: every file, ticked as you read
python3 lint.py ~/Downloads/idea-research/README.md   # exit 1 on a broken link, bad anchor, placeholder, filler word
```

> Are you the agent running this skill? Read [SKILL.md](SKILL.md) — that is the procedure. This page is for the person deciding whether to use it.

## Why

- **Nothing skipped.** [`inventory.py`](inventory.py) lists every file with size, kind, a one-line summary from the file's own words, and detected entrypoints; the writer ticks each one. An unticked line is a visible gap. Secret files are listed but never read.
- **Nothing invented.** Every command in the README was run in a scratch folder during the writing; every output is what it printed. Dependencies come from the imports, not from memory — the `yaml` line in [the run below](#what-does-a-run-look-like) is a dependency nobody had written down. A second pass, defined in [CHALLENGER.md](CHALLENGER.md), re-runs the commands and diffs the outputs; [`lint.py`](lint.py) then fails on anything a reader would trip over.
- **Reader first.** Before drafting, the writer names the reader, the job they came to do, and the one doubt that would make them leave. Every section serves those three lines.

## What is in the folder

| File | What it is |
|---|---|
| [`SKILL.md`](SKILL.md) | The procedure, in seven steps: inventory → reader → offer → demo (and make the screenshots or diagrams if none exist) → menu → write → challenge and lint. The 25-item section menu, each with a "use when", is step 5. Plus rules for monorepos, documents-only repos, existing READMEs, secrets and commands that cannot be run, and the anti-pattern list. |
| [`CHALLENGER.md`](CHALLENGER.md) | The second pass, run in a fresh context: three takeaways, three readers on three clocks, a proof test for every claim, a cut test for every section. Writes `readme-challenge.md`; the writer applies every cut, prove, add and move. |
| [`inventory.py`](inventory.py) | Walks a repo, writes `readme-inventory.md`. Detects `main`s in Python, Node, Go, Rust, Java, Kotlin, C#, C and shell; CLI parsers; npm bin and scripts; Makefile and Justfile targets; Cargo, Go, Maven, Gradle and other manifests; Dockerfiles, CI workflows, env examples, tests, agent instruction files, non-stdlib Python imports. Lists secret files without reading them, symlinks without following them, and vendored folders by name with a file count. |
| [`lint.py`](lint.py) | Checks a README: relative links and images exist (markdown, reference-style, HTML), `#anchors` match a heading under GitHub's rule, no unclosed code fence, no `<placeholder>`/TODO in prose or in a command, no filler words in prose, a code block in the first 40 lines, a License heading, body prose within bounds. Every finding carries a line number. |
| `README.md` | This page, written by following `SKILL.md` and challenged with `CHALLENGER.md`. |

## Use it

**In Claude (Cowork / Claude Code):** save the skill (the proposal card in the chat, or copy this folder to `~/.claude/skills/github-readme-writer/`), then ask:

```
Write the README for ~/Downloads/idea-research using the github-readme-writer skill.
```

**By hand, in any tool:** run the two scripts and follow `SKILL.md` steps 2–7 yourself. Both scripts are Python standard library only; they were run under 3.10, 3.11, 3.12 and 3.13 for this page.

```bash
python3 inventory.py ~/Downloads/idea-research --out ~/Downloads/idea-research/readme-inventory.md
python3 lint.py ~/Downloads/idea-research/README.md --max-body-words 1800 --min-body-words 150
```

| Flag | Script | Default |
|---|---|---|
| `--out PATH` | `inventory.py` | `<repo>/readme-inventory.md` |
| `--max-body-words N` | `lint.py` | 1800 — a finding above it |
| `--min-body-words N` | `lint.py` | 150 — a warning below it |

A run leaves three things behind:

1. `README.md` in the repo.
2. `readme-inventory.md` and `readme-challenge.md` beside it, plus `README.prev.md` if a README existed (delete them before commit if the owner prefers).
3. A short note to the owner: reader, job, files ticked out of total, sections chosen and skipped and why, commands not run and why, anything the README could not honestly claim. That note is where to look when the README is not what you expected.

## What does a run look like?

The repo is [workflow-studio](https://github.com/rishabhrawat35/workflow-studio), cloned next to this folder. Every block below was captured on 2026-09-10.

`inventory.py` printed:

```
wrote workflow-studio/readme-inventory.md (66 files listed, 3 folders skipped)
```

The tail of that file, where the writer learns the dependency nobody had written down:

```
## Python imports that are not stdlib (verify each is declared)

`yaml`

Total: 66 files, 1,281,328 bytes listed; 0 symlinks; 3 folders not opened; 0 secret files not read.
```

`lint.py` on that repo's README after the challenge pass:

```
OK — workflow-studio/README.md: 30 headings, 1783 body words, links and anchors resolve
```

And on a README that left a `<name>` placeholder in a command:

```
1 finding(s) in README.md:
  - line 4: placeholder '<name>' in a command — show a realistic argument
```

## What it is not

Not a template generator: it will not produce a README without reading the code. Not a docs site builder: depth beyond ~1,800 words is sent to `docs/`. Not a substitute for running the software: if a command cannot be run, its output is not shown and the README says why. Not a secret scanner: it refuses to read `.env` and key files, but it does not audit the rest of the code for embedded credentials.

## Where it came from

The menu and the rules were distilled from the READMEs of github/spec-kit, astral-sh/uv, fastapi/fastapi, httpie/cli, charmbracelet/gum, BurntSushi/ripgrep, openai/openai-agents-python, anthropics/claude-code and n8n-io/n8n, and from rewriting the README of [workflow-studio](https://github.com/rishabhrawat35/workflow-studio) after the first version was rejected for "showing nothing".

## License

No license yet.
