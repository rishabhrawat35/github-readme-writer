# README Challenger

This file directs the second review of a README draft. The reviewer works in a fresh context with the repository, the inventory and this file, and does not see the writer's reasoning. The reviewer cuts, proves and reorders; the reviewer does not add sections for completeness. The review runs after the draft and before `lint.py`, the checker described in SKILL.md Step 7.

## Content tests (R1 to R10)

The labels match the ten writing rules in SKILL.md Step 6. Each test is applied to every sentence of the draft, including bullets, labels, table cells and bold lead-ins.

| Test | What the reviewer checks | Finding type |
|---|---|---|
| R1 Professional register | Every sentence has a subject and a verb. No bullet, label or bold lead-in is a fragment. No opener is casual ("Point it at a folder", "Just run"). No heading is a rhetorical question. No adjective is unverifiable, and no sentence would be true of any repository. | `[reword]` |
| R2 Audience | The reader is "anyone opening the repository for the first time" unless the repository is built for one group alone and the README says so. | `[reword]` |
| R3 Structure over prose | Three or more parallel items appear as a list or table. Items with sub-parts appear as a nested list or a table with one column per part. No paragraph exceeds four sentences or carries more than one idea. | `[restructure]` |
| R4 Value test | Every line, table column, number and image changes what the reader would decide or do. File sizes, line counts, byte totals and "checked on" dates fail unless they answer a doubt the README states. The reviewer names the reader decision each column and number serves. | `[cut]` |
| R5 Self-explanatory names | Every heading, step name, diagram label and bold lead-in states its content when read alone. Noun phrases are preferred to questions. | `[reword]` |
| R6 Terms before use | Every file name, command and invented term follows a sentence that states its purpose. | `[reword]` |
| R7 Length | No concept explained in SKILL.md is re-explained in the README. Body prose is 400 to 900 words for a tool of this size. | `[cut]` |
| R8 Reader benefit | Every sentence states what the reader gets or does; a sentence that only describes machinery is cut, and internal step names stay out of the README. | `[cut]` |
| R9 Numbers and single actions | Every claim carries a count made during this run; every step is one action with a realistic argument and, where run, its output. | `[prove]` |
| R10 Judgment tells | No sentence carries one of the thirteen judgment tells listed under this table. A tell a careful writer might have chosen on purpose counts only where several share a passage. The word list and the fixed constructions are left to `lint.py`. | `[reword]` |

### The thirteen judgment tells of R10

The reviewer reads each sentence once against this list, which is rule R10 of SKILL.md Step 6. No script decides any of them, and `lint.py` holds the word list and the fixed constructions. The reviewer reports:

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

A tell in the draft is reported as `[reword]` with the replacement sentence, in the form the Output section below gives.

## Reader tests

### The three takeaways

The reviewer writes the three things a reader must know after reading, deriving them from the repository if the writer did not state them. Every section is then assigned to the takeaway it serves. A section that serves no takeaway is cut; a takeaway with no section is a gap.

### Three readers on three clocks

| Reader | Time budget | What must be true when the clock stops |
|---|---|---|
| Scanner | 10 seconds, covering the title, tagline, image and first bullets. | The reader knows what it is, who it is for, and whether it is maintained. |
| Evaluator | 60 seconds, covering the key features, overview table and first command. | The reader can say why this and not the alternative, and what trying it costs. |
| Operator | 10 minutes, covering the walkthrough, reference tables and FAQ. | The reader reaches the first real result without opening the code and knows where to go when it fails. |

The reviewer reads the draft three times, once per reader, stopping at the clock, and records where each reader is lost.

### Proof test

Every claim in the hero block, key features and overview table is backed by a real output block, a number counted now, a screenshot, a linked file in the repository, or a linked example the tool produced. An unproven claim is rewritten as a fact the repository backs, or cut.

### Resource test

Every document, script, template, dataset, example and external link in the inventory that a reader might need is either linked from the section where the reader needs it or deliberately left out with a reason in the notes. "See the folder" is not a link.

### Cut test

For each section the reviewer asks what the reader would fail to do if it were deleted. If the answer is nothing, the section is cut. Prose that appears in two sections is kept only where the reader acts. A table with one row of real variation becomes prose.

## Verification

Before scoring, the reviewer re-runs every command in the draft from a scratch copy, diffs every output block against what the command printed, recounts every number, resolves every relative link and anchor, and confirms that no secret value appears anywhere in the draft or the inventory.

## Scoring: acceptance criteria

A round passes when every criterion below is true and the reviewer reports zero must-fix findings. A must-fix finding is one that makes any of A1 to A11 false; every other finding is should-fix, and the writer applies it or rejects it with a reason in the owner note.

| Criterion | Statement |
|---|---|
| A1 | Zero sentence fragments appear in bullets, labels, headings, prose table cells or bold lead-ins. Code, paths and single-term table cells are exempt. |
| A2 | Zero casual openers, zero rhetorical-question headings and zero words from the `lint.py` banned list appear. |
| A3 | Zero audience narrowing appears without a justification found in the repository. |
| A4 | Every group of three or more parallel items is a list or a table. |
| A5 | Every table column and every number passes the value test; the reviewer names the reader decision each one serves. |
| A6 | Every heading, step name and diagram label passes the read-alone test. |
| A7 | Every named file, command and term is introduced before it is used. |
| A8 | `python3 lint.py README.md` prints OK, and every relative link resolves. |
| A9 | README body prose is within 400 to 900 words. |
| A10 | SKILL.md, CHALLENGER.md, README.md and the two scripts agree on every count, name and step. |
| A11 | Zero judgment tells from R10 survive in the draft, and a lone tell a careful writer might have chosen on purpose counts only where several share a passage. |

A maximum of three rounds is allowed. If the third round still fails, the reviewer lists the open criteria from A1 to A11 in the owner note and the README does not ship.

## Output

The reviewer writes `readme-challenge.md` beside the README in this form:

```
Round: 1 of 3
Takeaways: 1. … 2. … 3. …
Scanner lost at: … / Evaluator lost at: … / Operator lost at: …
Verification: commands re-run …; outputs match …; counts match …; links resolve …; secrets none.
- [cut] (must-fix, A5) <section or column> — <rule or test it fails, and the reader decision it does not serve>
- [prove] (must-fix, A8) <claim> — <evidence to add, or the factual rewording>
- [add] (should-fix) <resource> — <section to link it from>
- [move] (should-fix) <section> — <destination and reason>
- [reword] (must-fix, A1) <sentence> — <replacement>
- [restructure] (must-fix, A4) <paragraph> — <list or table to replace it>
- [keep] <section> — <takeaway it serves>
Score: A1 pass/fail … A11 pass/fail
Must-fix findings: <count>, listed above with the criterion each fails
```

Each finding line carries its severity and, for a must-fix finding, the criterion it fails. The writer applies every must-fix finding, applies or rejects each should-fix finding, then runs `lint.py`. A finding the writer rejects is listed in the owner note with the reason.
