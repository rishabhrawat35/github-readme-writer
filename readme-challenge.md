# Challenge pass — github-readme-writer README (2026-09-10)

Done by the writer in a fresh read after finishing the draft (no second agent available); every command was re-run from the scratch copy and its output diffed against the draft.

Takeaways:
1. It reads every file and runs every command before writing, so the README is true on the day it is written.
2. It is two small stdlib-only Python scripts plus two procedure files; trying it costs one command.
3. A second pass and a linter reject anything unproven — it is a filter, not a template.

Scanner lost at: badges — no status/date on the first screen (Status sits at the bottom). / Evaluator lost at: "What is it?" paragraph restates the flow the diagram already shows; 8 sentences before the first command. / Operator lost at: "copy this folder to ~/.claude/skills/…" — not run here, not marked as such.

Re-run check: inventory on workflow-studio → 66 files, 3 folders skipped (matches); tail `yaml` / 1,280,285 bytes (matches); lint OK 24 headings / 1793 words (matches); bad/README.md 6 findings (matches line for line); `--help` for both scripts (matches). Old README's 30 headings / 1783 words / 1,281,328 bytes did not match and were replaced. Inventory: 6/6 ticked. No secret values anywhere. All 5 relative links resolve; the one anchor resolves.

- [move] Status — one line under the badges (menu 34: "always, one line"); drop the Status H2. Serves takeaway 1 for the scanner.
- [cut] "What is it?" — first two sentences only (who, what, what happens after); the step list is derivable from the diagram in "How does a run flow?".
- [cut] Install prose — "and were run under all four versions for this page" is already the badge; keep one clause.
- [prove] "Reader first" bullet — link the three lines as they exist in this repo's own `readme-inventory.md`.
- [prove] "copy this folder to ~/.claude/skills/github-readme-writer/" — not run here; add "Not run while writing this README: needs a Claude session."
- [prove] "14 kinds of entrypoint (… shell)" — the 14 are patterns, not languages, and include web servers; reword to "14 entrypoint patterns" and name web servers.
- [prove] "a 66-file spec framework" — workflow-studio's own README says "ship a product with one PM and one AI"; say that, not "spec framework".
- [add] `readme-inventory.md`, `readme-challenge.md`, `README.prev.md` — link from "What does a run leave behind?" as the artefacts of this very run.
- [add] Bug found while re-running: `inventory.py --out <relative path>` counts its own previous output on a second run (66 → 67). Not a README claim; reported to the owner, script left untouched.
- [keep] Hero — takeaway 1 and 3.
- [keep] Why — takeaway 1 and 3; every bullet links a file or the run below.
- [keep] What is in the folder — takeaway 2; the line counts are what the evaluator uses to judge size.
- [keep] How does a run flow — takeaway 1; gates (grep = 0, lint OK) marked.
- [keep] How do I install and use it — takeaway 2.
- [keep] What does a run look like — takeaway 1; all output re-run today.
- [keep] What does a run leave behind — takeaway 3 (operator knows where to look when the result surprises).
- [keep] What is it not — takeaway 3.
- [keep] Where did it come from — answers "is the menu invented?"; two sentences.
- [keep] License — required.

Skipped from the menu, checked against "use when": 2 Demo visual (CLI — the output blocks are the screenshot), 3 Try without installing (no hosted demo), 6 TOC (11 H2s but the page is two screens; cut test says nothing is lost), 7 At a glance (the numbers already sit in the overview table), 9 Compared to (the Why heading names the alternative), 10 Concepts (no jargon beyond "lint"), 12 Architecture (four files, no data flow between modules), 15 Configuration (no config files; the three flags are in the Install table), 17 Get started step by step (two commands; the worked example covers it), 19 Reference tables (three flags only), 20 How it works (the flow diagram is the mechanism), 21 Tech stack (stdlib only), 22 Data sources (none), 23 Tests (no test suite in the repo — cannot claim one), 24 Safety (no AI-generated output shipped), 25 Troubleshooting (the two refusal messages fit in one line), 26–27 Runtime/Deploy (local, free), 28 For AI agents (the redirect to SKILL.md is the agent's section), 29 Platforms, 30 Customizing, 31 FAQ (no issue tracker), 35 Learn more (no docs/), 36 Support (no public repo URL verifiable from here).

Word budget: draft 830 body words against a 700 cap set by the owner; after the cuts above, lint reports 699. Final lint: OK — README.md: 11 headings, 699 body words, links and anchors resolve.
