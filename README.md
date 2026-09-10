# 📘 GitHub README Writer

### *Read every file, then write the README a stranger can use.*

**A skill for Claude (or any AI agent) that inventories a repository file by file, works out what it offers the end user, and writes a README with real commands, real output, and only the sections that repo needs.**

![Skill](https://img.shields.io/badge/type-agent%20skill-informational) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue) ![Status](https://img.shields.io/badge/status-working-green)

Point it at a folder. It lists every file (nothing sampled; secrets listed but never read), reads them one by one ticking each off, runs the repo's own commands in a scratch copy to capture what they print, picks sections from a 25-item menu, drafts, hands the draft to a second pass that re-runs every command, then lints links, anchors, placeholders and length.

```bash
python3 inventory.py ~/Downloads/idea-research        # writes readme-inventory.md: every file, ticked as you read
python3 lint.py ~/Downloads/idea-research/README.md   # exit 1 on a broken link, bad anchor, placeholder, filler word
```

> Are you the agent running this skill? Read [SKILL.md](SKILL.md) — that is the procedure. This page is for the person deciding whether to use it.

## Table of contents

- [Why](#why)
- [What is in the folder](#what-is-in-the-folder)
- [Use it](#use-it)
- [What a run produces](#what-a-run-produces)
- [The section menu](#the-section-menu)
- [What it is not](#what-it-is-not)
- [Where it came from](#where-it-came-from)
- [License](#license)

## Why

- **Nothing skipped.** `inventory.py` lists every file with size, kind, first line and detected entrypoints; the writer ticks each one. An unticked line is a visible gap.
- **Nothing invented.** Every command in the README was run in a scratch folder during the writing; every output is what it printed. Dependencies come from the imports, not from memory.
- **Reader first.** Before drafting, the writer names the reader, the job they came to do, and the one doubt that would make them leave. Every section serves those three lines.
- **Menu, not template.** 25 possible sections, each with a "use when". A three-file script gets six of them; a framework gets fifteen.
- **Challenged before shipped.** A second, independent pass re-runs the commands and diffs the outputs; `lint.py` then fails on anything a reader would trip over.

## What is in the folder

| File | What it is |
|---|---|
| `SKILL.md` | The procedure, in seven steps: inventory → reader → offer → demo → menu → write → challenge and lint. Plus rules for monorepos, documents-only repos, existing READMEs, secrets and commands that cannot be run, and the anti-pattern list. |
| `inventory.py` | Walks a repo, writes `readme-inventory.md`. Detects `main`s in Python, Node, Go, Rust, Java, Kotlin, C#, C and shell; CLI parsers; npm bin and scripts; Makefile and Justfile targets; Cargo, Go, Maven, Gradle and other manifests; Dockerfiles, CI workflows, env examples, tests, agent instruction files, non-stdlib Python imports. Lists secret files without reading them, symlinks without following them, and vendored folders by name with a file count. |
| `lint.py` | Checks a README: relative links and images exist (markdown, reference-style, HTML), `#anchors` match a heading under GitHub's rule, no unclosed code fence, no `<placeholder>`/TODO in prose or in a command, no filler words in prose, a code block in the first 40 lines, a License heading, body prose within bounds. Every finding carries a line number. |
| `README.md` | This page, written by following `SKILL.md`. |

## Use it

**In Claude (Cowork / Claude Code):** save the skill (the proposal card in the chat, or copy this folder to `~/.claude/skills/github-readme-writer/`), then ask:

```
Write the README for ~/Downloads/idea-research using the github-readme-writer skill.
```

**By hand, in any tool:** run the two scripts and follow `SKILL.md` steps 2–7 yourself.

```bash
python3 inventory.py ~/Downloads/idea-research            # 1. every file, listed
# read the repo, tick every line in readme-inventory.md
# run the repo's own commands in a scratch copy; keep the real output
# pick sections from the menu in SKILL.md; write
python3 lint.py ~/Downloads/idea-research/README.md       # 7. must print OK
```

What `inventory.py` printed for the framework repo next to this one:

```
wrote workflow-studio/readme-inventory.md (66 files listed, 3 folders skipped)
```

and the tail of that file, which is where the writer learns the dependency nobody had written down:

```
## Python imports that are not stdlib (verify each is declared)

`yaml`

Total: 66 files, 1,269,788 bytes listed; 0 symlinks; 3 folders not opened; 0 secret files not read.
```

What `lint.py` printed for that repo's README after the challenge pass:

```
OK — workflow-studio/README.md: 30 headings, 1783 body words, links and anchors resolve
```

and what it prints when something is wrong (a `<name>` placeholder left in a command):

```
1 finding(s) in README.md:
  - line 4: placeholder '<name>' in a command — show a realistic argument
```

## What a run produces

1. `README.md` in the repo.
2. `readme-inventory.md` beside it, every line ticked, and `README.prev.md` if a README existed (delete both before commit if the owner prefers).
3. A short note to the owner: reader, job, files ticked out of total, sections chosen and skipped and why, commands not run and why, anything the README could not honestly claim.

## The section menu

The full table with "use when" is in `SKILL.md` step 5. The short form: hero → demo visual → what it is with the first command → redirect for a second audience → table of contents → why → overview table → flow → install → quickstart → get started step by step with real output → worked example → reference tables → how it works → for AI agents / contributors → supported platforms → customizing → FAQ → prerequisites → what it is not → status → learn more → support → acknowledgements → license. Pick what the repo needs; the order stays.

## What it is not

Not a template generator: it will not produce a README without reading the code. Not a docs site builder: depth beyond ~1,800 words is sent to `docs/`. Not a substitute for running the software: if a command cannot be run, its output is not shown and the README says why. Not a secret scanner: it refuses to read `.env` and key files, but it does not audit the rest of the code for embedded credentials.

## Where it came from

The menu and the rules were distilled from the READMEs of github/spec-kit, astral-sh/uv, fastapi/fastapi, httpie/cli, charmbracelet/gum, BurntSushi/ripgrep, openai/openai-agents-python, anthropics/claude-code and n8n-io/n8n, and from rewriting the README of [workflow-studio](https://github.com/rishabhrawat35/workflow-studio) after the first version was rejected for "showing nothing".

## License

No license yet.
