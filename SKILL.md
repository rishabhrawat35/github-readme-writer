---
name: github-readme-writer
description: 'Writes or rewrites the README of a repository so an end user gets full context in one read: what it is, who it is for, what it does, how to install and use it, with real commands and real output. Walks every file in the folder first (nothing skipped), builds an inventory, then picks only the sections this repo needs from a full menu. Use when someone asks for a README, says the current one "shows nothing", or wants a repo presentable on GitHub.'
metadata:
  tags: "README, Documentation, Developer Experience, GitHub"
  category: "documentation"
---

# GitHub README Writer

**Version 1.1.0** · 1.0.0 is the commit that introduced R1 to R9 and A1 to A10. Keep this in step with the account skill's description, which is the only version the desktop app shows. Bump patch for wording, minor for a new rule or criterion, major for a change to the seven steps.

This skill produces a README that a first-time visitor can act on without opening the code, in seven numbered steps.

## Ground rules

1. **Every file is read before any prose is written.** Vendored and generated folders, binaries and secret files are listed without being read; a README that omits a feature is wrong, not short.
2. **Nothing unverified appears in the README.** Every command shown was run, every output shown is what it printed, and every path, count and claim was checked during this run.
3. **The reader is anyone opening the repository for the first time.** The audience is narrowed only when the repository is built for one group alone, and the README states why.
4. **The section menu in Step 5 is a menu, not a checklist.** A typical tool uses 10 to 14 of its 38 rows.
5. **The ten writing rules in Step 6 each carry a test and a fails/passes pair.**
6. **No secret is leaked and nothing is destroyed.** Only variable names from `.env.example` or the code appear in the README; an existing README is copied to `README.prev.md` before it is overwritten; nothing that deploys, publishes, pushes, deletes or spends money is run.

## Step 1 — Inventory every file in the repository

`inventory.py` is the script that walks a repository and writes a checklist of every file. It sits next to this file; if the skill was installed without its scripts, the folder is `~/Downloads/github-readme-writer/`, and if it is not there either, ask the owner for the skill folder before proceeding. `python3 inventory.py <repo>` writes `readme-inventory.md` beside the README with, for each file, the path, kind, first heading or docstring, and the entry points, manifests and scripts it detects. Secret files are listed but never read; symbolic links are listed but not followed. Without Python, the checklist comes from `find <repo> -type f`.

The inventory decides four special cases before any file is read:

Repository shape | Action
---|---
Empty folder, or binaries only | Tell the owner there is nothing to document and stop.
More than 1,500 files, or a monorepo | Work one top-level folder at a time from the "File count by top-level folder" map; never sample. A monorepo receives a routing root README plus one README per package.
Documents rather than code (`.docx`, `.xlsx`, `.pptx`, `.pdf`) | Convert each to text and read it as source. The README states what each document is for, who reads it and in what order; Installation and Quickstart are skipped.
An existing README | Copy it to `README.prev.md`, keep every claim the code still proves, and list each dropped claim in the owner note.

Files are then opened in this order:

1. The existing README, CONTRIBUTING, CHANGELOG, LICENSE and `docs/`, which show what the author promised.
2. Every entry point the inventory found, run with `--help`.
3. Configuration files and templates, which show what a user must fill in.
4. Source folders in inventory order. A line is ticked (`- [x]`) only after the file is opened; files over 1 MB are opened at the head. Nested READMEs are linked from the root README.
5. Tests and fixtures, which show the real use cases and expected outputs.
6. Generated and vendored folders, which are listed but not read.

The step ends when `grep -c '^- \[ \]' readme-inventory.md` prints `0`; that count goes into the owner note.

## Step 2 — Define the target reader and their goal

Three lines open `readme-inventory.md` and are copied into the owner note:

- **Reader:** one sentence names the reader, by default "anyone opening the repository for the first time".
- **Goal:** one sentence states what the reader wants to do in the ten minutes after landing on the page.
- **Doubt:** one sentence states the question that would make the reader leave, usually "Does this do X?", "How hard is setup?" or "Is this maintained?"

Every section serves the goal or answers the doubt. A second reader (AI agents, contributors) receives its own section and a redirect line under the introduction.

## Step 3 — State what the repository offers

The offer is written as a list that later becomes sections:

- One sentence a stranger understands (name, verb phrase, for whom) states what the repository does that the alternatives do not.
- Three to seven lines state what it does for the reader, each with the file that proves it.
- One line states what it needs (runtime, versions, dependencies, accounts, keys), taken from the code, since `import yaml` makes PyYAML a dependency even when nothing declares it.
- One line states what it deliberately does not do.
- The exact commands take a user from nothing to a first result.

## Step 4 — Run the commands and capture real output

The repository's own commands are run in a scratch copy, never in the repository itself; only `readme-inventory.md`, `README.md`, `README.prev.md` and `readme-challenge.md`, plus any image produced under `docs/`, are written beside the code. The output is captured with only whitespace trimmed; a refusal or error the user will meet is shown verbatim. The commands are:

1. Install.
2. Run the first command.
3. Run the most common command.
4. Provoke the most common error.

A command that cannot be run here (it needs a key, a network, a GUI, another OS or a paid account) or must not be run (it deploys, publishes, pushes or deletes) is shown without output, followed by one line: "Not run while writing this README: needs X." The owner note repeats this. For a documents-only repository the demonstration is the main document's heading list.

### Screenshots and diagrams

When no usable image of something visible exists, one is produced, saved under `docs/` (PNG for stills, GIF under 5 MB for motion) and referenced by relative path:

Subject | Visual to produce
---|---
Web UI or HTML output | A headless-browser screenshot of the main view at 1440 by 900.
CLI or TUI | A fenced code block with the real output; an image only when colour or layout carries meaning.
Pipeline, state machine or multi-step flow | A Mermaid diagram generated from the source, with every label a noun phrase understood on its own.
Documents-only repository | A table of the documents in reading order.
Library or pure API | No image; the demo row of the menu (Step 5, row 2) is skipped.
Architecture (Step 5, row 12) | A Mermaid diagram whose boxes are the top-level modules and whose arrows are the imports the inventory found.

Every image carries alt text stating what it shows and is regenerated when its subject changes.

## Step 5 — Select sections from the menu

The order below suits most developer tools.

Row | Section | Content | When it is used
---|---|---|---
1 | **Hero block** | The H1, an italic tagline stating what this does that alternatives do not, one bold sentence expanding it, and two to four informative badges. | Every README.
2 | **Demo screenshot or recording** | A screenshot or GIF under the badges, before any prose, showing the tool working. | A UI, terminal experience or visible output exists.
3 | **Hosted demo** | A link to a hosted instance or notebook, with one line on what to type first. | A live instance exists.
4 | **Purpose and first command** | Two to four sentences on who it is for and what it does, then a code block with the first command. | Every README.
5 | **Audience redirect** | A blockquote that sends the second reader to their section. | Two audiences exist.
6 | **Table of contents** | Links to every H2. | More than six H2 headings exist.
7 | **Key numbers** | One table of numbers that prove the project is real, each counted during this run. | Such numbers exist.
8 | **Key features** | Five to seven bullets, each a bold lead-in sentence and one sentence of evidence. | Alternatives exist.
9 | **Comparison with alternatives** | A table of this tool against what the reader uses today; rows are user outcomes. | An obvious alternative exists.
10 | **Glossary of terms** | A table of the five to ten terms the reader may not know, one line each. | The domain has jargon.
11 | **Overview table** | One table of the main parts: name, purpose, what it produces. | The system has several parts.
12 | **Architecture** | The Step 4 diagram plus one paragraph on where the work happens. | More than one moving part exists.
13 | **Main path of a run** | A diagram of the path a request takes, with gates marked. | An order of operations matters.
14 | **Installation** | One H3 heading and one code block per platform; rare paths inside `<details>`. | Anything is installed.
15 | **Configuration** | A table of every setting: name, effect, default, source. Values are never shown. | Configuration files or CLI flags exist.
16 | **Quickstart** | Three to seven numbered lines, each a full sentence starting with the action and followed by its command. | Every README.
17 | **Step-by-step walkthrough** | One H3 per step with its intent, a command with a realistic argument, and its real output; the last step covers failure. | More than one step exists.
18 | **Worked example** | One end-to-end case in the reader's domain, plus three to six inputs the reader can paste. | The repository is a framework, pipeline or agent.
19 | **Reference tables** | One complete table each for commands, flags, keys, steps and files; long tables inside `<details>`. | More than five commands or options exist.
20 | **How it works** | Three to five bullets on the mechanism, then the file layout inside `<details>`. | The reader may not trust the tool.
21 | **Technology stack** | A table of each tool, its responsibility and one verifiable reason for the choice. | More than three dependencies exist.
22 | **Data sources** | Origin, licence, fetch date and refresh method for the data or models. | The repository ships or downloads data.
23 | **Tests and evaluation** | The command, the real result, and one line per metric on its meaning. | Tests or an evaluation script exist.
24 | **Safety and responsible use** | What the tool refuses, what it must not be used for, and how AI output is checked. | The domain is sensitive or AI output is produced.
25 | **Troubleshooting** | A table of symptom, cause and fix from the errors met in Step 4. | Setup or external services exist.
26 | **Runtime and cost** | Where computation happens, what needs a key or network, and the cost per run. | Paid APIs, GPUs or hosted services are used.
27 | **Deployment** | The one supported way to host the tool and what to set there. | The repository is meant to be hosted.
28 | **For AI agents, or For contributors** | Where state lives, what not to do, where the rules are, and the code reading order. | A second audience exists.
29 | **Supported platforms and integrations** | A table of platform, installation and invocation. | Several platforms are supported.
30 | **Customization table** | A table of goal, file to edit, and command to run afterwards. | The tool is configurable.
31 | **Frequently asked questions** | Three to six real questions that do not restate the key features. | Recurring questions exist.
32 | **Prerequisites** | The exact runtime versions and dependencies, taken from the code. | Every README, kept short.
33 | **Limits and non-goals** | Two to five honest limits. | Every tool.
34 | **Status and roadmap** | One line stating working, beta or archived, with the date checked; the date answers "is this maintained?". | Every README.
35 | **Further documentation** | Links to the deeper documents in the repository. | `docs/` exists.
36 | **Support and contributing** | Where to ask and where to file, with the rules file linked. | The repository is public.
37 | **Acknowledgements** | The sources the project borrowed from. | Something was borrowed.
38 | **License** | One line; "No license yet" when no LICENSE file exists. | Every README, last.

Interview questions and "learning outcomes" sections are rejected because they serve the author, not the reader. The owner is told to set the repository description, topics and social-preview image, which a link shows before the README.

## Step 6 — Write the draft under the writing rules

Each rule carries a test and an example pair. CHALLENGER.md tests the rules under the same labels, R1 to R10.

1. **R1 The register is professional.** Test: every sentence, bullet, label, prose table cell and bold lead-in has a subject and a verb; no heading is a question; no sentence is true of every repository; no opener is casual.
   Fails: "Nothing skipped." and "Why this and not a template?"
   Passes: "Every file is read before writing begins." and "Differences from a README template"
2. **R2 The reader is anyone opening the repository for the first time.** Test: a narrower group is named only when the inventory shows the repository is built for that group alone.
   Fails: "a README a developer or PM can use"
   Passes: "a README anyone opening the repository for the first time can use"
3. **R3 Parallel items are structured.** Test: three or more parallel items form a list or table; items with sub-parts form a nested list or a table with one column per part; no paragraph exceeds four sentences.
   Fails: three sentences in a row, one per script.
   Passes: a table with the columns Script, Purpose, Output and Exit status.
4. **R4 Every element passes the value test.** Test: the reader would decide or act differently without it. File sizes, line counts, byte totals and "checked on" dates fail unless they answer a stated doubt.
   Fails: a Size column reading "181 lines".
   Passes: a Status line with a date, because the date answers "is this maintained?"
5. **R5 Names are understood alone.** Test: the heading, step name, diagram label or bold lead-in is read out of context and still states its content; a noun phrase is preferred to a question.
   Fails: "Decide who reads it"
   Passes: "Define the target reader and their goal"
6. **R6 Terms are introduced before use.** Test: the file name, command or term is covered and the preceding sentence still tells the reader what it does.
   Fails: "`lint.py` exits 1 on broken links."
   Passes: "`lint.py` is the checker that rejects a README with a broken link; it exits 1 on the first finding."
7. **R7 Each concept is explained once.** Test: a term receives one plain line on first use; a concept covered in SKILL.md is linked from the README, not repeated. The README body is 400 to 900 words for a small tool and never more than 1,800.
   Fails: a purpose paragraph that restates the flow diagram.
   Passes: "The seven steps are listed in [SKILL.md](SKILL.md)."
8. **R8 Each sentence states what the reader gets or does.** Test: the sentence answers "what do I get?" or "what do I do?"; a sentence that only describes machinery is cut, and internal terms ("Step 4") stay out of the README.
   Fails: "Step 1 ends only when the grep count prints 0."
   Passes: "The README is written only after every file on the checklist has been read."
9. **R9 Numbers replace adjectives, and every step is one action.** Test: a claim carries a count made during this run; a command carries a realistic argument (`~/Downloads/my-repo`, not `<path>`) and its output where it was run.
   Fails: "a fast and thorough checker"
   Passes: "The inventory script lists 66 files in under one second."
10. **R10 No AI tell survives a judgment read.** Test: each sentence is read once against the thirteen tells below, none of which a script decides. A tell a careful writer might have chosen on purpose counts only where several share a passage, and the word list and the fixed constructions are `lint.py`'s work rather than this rule's. The rule cuts:
    - a staged run-up before the point
    - an argument with an objection nobody raised
    - a triad that arrives because three sounds complete
    - a qualifier stacked on a qualifier
    - a hyphenated pair kept after the noun it modifies
    - a passive that hides who acts
    - a vague "associated with" in place of the real relationship
    - an -ing rider bolted onto a fact
    - a sales sentence
    - an unnamed expert
    - a send-off paragraph promising a future
    - a sentence describing what the previous README said
    - bold on a phrase that is not a lead-in stating its own content

    Fails: "The inventory script lists every file in the repository as a checklist, ensuring nothing is skipped."
    Passes: "The inventory script lists every file in the repository as a checklist, and the writer ticks each line only after opening the file."

Form rules: the first 50 words state what the tool is, what makes it different and for whom; a command appears before the first scroll; emoji appear on H2 headings only or nowhere. The final read is done as the reader from Step 2: every sentence that reader would skip is cut, and every sentence that reader would re-read is rewritten.

## Step 7 — Second review and lint check

`CHALLENGER.md`, the file next to this one, lists the review tests and the acceptance criteria A1 to A11. The draft goes to a second, independent pass in a fresh context with the repository, the inventory and that file; when no fresh context exists, the writer performs the pass after finishing the draft and says so in the owner note. The pass re-runs every command, checks every count, path, link and anchor, confirms that no secret value appears, scores the draft against A1 to A11, and writes `readme-challenge.md` beside the README. One round consists of three actions:

1. The reviewer scores the draft against A1 to A11 and writes `readme-challenge.md`.
2. The writer applies every must-fix finding (one that makes any of A1 to A11 false) and applies or rejects each should-fix finding with a reason in the owner note.
3. The writer runs `lint.py`.

Rounds repeat until a round reports zero must-fix findings, for at most three rounds; after a third failing round the open criteria go into the owner note and the README does not ship.

`lint.py` is the checker that runs after the review: `python3 lint.py <repo>/README.md`. It fails on the faults its docstring lists: broken links and images, anchors that match no heading, an unclosed code fence, placeholders, filler words, a missing first-screen command or License heading, and body prose over 1,800 words. It also fails on eight of the nine mechanical AI tells taken from blader/humanizer: a staged "not just X, it is Y" contrast (NOTXBUTY), an AI vocabulary word (AIWORD), an inflated-significance phrase (INFLATED), "serves as" where "is" would do (COPULA), an em dash, en dash or spaced double hyphen outside code (DASH), chat residue such as "Great question" (RESIDUE), three sentences in a row opening on the same content word (OPENER), and a one-line paragraph that restates the heading above it (HEADECHO). Curly quotation marks (CURLY) are the ninth and are advisory: the checker prints them as a note and the run still passes, because most editors curl a quote by themselves. R10 above carries the thirteen tells no script decides, which are the humanizer patterns these nine checks leave alone rather than the judgment half of the nine. A README ships only after both passes.

## Outputs of one run

1. `README.md` is the deliverable, with `README.prev.md` beside it when a README existed.
2. `readme-inventory.md` is the ticked inventory with the three Step 2 lines on top, kept or deleted at the owner's wish and never committed half-ticked.
3. `readme-challenge.md` is the second pass's findings and A1 to A11 score, kept or deleted on the same rule.
4. The owner note states the reader, goal and doubt; files ticked out of the total; sections chosen and skipped, with reasons; commands not run; claims dropped from the old README; and whether the review was a second agent or the writer.
