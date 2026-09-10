# Challenge notes for the github-readme-writer README (2026-09-10)

Round: 3 of 3. Round 1 (independent Challenger) reported 6 must-fix and 14 should-fix findings plus two on the scripts and run files; round 2 (independent Challenger) reported 1 must-fix and 5 should-fix findings. This file records the writer's response to every finding and the writer's self-check of the round-3 draft.

Takeaways:
1. Every file is read and every command is run before the README is written, so the README is true on the day it is written.
2. The skill is two standard-library Python scripts and two procedure files; trying it costs one command.
3. A second review and a checker reject anything unproven, so the output is filtered rather than templated.

Scanner lost at: nothing; the title, tagline, bold sentence and status line state what it is, who it is for and whether it is maintained. / Evaluator lost at: nothing; the key features and the file table answer why this rather than a template, and the first code block shows the cost of trying. / Operator lost at: the Installation in Claude step, which cannot be run here and is marked "Not run while writing this README".

Verification: every command in the README was re-run from a scratch folder holding a copy of this skill and a copy of workflow-studio side by side, and each output block sits directly under the command that produced it. `python3 github-readme-writer/inventory.py workflow-studio` printed 66 files listed and 3 folders skipped; `sed -n 5,11p` and `grep -A2` on the resulting checklist printed the folder map and the `yaml` section quoted; `python3 github-readme-writer/lint.py workflow-studio/README.md` printed 24 headings and 1793 body words; `cat -n bad/README.md` and `python3 github-readme-writer/lint.py bad/README.md` printed the seven-line file and the six findings quoted, line for line; the three error messages were provoked and match the table. Counts checked in the scripts: 28 banned words, 29 manifest types, ten languages in the entry-point patterns (Python, JavaScript and TypeScript, Go, Rust, Java, Kotlin, C#, C and C++, Ruby, shell); 38 menu rows and seven step headings in SKILL.md; ten criteria and nine rule labels in CHALLENGER.md. All ten relative links (seven targets) and the one anchor resolve; the GitHub link is verified by the owner. No secret value appears in any file. Python 3.11.15 was the only interpreter run.

## Response to the round-1 findings

Must-fix findings, all applied:
- [prove] (must-fix, A8) 1 — The workflow-studio link is restored with the owner's verification, and "which sits next to this folder" is removed.
- [cut] (must-fix, A2, A5) 2 — The self-justifying clause is removed; the status line now reads "The skill works as described here and was last verified on 2026-09-10."
- [reword] (must-fix, A10) 3 — The diagram uses the SKILL.md step headings verbatim, and SKILL.md Step 6 is renamed "Write the draft under the writing rules".
- [reword] (must-fix, A1, A10) 15 — Menu row 14 now prescribes an H3 heading per platform and row 16 a full sentence per line.
- [reword] (must-fix, A10) 16 — Step 7 defines a round, a must-fix finding, the review-fix-lint order, the three-round cap and the outcome of a third failing round, matching CHALLENGER.md.
- [reword] (must-fix, A10) 25 — CHALLENGER.md defines must-fix against A1 to A10, and the output template carries the severity and criterion on each finding line and on the count line.

Should-fix findings applied:
- 4 — The tagline is a full sentence.
- 5, 6 — Each output block follows the command that produced it, run from a folder holding both repositories.
- 7 — The seven-line README appears in a `<details>` block, shown as the output of `cat -n bad/README.md` because the checker would otherwise flag the example's own placeholder as a fault in this README.
- 8, 10 — Both Purpose cells are one sentence; the detection categories moved to the list "What the inventory detects".
- 9 — "`main` functions in ten languages" became "entry points in ten languages", counted from the patterns.
- 11 — "from Step 2 onward" became "from the point where the reader and goal are defined".
- 12 — The owner-note item now includes who performed the second review.
- 13 — "distilled" and the workflow-studio anecdote are cut; the sentence names the eight projects.
- 14 — Python is stated as "3.10 or later (verified on 3.11)" and the badge reads "3.10+".
- 17 — The screenshots sub-step is folded into Step 4 as a sub-heading; SKILL.md has seven numbered steps and the README diagram has seven step nodes.
- 18 — Ground rule 5 now reads "The nine writing rules in Step 6 each carry a test and a fails/passes pair."
- 20 — "The inventory decides four special cases".
- 21 — Step 4 states that only the repository's own commands run in a scratch copy and names the four files written beside the code.
- 22 — Rule R9's passing example names the inventory script and 66 files.
- 23, 26 — SKILL.md rules are labelled R1 to R9 and CHALLENGER.md's table runs to R9. R7 remains Length so that R1 to R7 match RULES.md; R8 is Reader benefit and R9 is Numbers and single actions.
- 24 — Menu rows are cited as "(Step 5, row 2)" and "(Step 5, row 12)" on first use.
- 27 — The three clock cells are sentences.
- 28 — inventory.py no longer prints a byte size per file or a byte total; the large-file note remains. The inventory of this folder was regenerated afterwards.
- 29 — This file no longer records the link as unverifiable.

Should-fix finding rejected:
- 19 — The `~/Downloads/github-readme-writer/` fallback stays because the owner instructed the writer to keep that path in Step 1; the suggested sentence is appended after it, so an agent that finds neither location asks the owner.

Owner note on menu row 36 (Support and contributing): the verified GitHub URL belongs to the sample repository, not to this skill, and this skill has no public repository URL, so the row stays skipped.

## Response to the round-2 findings

- [restructure] (must-fix, A1) 1 — Applied. The seven detection bullets are replaced by the table "Detected item | Examples" exactly as given; body prose fell from 892 to 830 words.
- 2 — Applied. `bad/README.md` is introduced as saved in the same folder before its first use.
- 3 — Applied. Step 4 now lists `docs/` images among the files written beside the code.
- 4 — Applied. The four commands of Step 4 are a numbered list.
- 5 — Applied. The Step 7 round is a numbered list of three actions, and the "Rounds repeat" sentence is its own paragraph.
- 6 — Applied. This file now states ten relative links across seven targets.

## Round-3 self-check against the criteria

- A1 pass — the tagline, every bullet, every prose table cell and every bold lead-in is a full sentence; the seven detection bullets became a two-column table whose cells are terms and examples.
- A2 pass — no casual opener, no question heading, and the checker reports no banned word.
- A3 pass — the reader is "anyone opening a repository for the first time" throughout.
- A4 pass — the four files, two scripts, seven detected items, three flags, five features, five limits, two error cases and three leftover files are each a list or table; in SKILL.md the four Step 4 commands and the three actions of a review round are numbered lists.
- A5 pass — the file table serves "which file do I open first"; the script table serves "can I script this"; the flag table serves "what do I type"; the message table serves "what did I do wrong"; the numbers 66, 3, 48, 24, 1793, 11, 6, 7, 28, 29, 38, ten and 1,800 were each counted in this run; the date serves "is this maintained?"; no byte size remains anywhere.
- A6 pass — every heading is a noun phrase and every diagram label is a SKILL.md step heading.
- A7 pass — inventory.py and lint.py are introduced by the sentence before the first code block; CHALLENGER.md, SKILL.md, workflow-studio and `bad/README.md` are introduced in the sentence where they first appear.
- A8 pass — `python3 lint.py README.md` printed "OK — README.md: 16 headings, 830 body words; every link and anchor resolves."
- A9 pass — body prose is 830 words.
- A10 pass — SKILL.md Step 4 names `docs/` images among the files written beside the code, matching its own sub-heading; SKILL.md has seven steps, 38 rows and rules R1 to R9; CHALLENGER.md tests R1 to R9 and scores A1 to A10 with a three-round cap; README.md repeats the step names, the seven-step count, the file names and the script messages; readme-inventory.md was regenerated after the last script edit.

Must-fix findings: 0, by the writer's self-check of round 3.
