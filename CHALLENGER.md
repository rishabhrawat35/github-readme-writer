# README Challenger

Run this after the draft, before lint. The challenger is a second pass in a fresh context that has the repo, the inventory, and this file — not the writer's reasoning. Its job is to cut, prove, and reorder; it does not add sections for completeness.

## 1. The three takeaways

Write the three things a reader must know after reading. If the writer did not state them, derive them from the repo. Then, for every section in the draft, name which takeaway it serves. A section that serves none is cut. A takeaway with no section is a gap.

## 2. Three readers, three clocks

| Reader | Time | Must be true |
|---|---|---|
| Scanner | 10 s — title, tagline, image, first bullets | Knows what it is, who it is for, and whether it is alive (status/date). |
| Evaluator | 60 s — Why, overview table, first command | Can say why this instead of the alternative, and what it costs to try. |
| Operator | 10 min — Get started, reference, FAQ | Reaches the first real result without opening the code, and knows where to go when it fails. |

Read the draft three times, once per reader, stopping at the clock. Record where each reader gets lost or leaves.

## 3. Proof test

Every claim in Hero, Why and Overview needs one of: a real output block, a number counted now, a screenshot, a linked file in the repo, or a linked example produced by the tool. Unproven claim → rewrite as a fact the repo backs, or cut.

## 4. Resources map

From the inventory: every document, script, template, dataset, example, or external link a reader might need. Each is either linked from the section where the reader needs it, or deliberately left out (say why in the note). No "see the folder".

## 5. Cut test

For each section, ask: if this were deleted, what would the reader fail to do? If the answer is "nothing", delete it. Prose repeated in two sections → keep the one closer to where the reader acts. A table with one row of real variation → prose.

## 6. Form

- First screen (before the first scroll, ~25 lines): name, tagline, one image or output block, one command. Nothing else.
- Tables only where the reader compares; prose where the reader decides.
- One worked example beats three feature lists.
- Every command has a realistic argument and, where it was run, its output.
- Headings are questions the reader has, not names of things.

## Output

`readme-challenge.md` beside the README:

```
Takeaways: 1… 2… 3…
Scanner lost at: … / Evaluator lost at: … / Operator lost at: …
- [cut] <section> — served no takeaway
- [prove] <claim> — <what evidence to add or how to reword>
- [add] <resource> — link from <section>
- [move] <section> — <where and why>
- [keep] <section> — <takeaway it serves>
```

The writer applies every `cut`, `prove`, `add`, `move`, then runs `lint.py`. A finding the writer rejects is listed in the owner note with the reason.
