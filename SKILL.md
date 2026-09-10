---
name: github-readme-writer
description: 'Writes or rewrites the README of a repository so an end user gets full context in one read: what it is, who it is for, what it does, how to install and use it, with real commands and real output. Walks every file in the folder first (nothing skipped), builds an inventory, then picks only the sections this repo needs from a full menu. Use when someone asks for a README, says the current one "shows nothing", or wants a repo presentable on GitHub.'
license: MIT
metadata:
  tags: "README, Documentation, Developer Experience, GitHub"
  category: "documentation"
---

# GitHub README Writer

Write the README a first-time visitor will actually read to the end, and be able to use the repo afterwards without opening the code.

Ground rules that never change:

- **Inventory before prose.** Every file in the folder is opened and read before one sentence is written; only vendored/generated folders, binaries and secret files are listed without reading. A README that misses a feature is wrong, not short.
- **Nothing unverified.** Every command shown was run; every output shown is what it printed; every path, count and claim was checked in the repo. If it cannot be verified, it is not written.
- **Reader first.** The reader is the end user of the repo, on the repo's GitHub page, with no context. Not the author, not you.
- **Menu, not checklist.** Section 5 lists everything a README *can* contain. Pick what this repo needs. A 300-line README for a 3-file script is a failure; so is a 40-line README for a framework.
- **Never leak, never destroy.** No content of `.env`, keys, tokens or credentials goes into the README or the inventory — only the variable *names*, from `.env.example` or the code. If a real secret file exists, tell the owner; do not print it. Never overwrite an existing README without a copy (`README.prev.md` beside it, deleted by the owner, or a clean git history). Run nothing that deploys, publishes, pushes, deletes or spends money.

## Step 1 — Inventory (do not skip, do not sample)

Run `python3 inventory.py <repo>` (the script sits next to this file; if the skill was installed without its scripts, the folder is `~/Downloads/github-readme-writer/`). It writes `readme-inventory.md` beside the README with every file, its size, type, first heading or docstring, and the entrypoints it detects (Python/Node/Go/Rust/Java/Kotlin/C#/shell `main`s, CLI parsers, `package.json` bin and scripts, Makefile/Justfile targets, Cargo/Go/Maven/Gradle manifests, Dockerfiles, CI workflows, slash-command folders). Secret files are listed but never read; symlinks are listed but not followed. Read that file top to bottom. If Python is unavailable, build the same tick list by hand from `find <repo> -type f`.

Special shapes, decided from the inventory header before reading further:

- **Empty or binaries-only folder:** tell the owner there is nothing to document; stop.
- **Large repo (>1,500 files) or monorepo (workspaces, several manifests):** work top-level folder by top-level folder from the "By top-level folder" map; never sample. A monorepo gets a root README that routes plus one README per package, each a separate run.
- **Documents, not code (`.docx`, `.xlsx`, `.pptx`, `.pdf`):** convert each to text (pandoc, python-docx, openpyxl) and read it like source; the README explains what each document is for, who reads it, and in what order. Skip Install/Quickstart; keep What it is, Overview table, Status, License.
- **Existing README:** read it first, copy it to `README.prev.md` before writing, keep every claim that the code still proves, and note in the owner message which claims were dropped and why.

Then open, in this order, and note what each one offers to the user:

1. Existing README, CONTRIBUTING, CHANGELOG, LICENSE, docs/ — what the author already promised.
2. Every entrypoint the inventory found — what a user can actually run, with which flags. Run each with `--help` or equivalent.
3. Config and templates (`*.yaml`, `*.toml`, `.env.example`, templates/) — what a user is expected to fill in.
4. Source folders, one by one, in inventory order. For each: what it does, for whom, what it produces. Tick it off in the inventory (`- [x]`) only after opening the file — a tick is a claim you read it. Files over 1 MB: open the head, note what it is, tick. Nested READMEs are inputs to the root README and get linked from it. The tick list is the proof that nothing was missed; leave it in `readme-inventory.md` for the next writer, or delete it before commit if the repo owner does not want it.
5. Tests and fixtures — they show the real use cases and the exact expected outputs.
6. Generated or vendored folders (`node_modules`, `build/`, `dist/`, caches) — list, do not read; mention only if the user must know about them.

Stop when every line of the inventory is ticked. Not before. Verify: `grep -c '^- \[ \]' readme-inventory.md` prints `0`; that number goes into the owner note.

## Step 2 — Decide who reads it and what they want

Write three lines at the top of `readme-inventory.md` before drafting (they are copied into the owner note later):

- **Reader:** one sentence. "A PM who never reads code and the AI agent operating the framework." "A data engineer evaluating whether to install this." "My teammate who has to run the trainer next week."
- **Job:** what the reader wants to do in the next ten minutes after landing on the page.
- **Doubt:** the one question that would make them leave. Usually "Does this do X?", "How hard is setup?", or "Is this maintained?"

Everything in the README serves the job and answers the doubt. If a repo has two readers (humans and AI agents; users and contributors), give the second one its own section and a redirect line under the intro, so neither has to read the other's part.

## Step 3 — Extract the offer

From the inventory, write the offer in plain words, as a list you will later turn into sections:

- What it is, in one sentence a stranger understands (name → verb phrase → for whom).
- The 3–7 things it does for the reader, each with the evidence file that proves it.
- What it needs (runtime, versions, dependencies, accounts, keys) — from the code, not from memory. `import yaml` means PyYAML is a dependency even if nobody wrote it down.
- What it deliberately does not do.
- How a user gets from zero to first result, as the exact commands, run by you.

## Step 4 — Run the demo for real

Before writing "Get started", do it in a scratch copy of the repo, never in the repo itself: install, initialise, run the first command, run the most common command, provoke the most common error. Capture the real output. Trim whitespace only. If the tool refuses or errors in a way the user will meet, show that verbatim too — an honest refusal message teaches more than a happy path.

When a command cannot be run here (needs an API key, a network, a GUI, another OS, a paid account) or must not be run (deploys, publishes, pushes, deletes), show the command without an output block and one line after it: "Not run while writing this README: needs X." Say the same in the owner note. Never write output you did not see. For a documents-only repo the demo is opening the main document; show its heading list instead of a terminal output.

Numbers you state (steps, commands, files, test cases) come from a script or a count you ran now, never from an older README.

## Step 5 — The menu

Pick from this list. Order is the order that works for most developer tools; keep it unless the repo has a reason. Every item names the repos where the pattern is strongest, so you can look at them when unsure.

| # | Section | What goes in it | Use when |
|---|---|---|---|
| 1 | **Hero** | H1 (emoji optional), italic one-line tagline, one bold sentence that expands it, 2–4 badges that mean something (version, license, works-with, status). No vanity badges. | Always |
| 2 | **Demo visual** | Screenshot or GIF directly under the badges, before any prose. Show the thing working, not the logo. | Anything with a UI, a terminal UX, or output worth seeing |
| 3 | **What it is** | 2–4 sentences: who, what, what happens after. Then one 2-line code block: the first command a user runs. | Always — a working command in the first screen |
| 4 | **Redirect** | Blockquote: "> Are you X? Jump to [section]." | Two audiences |
| 5 | **Table of contents** | Links to every H2. | More than ~6 H2s |
| 6 | **Why / Highlights** | 5–7 bullets, each a concrete claim the repo backs up. Bold lead-in, one sentence after. | Anything with alternatives |
| 7 | **Overview table** | One table of the repo's main parts: name, what question it answers, size, what you get. | Multi-part systems (workflows, modules, agents, services) |
| 8 | **How it flows** | ASCII arrow line or Mermaid diagram of the main path. | The user must understand an order of operations |
| 9 | **Install** | Per platform / per tool, bold label + code block. Rare paths inside `<details>`. | Anything installed |
| 10 | **Quickstart** | 3–7 numbered lines, **bold verb** + `command`. Fits on one screen. | Always |
| 11 | **Get started, step by step** | One H3 per step, 1–2 sentences of intent, exact command with a realistic argument (a real sentence, not `<thing>`), then the real output. Finish with "what if it refuses / fails". | Anything with more than one step |
| 12 | **Worked example** | One realistic end-to-end case in the reader's domain: what they type at each point, what appears on disk. | Frameworks, pipelines, agents |
| 13 | **Reference tables** | Commands, flags, config keys, steps, files — one table each, complete, generated from the source when possible. Long ones inside `<details>`. | Anything with more than ~5 commands/options |
| 14 | **How it works** | 3–5 plain bullets on the mechanism, then a `<details>` with the file layout tree. No code. | Anything a user might not trust |
| 15 | **For AI agents / For contributors** | Written to that reader: where state lives, what not to do, where the rules are. Link AGENTS.md / CONTRIBUTING.md. | Second audience exists |
| 16 | **Supported platforms / integrations** | Table: platform, how to install, how to invoke. | Multi-tool support |
| 17 | **Customizing** | `Goal → Edit this → Then run` table. | Anything configurable |
| 18 | **FAQ** | 3–6 real questions (from issues, from the doubt in Step 2). Never restate the Why bullets. | Recurring questions exist |
| 19 | **Prerequisites** | Exact runtime versions and dependencies, from the code. | Always, short |
| 20 | **What it is not** | 2–4 honest limits. | Always for tools; skip for pure docs repos |
| 21 | **Status / Roadmap** | One line: working / beta / archived, date, what is next. | Always, one line |
| 22 | **Learn more** | Links to deeper docs in the repo. | docs/ exists |
| 23 | **Support / Contributing** | Where to ask, where to file; link the file rather than inlining rules. | Public repos |
| 24 | **Acknowledgements** | Name what you borrowed from. | You borrowed |
| 25 | **License** | One line. If no LICENSE file exists, say "No license yet" — do not invent one. | Always, last |

Repos that do these well, for reference when a section feels off: github/spec-kit (get-started steps with real prompts; command tables split core/optional; quickstart as bold-verb list), astral-sh/uv (highlights with concrete claims; FAQ), fastapi/fastapi (run it → check it, with output), httpie/cli and charmbracelet/gum (demo GIF first; one section per command), BurntSushi/ripgrep ("why should I" *and* "why shouldn't I"), openai/openai-agents-python (code → **Output:** block; redirect blockquote), anthropics/claude-code (whole README under 80 lines when the docs live elsewhere).

## Step 6 — Write

- Length: body prose 600–1,800 words for a tool or framework; a 3-file script or a documents-only repo may go down to the lint floor of 150. Tables and code blocks do not count. Deep material goes to `docs/` and gets a link.
- The first 50 words answer what, why different, for whom. A command appears before the first scroll.
- Sentences are short. No adjectives that cannot be checked ("powerful", "seamless", "robust"). No "simply", "just", "easy".
- One idea per section. If two sections say the same thing, delete one.
- Realistic arguments in every command (`/speckit-specify Refund within 7 days for unused policies`, not `/speckit-specify <feature>`).
- Every relative link and image path exists. Every TOC anchor matches GitHub's rule (lowercase, spaces → `-`, punctuation and emoji stripped, one leading `-` if the heading started with an emoji).
- Emoji on H2 only, or nowhere. Never in body text.
- The reader from Step 2 must be able to complete the job from Step 2 using only the README. Read it once as that person.

## Step 7 — Challenge, then lint

Hand the draft to a second, independent pass (a fresh agent or a fresh context; if neither exists, re-open the inventory and do the pass yourself after finishing the draft, and say so in the owner note) with the inventory and this instruction: *re-run every command, diff every output, check every count, path, link and anchor, check that no secret value appears, flag every sentence a first-time reader would not understand, flag anything derivable from something already said.* Fix every confirmed finding. Then run `python3 lint.py <repo>/README.md` (next to this file): it fails on broken relative links and images (markdown, reference-style and HTML), anchors that match no heading, an unclosed code fence, placeholders in prose or in commands (`<thing>`, TODO, lorem), banned words, a missing first-screen code block, a missing License heading, and prose over 1,800 words (under 150 is a warning).

Do not ship a README that has not been through both.

## Anti-patterns (each one seen in a real repo)

- Listing folders instead of explaining what the user can do ("`src/` — source code").
- Commands without output; output nobody ran.
- Installation sprawl: twenty platforms uncollapsed, quick examples buried underneath.
- Contributor build steps mixed into end-user steps.
- Feature claims copied from an older README the code has outgrown (a count of tests, a version, a dependency).
- A product screenshot standing in for a mechanism explanation, or a mechanism explanation where a screenshot would do.
- FAQ that restates the Why bullets.
- No limits section, so the reader discovers the limit after installing.
- A README that is the only documentation and therefore 4,000 words long.
- A real value from `.env` (a key, a hostname, a password) pasted as the "example".

## Outputs of one run

1. `README.md` — the deliverable.
2. `readme-inventory.md` — the ticked inventory with the three Step 2 lines on top (keep or delete per repo owner's wish; never commit it half-ticked). `README.prev.md` if a README existed.
3. A short note to the owner: reader, job, doubt; files ticked / total; sections chosen and why, sections skipped and why; commands not run and why; claims from the old README that were dropped; anything in the repo the README could not honestly claim; whether the challenge pass was a second agent or yourself.
